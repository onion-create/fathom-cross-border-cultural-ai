#!/usr/bin/env python3
"""
Fathom 数据再生管道
===================
1. 从 COUNTRY_DATA 英文 profile 生成 40 国地道中文简介
2. 审计 CULTURAL_DB 规则是否有混入他国内容
3. 输出干净 JSON 文件，安全导入

用法:
  export DEEPSEEK_API_KEY=sk-xxx
  python3 tools/regenerate_data.py

输出:
  output/profiles_zh.json    — 40国中文简介，json.dumps 安全编码
  output/rules_audit.json    — CULTURAL_DB 审计报告
"""

import re, json, os, sys, time

DEEPSEEK_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
if not DEEPSEEK_KEY:
    print("请设置 DEEPSEEK_API_KEY 环境变量")
    sys.exit(1)

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# 1. 提取 COUNTRY_DATA 英文 profile
# ============================================================
def extract_profiles(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    start = html.find('const COUNTRY_DATA = {\n')
    end = html.find('\n};\n', start)
    block = html[start:end]

    profiles = {}
    for m in re.finditer(r'"([a-z]{2})":\s*\{', block):
        code = m.group(1)
        # 找下一个 entry 的起始
        next_m = None
        for m2 in re.finditer(r'"([a-z]{2})":\s*\{', block):
            if m2.start() > m.start():
                next_m = m2
                break
        seg = block[m.start():(next_m.start() if next_m else len(block))]

        en_name = ''
        zh_name = ''
        for nm in re.finditer(r'^\s{4}(en|zh):\s*"([^"]*)"', seg, re.MULTILINE):
            if nm.group(1) == 'en' and not en_name:
                en_name = nm.group(2)
            elif nm.group(1) == 'zh' and not zh_name:
                zh_name = nm.group(2)

        pf = re.search(r'profile:\{en:"(.*?)"', seg)
        if pf:
            profiles[code] = {
                'en_name': en_name,
                'zh_name': zh_name,
                'en_profile': pf.group(1)
            }
    return profiles

# ============================================================
# 2. DeepSeek API 调用 — 生成地道中文简介
# ============================================================
def call_deepseek(system_prompt, user_prompt, max_tokens=1024):
    resp = __import__('urllib.request').request.urlopen(
        __import__('urllib.request').request.Request(
            'https://api.deepseek.com/v1/chat/completions',
            data=json.dumps({
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.7,
                'max_tokens': max_tokens
            }).encode(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {DEEPSEEK_KEY}'
            }
        ),
        timeout=120
    )
    data = json.loads(resp.read())
    return data['choices'][0]['message']['content']

def generate_zh_profile(en_name, en_profile, zh_name):
    """调用 DeepSeek 为单个国家生成地道中文简介"""
    system = """你是一位顶尖的中文商业文化写作者。你的任务是将英文的国家商业文化简介改写为地道、流畅、有信息密度的中文。

要求：
1. 用中文母语者的语感写作，不是翻译腔
2. 保持原文所有关键信息点，但用中文读者习惯的表达方式重组
3. 每段 2-3 句，用 \\n\\n 分隔段落
4. 长度控制在 200-400 字，信息密度高但不堆砌
5. 使用地道的中国文化术语来类比解释（例如用"面子"对应 face，用"根回"对应 nemawashi）
6. 禁止出现"N/A"、"不适用"、"建议咨询当地专家"等空洞内容
7. 输出纯文本，不要 markdown 标记"""
    
    user = f"""请为 {zh_name}（{en_name}）撰写一段中文商业文化简介。参考英文内容：

{en_profile}

输出要求：纯中文文本，200-400字，用 \\n\\n 分段，地道表达。"""
    
    for attempt in range(3):
        try:
            result = call_deepseek(system, user, max_tokens=800)
            if len(result) > 50:
                return result.strip()
        except Exception as e:
            print(f"  [{en_name}] 第{attempt+1}次尝试失败: {e}")
            time.sleep(3)
    return ''

# ============================================================
# 3. CULTURAL_DB 规则审计
# ============================================================
def audit_rules(worker_path):
    with open(worker_path) as f:
        worker = f.read()

    cu_start = worker.find('const CULTURAL_DB = {')
    cu_end = worker.find('\nconst GLOBE_DB', cu_start)
    cu_block = worker[cu_start:cu_end]

    # 解析每个国家的规则
    entries = list(re.finditer(r'"([a-z]{2})":\{', cu_block))
    issues = []

    # 已知的国家文化关键词（用于交叉验证）
    country_keywords = {
        'cn': ['中国', '中文', '关系', 'guanxi', '宴请', '白酒', '春节', '面子', '儒家', '红包'],
        'jp': ['日本', '名片', 'meishi', '鞠躬', '根回', 'nemawashi', '敬语', 'keigo', '禀议', 'ringi'],
        'kr': ['韩国', '眼치', 'nunchi', '会食', 'hoesik', '财阀', 'chaebol', '鞠躬'],
        'de': ['德国', '守时', 'Pünktlichkeit', '工程', 'Ingenieur', '严谨', '合同'],
        'ru': ['俄罗斯', '炼油', 'vodka', '伏特加', '寡头', 'доверие'],
        'sg': ['新加坡', '多元', 'GLC', 'CPIB', '廉政', '法治'],
        'in': ['印度', '孟买', '种姓', 'caste', '素食', '素食主义', '排灯节', 'Diwali', '宝莱坞'],
        'br': ['巴西', 'jeitinho', '桑巴', 'samba', '关系', '家人'],
        'ae': ['阿联酋', '迪拜', 'wasta', '伊斯兰', '清真', '斋月', 'gahwa', '阿拉伯咖啡'],
    }

    for m in entries:
        code = m.group(1)
        seg_end = None
        for m2 in entries:
            if m2.start() > m.start():
                seg_end = m2.start()
                break
        seg = cu_block[m.start():(seg_end or len(cu_block))]

        # 提取该国名字
        en_name = ''
        nm = re.search(r'en:"([^"]+)"', seg)
        if nm:
            en_name = nm.group(1)

        # 检查 rules 数组
        rules_start = seg.find('rules:[')
        if rules_start < 0:
            continue
        rules_seg = seg[rules_start:]

        # 粗略提取 cat 和 rule.en 进行关键词匹配
        for rm in re.finditer(r'cat:"([^"]+)"', rules_seg):
            cat = rm.group(1)
            # 找对应的 rule.en
            rule_en_start = rm.end()
            rule_en_m = re.search(r'en:"([^"]{0,100})"', rules_seg[rule_en_start:rule_en_start+500])
            rule_en = rule_en_m.group(1) if rule_en_m else ''

            # 交叉验证：如果规则内容包含其他国家的关键词，标记
            rule_lower = rule_en.lower()
            for other_code, kws in country_keywords.items():
                if other_code == code:
                    continue
                matched = [kw for kw in kws if kw.lower() in rule_lower]
                if len(matched) >= 2:  # 至少匹配2个他国关键词才报警
                    issues.append({
                        'country': code,
                        'country_name': en_name,
                        'category': cat,
                        'rule_snippet': rule_en[:80],
                        'matched_other_country': other_code,
                        'matched_keywords': matched
                    })

    return issues

# ============================================================
# 主流程
# ============================================================
def main():
    os.makedirs(f'{PROJECT}/output', exist_ok=True)

    html_path = f'{PROJECT}/src/index.html'
    worker_path = f'{PROJECT}/src/worker.js'

    # --- Part A: zh profiles ---
    print("=" * 60)
    print("Part A: 生成中文商业文化简介")
    print("=" * 60)
    profiles = extract_profiles(html_path)
    print(f"提取 {len(profiles)} 个国家英文 profile")

    zh_profiles = {}
    for code, info in profiles.items():
        en_name = info['en_name']
        zh_name = info['zh_name']
        en_prof = info['en_profile']
        print(f"\n[{code}] {zh_name}（{en_name}）...")
        if not en_prof:
            print("  跳过：无英文 profile")
            continue
        zh = generate_zh_profile(en_name, en_prof, zh_name)
        if zh:
            zh_profiles[code] = zh
            print(f"  生成 {len(zh)} 字")
        else:
            print("  生成失败，保留空白")
        time.sleep(2)  # 限流

    with open(f'{PROJECT}/output/profiles_zh.json', 'w', encoding='utf-8') as f:
        json.dump(zh_profiles, f, ensure_ascii=False, indent=2)
    print(f"\n中文简介已保存到 output/profiles_zh.json ({len(zh_profiles)} 国)")

    # --- Part B: rules audit ---
    print("\n" + "=" * 60)
    print("Part B: CULTURAL_DB 规则审计")
    print("=" * 60)
    issues = audit_rules(worker_path)
    print(f"发现 {len(issues)} 条可疑规则（匹配他国文化关键词 ≥2 个）")
    for iss in issues:
        print(f"  [{iss['country']}] {iss['category']}: 匹配到 {iss['matched_other_country']} 关键词 {iss['matched_keywords']}")

    with open(f'{PROJECT}/output/rules_audit.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print(f"\n审计报告已保存到 output/rules_audit.json")

    # --- Part C: 缺失国家补充 ---
    print("\n" + "=" * 60)
    print("Part C: CULTURAL_DB 国家覆盖")
    print("=" * 60)
    with open(worker_path) as f:
        worker = f.read()
    cu_start = worker.find('const CULTURAL_DB = {')
    cu_end = worker.find('\nconst GLOBE_DB', cu_start)
    cu_block = worker[cu_start:cu_end]
    cu_codes = set(re.findall(r'"([a-z]{2})":\{', cu_block))
    cd_codes = set(profiles.keys())
    missing = cd_codes - cu_codes
    print(f"CULTURAL_DB 现有: {len(cu_codes)} 国")
    print(f"COUNTRY_DATA 现有: {len(cd_codes)} 国")
    print(f"缺失: {sorted(missing)}")

    print("\n✅ 管道运行完成。使用 output/profiles_zh.json 中的内容替换 index.html COUNTRY_DATA 的 profile.zh 字段。")

if __name__ == '__main__':
    main()
