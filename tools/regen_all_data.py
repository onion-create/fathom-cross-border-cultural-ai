#!/usr/bin/env python3
"""
Fathom 全量数据再生成脚本
功能:
  1. 从英文 profile 生成 40 国中文简介（母语级别）
  2. 为缺失 31 国生成 CULTURAL_DB 规则（6 类，中英双语）
  3. 输出到 output/ 目录
  4. 可选: 注入到源文件

用法:
  export DEEPSEEK_API_KEY=sk-xxx
  python3 tools/regen_all_data.py          # 只生成数据
  python3 tools/regen_all_data.py --inject  # 生成并注入源文件
"""

import json, re, os, sys, time, urllib.request, urllib.error

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not API_KEY:
    print("❌ 请设置 DEEPSEEK_API_KEY 环境变量")
    print("   export DEEPSEEK_API_KEY=sk-xxx")
    sys.exit(1)

BASE_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"
BATCH_DELAY = 2  # seconds between successful API calls
MAX_RETRIES = 3  # max retries per API call
BASE_BACKOFF = 4  # base seconds for exponential backoff

def call_ds(system_prompt, user_prompt, max_tokens=6000, temp=0.5):
    """调用 DeepSeek，带指数退避和重试，返回解析后的 JSON"""
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temp,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"}
    }, ensure_ascii=False).encode('utf-8')

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        if attempt > 0:
            delay = BASE_BACKOFF * (2 ** (attempt - 1))
            print(f"  ⚠️ 重试 {attempt}/{MAX_RETRIES}，等待 {delay}s...")
            time.sleep(delay)

        req = urllib.request.Request(BASE_URL, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        })

        sys.stdout.write(f"  → API call ({len(user_prompt)} chars)...")
        sys.stdout.flush()
        t0 = time.time()

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = json.loads(resp.read())
            content = raw["choices"][0]["message"]["content"]
            elapsed = int((time.time() - t0) * 1000)
            print(f" {elapsed}ms, {len(content)} chars")

            # Parse JSON
            s = content.strip()
            s = s.replace("```json", "").replace("```", "").strip()
            i = s.find("{")
            if i >= 0:
                s = s[i:]
                # Find matching closing brace
                depth = 0
                for j, c in enumerate(s):
                    if c == '{': depth += 1
                    elif c == '}': depth -= 1
                    if depth == 0:
                        s = s[:j+1]
                        break
            # Remove trailing commas
            s = re.sub(r',\s*([}\]])', r'\1', s)
            return json.loads(s)

        except urllib.error.HTTPError as e:
            last_error = e
            err_body = ""
            try: err_body = e.read().decode()[:300]
            except: pass
            status = e.code
            print(f" HTTP {status}")

            # Non-retryable errors
            if status in (400, 401, 402, 403, 404):
                print(f"  ❌ 不可重试的错误 (HTTP {status}): {err_body}")
                return {}

        except json.JSONDecodeError as e:
            last_error = e
            print(f" JSON解析错误: {e}")

        except Exception as e:
            last_error = e
            print(f" 网络/其他错误: {e}")

    print(f"  ❌ 已达最大重试次数 ({MAX_RETRIES})，放弃")
    return {}

def extract_country_data():
    """从 index.html 提取 COUNTRY_DATA（40 国的英文数据）"""
    with open('src/index.html', encoding='utf-8') as f:
        html = f.read()

    cd_start = html.find('const COUNTRY_DATA = {\n')
    cd_end = html.find('\n};\n', cd_start) + 4
    cd_block = html[cd_start:cd_end]

    # 逐国解析
    entries = list(re.finditer(r'\n  "([a-z]{2})": \{\n\s+flag: "([^"]*)",\n\s+en: "([^"]*)",\n\s+zh: "([^"]*)",\n\s+profile:\{en:"(.*?)",zh:"', cd_block, re.DOTALL))

    countries = []
    for m in entries:
        code = m.group(1)
        flag = m.group(2)
        en_name = m.group(3)
        zh_name = m.group(4)
        en_profile = m.group(5)
        countries.append({
            "code": code, "flag": flag, "en": en_name, "zh": zh_name,
            "en_profile": en_profile
        })

    print(f"✓ 提取 {len(countries)} 国数据")
    return countries

def extract_existing_cultural_db():
    """从 worker.js 提取已有 CULTURAL_DB 国家列表"""
    with open('src/worker.js', encoding='utf-8') as f:
        worker = f.read()

    cu_start = worker.find('const CULTURAL_DB = {')
    cu_end = worker.find('\nconst GLOBE_DB', cu_start)
    cu = worker[cu_start:cu_end]

    entries = list(re.finditer(r'"([a-z]{2})":\{\n\s+flag:"', cu))
    return set(m.group(1) for m in entries)

# ============================================================================
# Phase 1: 生成 40 国中文简介
# ============================================================================

