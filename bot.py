import os

from _env import TOKEN, PRODUCTION_MODE
from _version import __version__

from loguru import logger

from telegram import ParseMode
from telegram.ext import CommandHandler, Defaults, Updater

from commands import kana, version, weblio


def main():
    logger.info(f"Running BOT version {__version__}")
    logger.debug(f"Production Mode = { PRODUCTION_MODE }")

    updater = Updater(
        defaults = Defaults(
            parse_mode = ParseMode.HTML,
            disable_notification=True,
            disable_web_page_preview=False
        ),
        token = TOKEN,
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

    if PRODUCTION_MODE:
        url = os.environ.get('URL')
        port = int(os.environ.get('PORT', 8000))
        logger.info("Starting Webhook on 8000 ...")
        updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            # url_path=token
        )
        updater.bot.set_webhook(url)
        logger.info(f"Webhook set on { url }")
    else:
        logger.info("Starting Polling...")
        updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
