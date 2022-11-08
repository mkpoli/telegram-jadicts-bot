# Logging
from loguru import logger
from telegram import Message


def bind_logger(message: Message):
    context_logger = logger.bind(
        chat_id=message.chat.id,
        chat_title=message.chat.title
        if message.chat.type != "private"
        else f"@{message.chat.username} ({message.chat.last_name}, {message.chat.first_name})",
        message_id=message.message_id,
        message_text=message.text,
    )
    return context_logger
