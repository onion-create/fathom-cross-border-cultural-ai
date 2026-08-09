<p align="center">
  <img src="logo.jpg" alt="Fathom" width="96" height="96" />
</p>

<h1 align="center">Fathom · 知彼</h1>

<p align="center">
  <strong>Cross-border business cultural intelligence — generated on demand.</strong><br />
  <em>40 countries · 594 rules · Scene-specific playbook · Dialogue simulation · EN/中文</em>
</p>

<p align="center">
  <a href="https://onion-create.github.io/fathom/"><strong>🌐 Live Demo</strong></a> &nbsp;&nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-BSL%201.1-blue.svg" alt="License" /></a>
  <img src="https://img.shields.io/badge/countries-40-8b5cf6.svg" alt="Countries" />
  <img src="https://img.shields.io/badge/rules-594-eab308.svg" alt="Rules" />
  <img src="https://img.shields.io/badge/scenarios-22-brightgreen.svg" alt="Tested" />
</p>

---

## Why This Exists

Cross-border business fails in predictable, expensive ways.

A Chinese founder brings the wrong gift to a Japanese department head and loses the deal before it starts. A European buyer demands a contract clause that makes a Saudi investor lose face in front of his board. A tech CEO calls a Korean VP by his first name because "we're modern" — and wonders why the follow-up email goes unanswered.

The problem isn't ignorance. It's that **nobody tells you what matters until you've already made the mistake.**

Fathom starts from a different premise: **a cultural blind spot is a product problem, not a user failure.** You type your scenario — *"I'm meeting a 50-year-old Japanese department head tomorrow"* — and Fathom returns a complete, scene-specific cultural playbook. Not generic country notes. Not Wikipedia summaries. A briefing that reads like it was written by someone who's been in that room.

**Built solo, end-to-end, without a team.** Designed from first principles, built through AI-assisted development (WorkBuddy, Claude Code, DeepSeek API), deployed to Tencent Cloud SCF + GitHub Pages. From zero to production — one person, zero frameworks, 594 verified cultural rules organized across 40 countries.

---

## What Makes It Different

### 🎯 Scene-Specific, Not Generic
Every culture has 50 ways to say "no." But the way a Japanese department head says it over green tea is different from how a Brazilian buyer says it over coffee. Fathom's analysis is anchored to your actual scenario — country, industry, interaction type, seniority — and generates a playbook tailored to that moment.

### 🌍 Structured Cultural Database, Not Hallucination
594 verifiable cultural rules across 40 countries — greetings, meetings, hierarchy, negotiation, communication, taboos, gifts, and dining. Each rule tagged with confidence level and academic source. The AI augments this foundation; it doesn't hallucinate from scratch.

### 🗣️ Practice Before You Go
The simulation engine lets you rehearse the conversation. Type what you'd say — Fathom scores you on cultural fit, communication effectiveness, face preservation, and language quality. Then gives you a better version. Not a chatbot. A coach.

### 📊 Compare Any Two Cultures
Select two countries and Fathom maps the collision points across 12 cultural dimensions — Hofstede radar charts, gap analysis, and specific behavioral recommendations for bridging each gap. When cultures clash, Fathom tells you exactly where and what to do about it.

---

## Features

| Category | What You Get |
|----------|--------------|
| 🎯 **Scene Analysis** | Natural language input → complete cultural playbook. Country detection, opening greetings, meeting agenda, cultural profile, industry context, scene confirmation, critical taboos, dos, risk matrix, strategic guidance with phased playbook, dialogue practice, and deliverable template (email, agenda, or script). |
| 📊 **Country Comparison** | 40 countries × 12 cultural dimensions. Hofstede radar charts. Gap analysis with clash detection. Cross-cultural action advice mapped to specific behaviors. Expandable dimension cards. Academic data tables. |
| 🗣️ **Dialogue Simulation** | Scored practice environment. 4-dimension feedback: cultural adaptation, communication effectiveness, face preservation, language quality. Picks up idioms, tone, and power-distance signals. |
| 🌐 **Live Intelligence** | Real-time web search via Tavily API for industry-specific context, sanctions compliance, and regulatory awareness. |
| 🌐 **Bilingual** | Full EN / 中文 throughout. Country cultural profiles available in both languages. Example chips and UI switch instantly. |
| 📱 **Progressive Rendering** | Content appears as it's ready — never a blank screen. Country-specific loading messages with quips. Skeleton placeholders during AI generation. |
| 📄 **Export** | Save any analysis as a clean, printable PDF. Page-break-controlled output. Strips UI chrome automatically. |
| 🌓 **Dark Mode** | Auto (system preference) or manual toggle. Persisted in localStorage. |
| ⚡ **Performance** | Single-file HTML (~997KB). Zero framework dependencies. Serverless backend on Tencent Cloud SCF. Parallel AI calls with structured fallback. |

