import os

from _env import TOKEN, PRODUCTION_MODE
from _version import __version__

from loguru import logger
from telegram import ParseMode
from telegram.ext import CommandHandler, Defaults, Updater

from commands import kana, get_dictionary_commands, version
from command_helper import Command, Parameter

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

    # Register commands
    COMMANDS = [
        *list(get_dictionary_commands()),
        Command('version', version, 'バージョン表示', []),
        Command('kana', kana, 'ふりがな', [Parameter('text', str, "原文")], last_ignore_space=True)
    ]

    logger.debug('Registering Commands...')
    for command in COMMANDS:
        logger.debug(f'  { command.name } - { command.description }')
        dispatcher.add_handler(CommandHandler(command.name, command.get_handler()))

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