def generate_zh_profiles(countries):
    """批量生成中文简介，每次 5 国"""
    output = {}
    batch_size = 5
    batches = [countries[i:i+batch_size] for i in range(0, len(countries), batch_size)]

    system = """You are a professional Chinese business writer.
Convert the following English country profiles into native-level, fluent Chinese.
Rules:
- Sound like a Chinese business consultant's briefing, NOT a literal translation.
- Use natural Chinese idioms and sentence rhythm. Avoid Western sentence structures.
- Keep all key information but make it read smoothly.
- Output ONLY valid JSON matching this structure:
{"results": [{"code": "xx", "zh_profile": "流畅的中文简介..."}, ...]}"""

    for bi, batch in enumerate(batches):
        names = [f'{c["flag"]} {c["en"]}/{c["zh"]}' for c in batch]
        print(f"\n📝 中文简介 batch {bi+1}/{len(batches)}: {', '.join(names)}")

        user = "English profiles:\n\n"
        for c in batch:
            user += f"CODE: {c['code']}\nCOUNTRY: {c['en']} ({c['zh']})\nPROFILE: {c['en_profile']}\n\n"

        result = call_ds(system, user, max_tokens=4000, temp=0.5)
        items = result.get("results", [])
        for item in items:
            code = item.get("code", "")
            zh_prof = item.get("zh_profile", "")
            if code and zh_prof:
                output[code] = zh_prof
                print(f"  ✓ {code}: {zh_prof[:50]}...")

        time.sleep(BATCH_DELAY)

    return output

# ============================================================================
# Phase 2: 生成 31 国 CULTURAL_DB 规则
# ============================================================================

def generate_cultural_rules(missing_countries):
    """批量生成文化规则，每次 3 国"""
    output = {}
    batch_size = 3
    batches = [missing_countries[i:i+batch_size] for i in range(0, len(missing_countries), batch_size)]

    system = """You are a world-class cross-cultural business expert.
Generate cultural rules for each country. Rules must be PRACTICAL, ACCURATE, and REFLECT REAL BUSINESS PRACTICE — not generic stereotypes.

Each country needs rules in these categories:
1. greeting: how to greet in business meetings (handshake, bow, titles, formal/informal)
2. meeting: meeting structure, pacing, expectations, preparation norms
3. hierarchy: power distance, decision-making, age/rank dynamics
4. negotiation: negotiation style, pricing, concessions, deal rhythm
5. communication: directness, context level, taboos in speech
6. taboo: absolute no-gos — topics, behaviors, gestures to avoid

IMPORTANT RULES:
- Cite real cultural traits, not clichés. Use specific cultural terminology where authentic.
- Chinese (zh) MUST be native-level business Chinese. Never literal translation.
- English (en) MUST be idiomatic. Sound like a colleague giving advice.
- Each rule: 1-2 sentences, actionable, specific.
- Tags: 2-3 relevant lowercase keywords.

Output ONLY valid JSON:
{"results": [{"code": "xx", "rules": [
  {"cat": "greeting", "rule": {"en": "advice in English", "zh": "中文建议"}, "tags": ["tag1", "tag2"], "conf": "high", "cite": "Hofstede (2001), Culture's Consequences, 2nd ed.", "src": "literature"},
  ...(6 total)
]}, ...]}"""

    for bi, batch in enumerate(batches):
        names = [f'{c["flag"]} {c["en"]}' for c in batch]
        print(f"\n📚 CULTURAL_DB batch {bi+1}/{len(batches)}: {', '.join(names)}")

        user = "Generate cultural rules for:\n\n"
        for c in batch:
            user += f"CODE: {c['code']}\nCOUNTRY: {c['en']} ({c['zh']})\nPROFILE: {c.get('en_profile', '')[:300]}\n"
            if c.get('hofstede'):
                user += f"Hofstede: {c['hofstede']}\n"
            user += "\n"

        result = call_ds(system, user, max_tokens=6000, temp=0.5)
        items = result.get("results", [])
        for item in items:
            code = item.get("code", "")
            rules = item.get("rules", [])
            if code and len(rules) >= 4:
                output[code] = rules
                print(f"  ✓ {code}: {len(rules)} rules ({', '.join(r.get('cat','?') for r in rules[:3])}...)")

        time.sleep(BATCH_DELAY)

    return output

# ============================================================================
# Phase 3: 注入数据
# ============================================================================

