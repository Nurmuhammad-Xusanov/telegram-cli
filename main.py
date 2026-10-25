import sys
import asyncio
from telegram_client import TelegramManager
from ui import TelegramTUI

async def main():
    print("\n" + "="*50)
    print("   TELEGRAM-CLI | Monochrome & Distraction-Free")
    print("="*50 + "\n")
    
    tg = TelegramManager()
    
    print("Connecting to Telegram...")
    is_auth = await tg.init()
    
    if not is_auth:
        print("\nAuthentication required.")
        print("Please enter your phone number with country code (e.g. +998901234567)")
        try:
            await tg.login_interactive()
            print("\nSuccessfully logged in! Launching interface...\n")
        except Exception as e:
            print(f"\nLogin failed: {e}")
            sys.exit(1)
            
    # Launch TUI
    app = TelegramTUI(tg)
    await app.run_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nExited. Goodbye!")
