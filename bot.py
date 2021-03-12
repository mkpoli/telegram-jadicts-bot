from command_parser import Parameter, BadUsage, parse_command
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


BASE_DIR = Path(__file__).parent

def weblio(update: Update, context: CallbackContext) -> None:
    DESCRIPTION = "Weblio 辞書"
    PARAMETERS = [
        Parameter('word', str, "調べたい内容")
    ]
    
    try:
        word = parse_command(PARAMETERS, DESCRIPTION, update)[1]["word"]
    except BadUsage:
        return
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'<a href="https://www.weblio.jp/content/{urllib.parse.quote(word)}">https://www.weblio.jp/content/{word}</a>',
    )



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
