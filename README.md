# 🖤 Minimalist Telegram CLI (OLED & Dopamine-Free)

A clean, distraction-free, and keyboard-driven **Terminal User Interface (TUI)** client for Telegram. Built for digital minimalism, low dopamine consumption, and maximum focus on both **Linux Desktop** and **Android (Termux)**.

---

## 📸 Preview

### 💻 Linux Desktop Terminal
![Linux Desktop Preview](assets/preview-desktop.svg)

### 📱 Android Mobile (Termux / OneUI)
<p align="center">
  <img src="assets/preview-mobile.svg" alt="Android Mobile Preview" width="340"/>
</p>

---

## ✨ Features

- **🖤 OLED Pure Black:** True black (`#000000`) theme with crisp typography. Zero distractions.
- **🛡️ Dopamine Control:** No auto-downloading images, videos, stickers, or animated gifs. Media is labeled compactly (e.g. `[Photo #1]`, `[Voice 15s #2]`).
- **👁️ On-Demand Media Viewer:** Need to view an invoice or photo? Open it only when you explicitly choose to via `/1` or `F3`.
- **📤 Easy File & Media Upload:** Send photos, videos, audio, or files directly from your terminal using `/send <path> [caption]`.
- **🚫 Distraction Filtering:** Public channels are hidden by default to prevent doomscrolling. Press `F2` to toggle if needed.
- **⚡ Super Fast Navigation:** Jump between chats, search, and type messages entirely using keyboard shortcuts.

---

## 💻 Linux Desktop Installation

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
5. Edit `.env` with your preferred editor and paste your credentials:
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

## 📱 Android (Termux / OneUI) Step-by-Step Tutorial

You can run this client directly on your Android phone (Samsung OneUI / Android 14+) with a 1-tap Homescreen app icon using **Termux:Widget**:

### Step 1: Install Termux & Termux:Widget
1. Download and install **[Termux](https://f-droid.org/en/packages/com.termux/)** from F-Droid.
2. Download and install **[Termux:Widget](https://f-droid.org/en/packages/com.termux.widget/)** from F-Droid.

### Step 2: One-Line Automatic Setup
Open Termux and run this single command:
```bash
pkg update -y && pkg install -y git python && git clone https://github.com/Nurmuhammad-Xusanov/telegram-cli.git && cd telegram-cli && bash setup_android.sh
```
> This automatically installs all dependencies, creates the global `tg` command, and configures the `Termux:Widget` shortcut!

### Step 3: Configure credentials
```bash
nano .env
```
Paste your `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`, then press `Ctrl + O`, `Enter`, `Ctrl + X` to save.

### Step 4: Launch!
- **From Termux:** Simply type `tg` and press Enter.
- **From Android Home Screen (1-Tap Icon):**
  1. Long-press on an empty area of your phone's Home Screen and tap **Widgets**.
  2. Select **Termux:Widget** (or **Termux Shortcut**).
  3. Pick **Telegram** from the list.
  4. Done! It now opens like a native app directly from your home screen.


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
- `/<id>` or `/open <id>` — Open media by its ID (e.g. `/1` or `/open 2`). Opens in your system gallery/player.
- `/send <path> [caption]` — Send a local photo, video, audio, or file to the active chat.
  - *Example:* `/send ~/Downloads/receipt.jpg Monthly payment`
  - *Example:* `/send ~/report.pdf`
  - *Short alias:* `/f <path>`

---

## 🔐 Security & Privacy Note

- **Never share or commit your `.env` file or `data/` directory.**
- `data/telegram_session.session` contains your active Telegram authentication token.
- Both `.env` and `data/` are included in `.gitignore` by default to ensure your account credentials are never pushed to GitHub.
