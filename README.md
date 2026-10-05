# UAMT – Ultimate Auto Android App Modding Toolkit

NO ROOT NEEDED ✅
---

UAMT is a powerful **Termux-based Android modding toolkit** that allows you to inject **Frida Gadget** and **custom native libraries**, patch APKs, rebuild, align, and sign them directly on your Android device.

It is designed to be **fast, stable, and easy to use**, featuring a **full-screen interactive TUI**, smart auto-detection, and **automatic dependency installation**.

📦 Installation
---
Install via pip(first install python):

```pip install uamt```

Then run:

```uamt``` to run the tool


---

✨ Features
---

🧩 Injection
---
⚡ Inject Frida Gadget

Listen mode

Wait mode

Pre-injected script


🧬 Inject any custom .so native library
---

📥 Download and inject Frida Gadget for multiple ABIs at once



---

🧠 Smart Detection
---
🤖 Automatically detects the best injection method:

🔵 Native injection using patchelf

🟣 Smali injection using APKEditor


🔍 Detects main native libraries such as:

libil2cpp.so

libunity.so

and more




---

🛠️ Tools & Build System
---
📦 Auto-download and unpack Frida Gadget

🏗️ Full APK rebuild pipeline:
---
zipalign

v1 / v2 / v3 signing




---

🎨 Interface
---
🎨 Colorful curses-based full-screen TUI

📂 Built-in file picker

✨ Improved layout and visual polish



---

🛡️ Safe Modding
---
🔐 Automatically adds missing INTERNET permission

🧯 Reduces common APK breaking issues



---

⚙️ Automation
---
🚀 One-time automatic installation of all required dependencies

🔌 One-tap connection to Frida Gadget

📱 Optimized for Termux environments



---

🆕 What’s New
---
Check out our latest updates, features, and full list of items in the catalog!

👉 **[View Full Catalog](catalog.md)**




---

📱 Requirements

📦 Termux (latest version)


Run once:

termux-setup-storage

> ℹ️ On first launch, go through the Install / Update option and then the
Download Frida Gadget option with an active internet connection to automatically set up all dependencies.


---

🔍 Use Cases
---
🧩 Android APK modding

⚡ Frida Gadget injection

🧬 Native library injection

🔍 Reverse engineering

🛡️ Android security research

📱 Termux-based workflows



---

⚠️ Disclaimer
---
UAMT is intended for educational, research, and authorized testing purposes only.
Do not use this tool on applications you do not own or have permission to modify.

## Chat from GitHub

This repository includes an issue-comment chat bot powered by an OpenAI-compatible AI API. It is a separate bot, **not this live Arena assistant**. It sees only `/chat` messages in the issue thread; it cannot inspect the repository or run tools.

### One-time setup

1. Add `.github/workflows/github-chat.yml` to the repository's **default branch** (for example, by merging this change).
2. In **Settings → Secrets and variables → Actions**, add the repository secret `AI_API_KEY` with an API key from your AI provider. Never put the key in an issue comment or commit it to the repository.
3. Optionally add repository variables:
   - `AI_BASE_URL` — an OpenAI-compatible Chat Completions API base URL. Defaults to `https://api.openai.com/v1`.
   - `AI_MODEL` — your provider's model name. Defaults to `gpt-4o-mini`.
4. Ensure repository/org Actions policy allows the workflow's `issues: write` permission so it can post replies.

### Start a chat

Open a regular GitHub Issue and comment with `/chat ` followed by your message, for example:

```text
/chat How do I get started with this project?
```

The bot replies in that issue. To limit API usage, only repository owners, members, and collaborators can invoke it. The chat prompt and recent `/chat` history are sent to your configured AI provider, so do not include secrets or sensitive data. AI-provider usage may be billed by your provider.