def inject_profiles(countries, zh_profiles):
    """将中文简介注入 index.html 的 COUNTRY_DATA"""
    with open('src/index.html', encoding='utf-8') as f:
        html = f.read()

    cd_start = html.find('const COUNTRY_DATA = {\n')
    cd_end = html.find('\n};\n', cd_start) + 4
    before = html[:cd_start]
    after = html[cd_end:]
    block = html[cd_start:cd_end]

    for c in countries:
        code = c['code']
        zh_new = zh_profiles.get(code, '')
        if not zh_new:
            continue
        # 安全编码
        zh_safe = json.dumps(zh_new, ensure_ascii=False)[1:-1]  # strip outer quotes

        # 找到 profile:{en:"...",zh:"OLD"} 并替换 zh 值
        pattern = rf'(profile:\{{en:"{re.escape(c["en_profile"])}",zh:)"[^"]*"(\}})'
        block = re.sub(pattern, rf'\1"{zh_safe}"\2', block, count=1)

    new_html = before + block + after
    with open('src/index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"\n✓ 已注入 {len(zh_profiles)} 国中文简介到 index.html")

def inject_cultural_db(new_rules, existing_countries):
    """将新规则注入 worker.js 的 CULTURAL_DB"""
    with open('src/worker.js', encoding='utf-8') as f:
        worker = f.read()

    # 找到 CULTURAL_DB 结束位置（const GLOBE_DB 之前）
    db_end = worker.find('\nconst GLOBE_DB')
    before = worker[:db_end]

    # 生成新条目
    new_entries = []
    for entry in new_rules:
        code = entry['code']
        country = entry['country']
        rules = entry['rules']

        # 序列化规则为 JS 格式
        rule_lines = []
        for r in rules:
            tags_str = json.dumps(r['tags'], ensure_ascii=False)
            rule_en = json.dumps(r['rule']['en'], ensure_ascii=False)
            rule_zh = json.dumps(r['rule']['zh'], ensure_ascii=False)
            cat = r['cat']
            conf = r.get('conf', 'medium')
            cite = r.get('cite', 'Hofstede (2001), Culture\'s Consequences, 2nd ed.')
            src = r.get('src', 'ai_generated')
            rule_lines.append(
                f'      {{cat:{json.dumps(cat)},rule:{{en:{rule_en},zh:{rule_zh}}},'
                f'tags:{tags_str},conf:{json.dumps(conf)},cite:{json.dumps(cite)},src:{json.dumps(src)}}}'
            )

        entry_str = (
            f'\n  {json.dumps(code)}:{{\n'
            f'    flag:{json.dumps(country["flag"])},'
            f' en:{json.dumps(country["en"])},'
            f' zh:{json.dumps(country["zh"])},'
            f' region:{json.dumps(country.get("region", "other"))},\n'
            f'    profile:{json.dumps(country.get("en_profile", ""))},\n'
            f'    rules:[\n'
            + ',\n'.join(rule_lines) +
            f'\n    ]\n'
            f'  }},'
        )
        new_entries.append(entry_str)

    # 在现有 DB 结束后、GLOBE_DB 前插入
    after = worker[db_end:]
    new_worker = before + '\n'.join(new_entries) + '\n' + after

    with open('src/worker.js', 'w', encoding='utf-8') as f:
        f.write(new_worker)
    print(f"✓ 已注入 {len(new_rules)} 国 CULTURAL_DB 规则到 worker.js")

# ============================================================================
# Main
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--inject', action='store_true', help='注入数据到源文件')
    parser.add_argument('--skip-profiles', action='store_true')
    parser.add_argument('--skip-rules', action='store_true')
    args = parser.parse_args()

    print("=" * 60)
    print("  Fathom 全量数据再生成")
    print("=" * 60)

    # 提取现有数据
    countries = extract_country_data()
    existing_cu = extract_existing_cultural_db()
    missing_cu = [c for c in countries if c['code'] not in existing_cu]
    print(f"CULTURAL_DB 已有: {len(existing_cu)} 国, 缺失: {len(missing_cu)} 国")
    if len(missing_cu) < 30:
        print("  (已有较完整覆盖，跳过规则生成)")

    # Phase 1: 中文简介
    zh_profiles = {}
    if not args.skip_profiles:
        zh_profiles = generate_zh_profiles(countries)
        with open('output/profiles_zh.json', 'w', encoding='utf-8') as f:
            json.dump(zh_profiles, f, ensure_ascii=False, indent=2)
        print(f"\n✓ profiles_zh.json: {len(zh_profiles)} 国")

    # Phase 2: CULTURAL_DB 规则
    new_rules_all = []
    if not args.skip_rules and len(missing_cu) > 5:
        new_rules_raw = generate_cultural_rules(missing_cu)
        # Format for injection
        for c in missing_cu:
            rules = new_rules_raw.get(c['code'])
            if rules and len(rules) >= 4:
                new_rules_all.append({
                    "code": c['code'],
                    "country": c,
                    "rules": rules
                })
        with open('output/cultural_db_new.json', 'w', encoding='utf-8') as f:
            json.dump(new_rules_all, f, ensure_ascii=False, indent=2)
        print(f"\n✓ cultural_db_new.json: {len(new_rules_all)} 国")

    # Phase 3: 注入
    if args.inject:
        print("\n" + "=" * 60)
        print("  注入数据到源文件")
        print("=" * 60)
        if zh_profiles:
            inject_profiles(countries, zh_profiles)
        if new_rules_all:
            inject_cultural_db(new_rules_all, countries)

    print("\n✅ 完成")

if __name__ == '__main__':
    main()
