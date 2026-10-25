#!/data/data/com.termux/files/usr/bin/bash
# Android Termux Setup Script for Telegram CLI

echo "=========================================="
echo "  Telegram CLI - Android (Termux) Setup   "
echo "=========================================="

# Update and install dependencies
echo "[1/4] Installing Python, Git and Termux tools..."
pkg update -y
pkg install -y python git termux-tools clang libjpeg-turbo

# Virtual environment / dependencies
echo "[2/4] Installing Python libraries..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment if not present
if [ ! -f .env ]; then
    echo "[3/4] Creating .env file from template..."
    cp .env.example .env
    echo "(!) Please edit .env with your TELEGRAM_API_ID and TELEGRAM_API_HASH"
fi

# Create global shortcut in Termux ($PREFIX/bin/telegram-cli and tg)
echo "[4/4] Creating terminal shortcut 'tg' and 'telegram-cli'..."
BIN_DIR="$PREFIX/bin"
PROJECT_DIR="$(pwd)"

cat <<EOF > "$BIN_DIR/telegram-cli"
#!/data/data/com.termux/files/usr/bin/bash
cd "$PROJECT_DIR"
python3 main.py "\$@"
EOF

chmod +x "$BIN_DIR/telegram-cli"
ln -sf "$BIN_DIR/telegram-cli" "$BIN_DIR/tg"

echo ""
echo "=========================================="
echo "  Setup Complete!                         "
echo "  Run it anytime by typing: tg            "
echo "=========================================="
