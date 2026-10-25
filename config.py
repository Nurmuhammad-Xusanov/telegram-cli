import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()

def _load_env():
    """Load environment variables from .env file if present"""
    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

_load_env()

# API credentials loaded securely from environment / .env
raw_api_id = os.environ.get("TELEGRAM_API_ID")
API_HASH = os.environ.get("TELEGRAM_API_HASH")

if not raw_api_id or not API_HASH or raw_api_id == "your_api_id_here":
    print("\n[ERROR] Telegram API credentials not found!")
    print("Please create a '.env' file in the project folder with:")
    print("  TELEGRAM_API_ID=your_id")
    print("  TELEGRAM_API_HASH=your_hash\n")
    sys.exit(1)

try:
    API_ID = int(raw_api_id)
except ValueError:
    print("\n[ERROR] TELEGRAM_API_ID must be a numeric integer.\n")
    sys.exit(1)

# Session and cache directories (ignored by git)
CONFIG_DIR = PROJECT_DIR / "data"
try:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    CONFIG_DIR = PROJECT_DIR

SESSION_FILE = str(CONFIG_DIR / "telegram_session")

# Minimalist settings
SHOW_CHANNELS = False
MESSAGE_LIMIT = 50
DIALOGS_LIMIT = 100
