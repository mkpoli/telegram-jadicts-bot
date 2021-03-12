from pathlib import Path

from telegram import ParseMode
from telegram.ext import CommandHandler, Defaults, Updater

from commands import kana, version, weblio

BASE_DIR = Path(__file__).parent

def main():
    with open(BASE_DIR / 'TOKEN') as f:
        token = f.read().strip()
        
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

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
