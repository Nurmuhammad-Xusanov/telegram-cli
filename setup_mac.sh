#!/usr/bin/env bash
# macOS Setup Script for Telegram CLI

echo "=========================================="
echo "    Telegram CLI - macOS Setup            "
echo "=========================================="

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "[!] Python 3 not found. Please install Python 3 (e.g. via brew install python3)."
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Create virtual environment if not present
echo "[1/3] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Install dependencies
echo "[2/3] Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Configure environment
if [ ! -f .env ]; then
    echo "[3/3] Creating .env file from template..."
    cp .env.example .env
    echo "(!) Please edit .env with your TELEGRAM_API_ID and TELEGRAM_API_HASH"
fi

# Setup launcher in ~/.local/bin or ~/bin
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat <<EOF > "$BIN_DIR/telegram-cli"
#!/usr/bin/env bash
cd "$PROJECT_DIR"
exec "$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/main.py" "\$@"
EOF

chmod +x "$BIN_DIR/telegram-cli"
ln -sf "$BIN_DIR/telegram-cli" "$BIN_DIR/tg"

echo ""
echo "=========================================="
echo "  Setup Complete!                         "
echo "  Run it anytime by typing:               "
echo "    python3 main.py                       "
echo "  Or use the global shortcut:             "
echo "    ~/.local/bin/tg                       "
echo "=========================================="
