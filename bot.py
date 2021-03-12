import os

from pathlib import Path

from telegram import ParseMode
from telegram.ext import CommandHandler, Defaults, Updater

from commands import kana, version, weblio

BASE_DIR = Path(__file__).parent

def main():
    if not (token := os.environ.get('TELEGRAM_BOT_TOKEN')):
        with open(BASE_DIR / 'TOKEN') as f:
            token = f.read().strip()
    
    if not token:
        raise KeyError("No TOKEN found!")

    production = bool(os.environ.get('TELEGRAM_BOT_PRODUCTION', default=False))

    updater = Updater(
        defaults = Defaults(
            parse_mode=ParseMode.HTML,
            disable_notification=True,
            disable_web_page_preview=False
        ),
        token = token,
        use_context = True
    )
    dispatcher = updater.dispatcher
    
    # COMMANDS
    COMMANDS = {
        # Weblio
        'weblio': weblio,
        'version': version,
        'kana': kana
    }

    for command, handler in COMMANDS.items():
        dispatcher.add_handler(CommandHandler(command, handler))

    if production:
        updater.start_webhook(port=int(os.environ.get('PORT', default=8000)))
    else:
        updater.start_polling()
        
    updater.idle()

if __name__ == '__main__':
    main()
