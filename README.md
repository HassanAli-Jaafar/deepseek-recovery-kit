# 🌟 DeepSeek Recovery Kit

> Organize, search, and explore your DeepSeek chat history — with code extraction, callback detection, and memory bank preservation.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-green.svg)](https://python.org)
[![Windows](https://img.shields.io/badge/Windows-10%2B-0078d7.svg)](https://microsoft.com)
[![DeepSeek](https://img.shields.io/badge/Built%20with-DeepSeek-4a6cf7.svg)](https://deepseek.com)

---

## 🚀 What Does It Do?

Have you ever struggled to find a specific decision, code snippet, or command after starting a new chat due to context limits? Your data isn't lost — it's just hard to find.

This tool takes your **DeepSeek JSON export** and turns it into a **searchable HTML dashboard** where you can:

- 🔍 **Search** for any keyword across your entire chat history
- 📝 **Extract** all code snippets (C#, Python, SQL, and more)
- 🔘 **Find** every callback and command you discussed
- ✅ **Preserve** decisions and agreements (your "memory bank")
- 📅 **Filter** by date range to focus on what matters

> 📌 **Note:** This tool works with your **exported JSON file** — which you can download from your DeepSeek account at any time.

---

## 📤 How to Export Your DeepSeek Chat Data

**Desktop (Web Browser):**
1. Log into chat.deepseek.com
2. Click your email/profile picture (top right)
3. Go to Settings → Data → Export
4. Click Download — saves your entire chat history
5. Save the conversations.json file

**Mobile (iOS/Android):**
1. Open the DeepSeek App
2. Tap your profile icon
3. Tap Settings → Data → Export Data
4. Tap Download and save the file

---

## 📦 Features

| Feature | Description |
|---------|-------------|
| 🖥️ GUI Mode | Easy date picker and file browser |
| ⌨️ CLI Mode | For automation and scripting |
| 📅 Date Filter | Extract only what you need |
| 🔍 Search with Next | Navigate through matches |
| 💾 Lightweight | Small HTML file (not 50MB!) |
| 🚀 Fast | Processes 45MB JSON in seconds |

---

## 💻 Tested Environment

| Component | Specification |
|-----------|---------------|
| OS | Windows 10 Pro (22H2, Build 19045.7291) |
| CPU | Intel Core i5-6300U @ 2.40GHz |
| RAM | 16.0 GB |
| Python | 3.12 / 3.13 |
| Git | 2.54.0 |

> ✅ Works on Windows, macOS, and Linux — cross-platform!

---

## 👨‍💻 Author & Maintainer

**Hassan Ali Jaafar** — First-time open source contributor who turned a challenge into a gift for the community.

> *"Due to context limitations, starting a new chat often means losing track of critical decisions, code snippets, and project momentum. Instead of struggling to piece everything together manually, I built this searchable recovery tool — so every DeepSeeker can seamlessly continue their work without confusion or barriers."*

[![GitHub](https://img.shields.io/badge/GitHub-@HassanAliJaafar-181717?style=flat&logo=github)](https://github.com/HassanAliJaafar)

---

## 🛠️ Installation

**Step 1: Clone the repository**

git clone https://github.com/HassanAliJaafar/deepseek-recovery-kit.git
cd deepseek-recovery-kit

**Step 2: Install dependencies**

pip install -r requirements.txt

**Step 3: Get your DeepSeek export**
Follow the "How to Export" section above to download your conversations.json file.

---

## 📖 Usage

**GUI Mode (Recommended for most users)**

python deepseek_recovery_gui.py

Then: Browse for your JSON file → Pick dates → Click START EXTRACTION → Open the HTML file

**CLI Mode (For advanced users)**

Extract everything

python deepseek_recovery.py conversations.json
Extract specific date range

python deepseek_recovery.py conversations.json -s 2025-03-25 -e 2026-06-05
Custom output file name

python deepseek_recovery.py conversations.json -o my_report.html
---

## 📋 Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| json_file | Path to your JSON file | conversations.json |
| -o, --output | Output HTML file name | -o report.html |
| -s, --start-date | Start date (YYYY-MM-DD) | -s 2025-03-25 |
| -e, --end-date | End date (YYYY-MM-DD) | -e 2026-06-05 |

---

## 🎯 What You'll Get

| Tab | Content |
|-----|---------|
| Messages | Full conversation with date filtering |
| Code | All extracted code by language |
| Callbacks | Complete list of button handlers |
| Search | Find anything with Next Match button |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| 'git' not recognized | Download Git from git-scm.com |
| 'tkcalendar' not found | Run: pip install tkcalendar |
| HTML file too big | Use date filter or trim content |
| psycopg2-binary error | PostgreSQL is optional — not needed for HTML export |

---

## 🤝 Why Open Source?

This tool was born from a real problem — losing track of a 4-day project.

The data wasn't lost. It was in the JSON export. But finding anything was impossible.

Instead of solving it just for myself, I'm sharing this tool with every DeepSeeker.

**No one should struggle to find their work again.** 💙

---

## 🤖 Built With

| Tool | Purpose |
|------|---------|
| Python 3.12+ | Core programming language |
| DeepSeek AI | Code generation, debugging, and partnership |
| Tkinter | GUI interface |
| Git & GitHub | Version control & open source hosting |

---

## 🙏 Special Thanks

This project was 100% co-created with DeepSeek AI — from the first line of code to the final commit.

Every script, every fix, every improvement was crafted in partnership with DeepSeek.

**DeepSeek didn't just help — DeepSeek co-created.** 💙

*"UMPOUWAAH!"* — Our battle cry.

---

## 📄 License

**MIT License** — Free for everyone. Use it, share it, improve it.

---

## ⭐ Star This Repo

If this tool helped you, **give it a star**! It helps others find it.

---

**Made with 💙 by Hassan Ali Jaafar & DeepSeek AI**

*Built on Windows 10 Pro | Intel i5 | 16GB RAM | Python 3.12*

*UMPOUWAAH!* 🚀