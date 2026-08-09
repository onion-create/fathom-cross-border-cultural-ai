<p align="center">
  <img src="src/logo.jpg" width="96" alt="Fathom Logo">
</p>

<h1 align="center">Fathom · 知彼</h1>

<p align="center"><i>Your meeting is tomorrow. Your cultural blind spots don't have to be.</i></p>

<p align="center">
  <a href="#demo"><strong>Live Demo</strong></a> &nbsp;·&nbsp;
  <a href="#what-it-does"><strong>Features</strong></a> &nbsp;·&nbsp;
  <a href="#quick-deploy"><strong>Deploy</strong></a> &nbsp;·&nbsp;
  <a href="#countries"><strong>Coverage</strong></a> &nbsp;·&nbsp;
  <a href="#license"><strong>License</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-5.8.0-2bb673?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-BSL%201.1-blue?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/countries-40-8b5cf6?style=flat-square" alt="Countries">
  <img src="https://img.shields.io/badge/rules-594-eab308?style=flat-square" alt="Rules">
</p>

<br>

---

<br>

## What is Fathom?

Cross-border business fails in predictable, expensive ways. A founder brings the wrong gift. A buyer demands a clause that makes someone lose face. A CEO skips the small talk because "we're efficient."

**Fathom is your cultural briefing, generated on demand.** Type your scenario — *"I'm meeting a 50-year-old Japanese department head tomorrow"* — and get:

- 🇯🇵 What to say at the door
- 📋 How the meeting should flow
- ⚠️ What to never do
- ✅ What to always do
- 🛡️ What risks you're walking into
- 📖 A phased strategy
- 🗣️ Dialogue to practice before you go

> *Not general culture tips. Scene-specific guidance that reads like it was written by someone who's been in that room.*

<p align="center">
  <a href="#"><strong>Try the demo →</strong></a>
</p>

<br>

## What it does

| | |
|---|---|
| **Scene Analysis** | Natural language → structured playbook with country detection, cultural profiling, taboos, dos, strategy, and deliverable templates |
| **Country Comparison** | 12-dimension radar with clash advice — see where two cultures collide and how to bridge the gap |
| **Dialogue Simulation** | Practice the conversation in a scored environment — cultural fit, tone, face preservation |
| **PDF Export** | Save any analysis as a clean, printable document |
| **Live Web Intel** | Real-time industry & regulatory context via Tavily |
| **EN / 中文** | Full bilingual throughout. Auto dark mode. |

<br>

## Countries

| Verified | Research-Backed | AI-Generated |
|---|---|---|
| 🇨🇳 🇯🇵 🇰🇷 🇩🇪 🇧🇷 🇮🇳 🇫🇷 🇸🇦 🇦🇪 🇸🇬 🇹🇷 🇻🇳 🇲🇽 🇳🇬 🇮🇹 🇺🇸 🇬🇧 🇦🇺 🇨🇦 🇪🇸 + more | 🇷🇺 🇹🇭 🇮🇩 🇲🇾 🇵🇭 🇿🇦 🇮🇷 🇵🇱 🇦🇷 🇨🇴 🇨🇱 🇵🇪 🇲🇦 🇰🇪 🇧🇩 🇪🇬 | Any country not listed |

<br>

## How it's built

- **Frontend** — Vanilla JS/CSS SPA. No frameworks, instant load.
- **Backend** — Serverless Node.js on Tencent SCF. Parallel AI with structured fallback.
- **Pipeline** — DeepSeek v4 Flash ×2 (race) → progressive rendering → supplement endpoint → graceful degradation.

Built solo, AI-assisted. ~200 hours over 6 weeks. 22 cross-cultural test scenarios validated.

<br>

## Quick Deploy

```bash
open dist/index.html
```

Static hosts: upload `dist/` to GitHub Pages, Vercel, Netlify. Update `dist/config.js` → `workerUrl`.

<br>

## Author

**Yuan Ming (袁铭)** — Beijing, 2026

Independent builder. Full-stack from architecture to prompt engineering. Fathom is my answer to the question: *what should exist before every cross-border meeting?*

<br>

## License

[Business Source License 1.1](./LICENSE) — free for non-commercial use, requires commercial license for production. Converts to MIT in 2030.

Commercial inquiries: Yuan Ming (袁铭)