---

## The AI-Assisted Development Story

*This project is a case study in AI-native product development.*

Fathom was conceived, designed, and built by one person — **袁铭 (Yuan Ming)** — with a vision for what should exist before every cross-border business meeting. The development stack: **WorkBuddy + Claude Code** as AI engineering partners, **DeepSeek v4 Flash** for scene analysis, **Tavily API** for real-time web intelligence, and **Tencent Cloud SCF + GitHub Pages** for zero-infrastructure deployment.

The methodology: test-driven cultural intelligence. Every feature was validated against 22 real-world cross-border business scenarios — from a Dutch dairy equipment supplier in Hokkaido to an EN590 diesel dispute in Singapore. The cultural database was built through structured research across Hofstede, GLOBE, and Trompenaars academic frameworks, then augmented with AI-generated insights and verified against domain expertise.

The result: a production-grade cultural intelligence tool with 40 countries, 594 rules, multi-agent AI analysis with parallel fallback, progressive rendering, and a design system tuned for information density — built by a solo creator in weeks.

**If you're evaluating this project as a portfolio piece or hiring signal:** it demonstrates product vision, cross-cultural domain expertise, full-stack engineering capability (frontend, serverless backend, prompt engineering), and the ability to ship a complete product end-to-end — the exact skill set that AI-augmented product teams need in 2026.

---

## Project Structure

```
fathom/
├── index.html              # Production build — single-file SPA (~997KB, self-contained)
├── config.js               # Frontend config — worker URL + feature flags
├── logo.jpg                # Brand logo
├── dist/                   # Deployable build output
│   ├── index.html
│   └── config.js
├── src/                    # Source code
│   ├── index.html          # Application (JS + CSS inline)
│   ├── worker.js           # Serverless backend worker
│   ├── config.js           # Local config
│   ├── js/data.js          # Cultural database
│   ├── css/main.css        # Print-optimized styles
│   ├── logo.jpg            # Brand logo
│   └── manifest.json       # PWA manifest
├── tools/                  # Build & data regeneration
│   ├── build.py            # Asset builder
│   └── regen_all_data.py   # Data regeneration
├── README.md
├── LICENSE                 # BSL 1.1 (auto-converts to MIT in 2030)
└── .gitignore
```

---

## Quick Start

```bash
# Clone and open — no build step needed for production
git clone https://github.com/onion-create/fathom.git
open fathom/index.html

# Or serve locally
python3 -m http.server 8080  # → http://localhost:8080
```

### Development

```bash
# Requires Python 3
python3 tools/build.py --output dist    # Rebuild dist/index.html from src/
```

---

## Attribution

- **Hofstede Insights** — Cultural dimension data based on Geert Hofstede's 50-year cross-cultural research framework.
- **GLOBE Project** — Leadership and culture data from House, Hanges, Javidan, Dorfman & Gupta (2004).
- **Trompenaars Model** — Cultural dimensions from Trompenaars & Hampden-Turner (1993, 2012).
- **AI Analysis** — Scene analysis powered by DeepSeek API. Real-time web intelligence via Tavily.
- **Typography** — System font stack. Zero external font dependencies for instant loading.

---

## License

**Business Source License 1.1** — Free for non-commercial use. Requires a commercial license for production deployment. Automatically converts to MIT on 2030-08-08.

- ✅ View, learn from, and modify the source code
- ✅ Use for personal, academic, and non-commercial purposes
- ❌ Deploy for commercial use without a written license

See [LICENSE](LICENSE) for full terms. Commercial inquiries: 袁铭 (Yuan Ming)

---

<p align="center">
  <sub>Conceived, designed, and shipped by <strong>袁铭 (Yuan Ming)</strong><br/>
  AI-Assisted Development · © 2026 All rights reserved</sub>
</p>