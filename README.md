# 🖤 Minimalist Telegram CLI (OLED & Dopamine-Free)

A clean, distraction-free, and keyboard-driven **Terminal User Interface (TUI)** client for Telegram. Designed for digital minimalism, low dopamine consumption, and maximum focus.

---

## ✨ Features

- **🖤 OLED Pure Black:** True black (`#000000`) theme with crisp typography. Zero distractions.
- **🛡️ Dopamine Control:** No auto-downloading images, videos, stickers, or animated gifs. Media is labeled compactly (e.g. `[Photo #1]`, `[Voice 15s #2]`).
- **👁️ On-Demand Media Viewer:** Need to view an invoice or photo? Open it only when you explicitly choose to via `/1` or `F3`.
- **📤 Easy File & Media Upload:** Send photos, videos, audio, or files directly from your terminal using `/send <path> [caption]`.
- **🚫 Distraction Filtering:** Public channels are hidden by default to prevent doomscrolling. Press `F2` to toggle if needed.
- **⚡ Super Fast Navigation:** Jump between chats, search, and type messages entirely using keyboard shortcuts.

---

## 🚀 Step-by-Step Installation Tutorial

Anyone can set up and run this client in less than 2 minutes:

### 1. Clone the repository
```bash
git clone https://github.com/Nurmuhammad-Xusanov/telegram-cli.git
cd telegram-cli
```


### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your Telegram API credentials
1. Log in to [my.telegram.org](https://my.telegram.org) with your Telegram phone number.
2. Go to **API development tools** and create an app (name it anything, e.g. `my-cli`).
3. Copy your `api_id` and `api_hash`.
4. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
5. Edit `.env` with your preferred text editor (e.g. `nano .env`) and paste your credentials:
   ```env
   TELEGRAM_API_ID=12345678
   TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef
   ```

### 5. Launch the application
```bash
python3 main.py
```
> **First run:** You will be prompted once in the terminal to enter your phone number and the verification code sent to your Telegram app. The session will be saved locally in `data/` and you won't need to log in again.

---

## ⌨️ Keyboard Shortcuts & Commands

### Navigation:
| Key | Action |
|---|---|
| `↑` / `↓` | Navigate chat list |
| `Enter` | Select and open chat |
| `Tab` | Switch focus between chat list and message input |
| `Esc` | Return focus to chat list |
| `/` | Focus search bar |
| `F2` | Toggle public channels on/off |
| `F3` | Open most recent media file in system viewer |
| `F5` | Refresh chats list |
| `Ctrl + C` | Quit application |

### Chat Commands (typed into message input):
- `/<id>` or `/open <id>` — Open media by its ID (e.g. `/1` or `/open 2`). Opens in your system's default media player.
- `/send <path> [caption]` — Send a local photo, video, audio, or file to the active chat.
  - *Example:* `/send ~/Downloads/receipt.jpg Monthly payment`
  - *Example:* `/send ~/report.pdf`
  - *Short alias:* `/f <path>`

---

## 🔐 Security & Privacy Note

- **Never share or commit your `.env` file or `data/` directory.**
- `data/telegram_session.session` contains your active Telegram authentication token.
- Both `.env` and `data/` are included in `.gitignore` by default to ensure your account credentials are never pushed to GitHub.
