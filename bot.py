from command_helper import Parameter, BadUsage, parse_command
from pathlib import Path

import urllib

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    CallbackQuery
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Defaults,
    Filters,
    MessageHandler,
    PicklePersistence,
    Updater,
)

from commands import weblio

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
        'weblio': weblio# weblio
    }

    for command, handler in COMMANDS.items():
        dispatcher.add_handler(CommandHandler(command, handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
