# Logging
from loguru import logger
from telegram import Update

def bind_logger(update: Update):
    context_logger = logger.bind(
        chat_id=update.effective_message.chat.id,
        chat_title=update.effective_message.chat.title if update.effective_message.chat.type != 'private' else f"@{update.effective_message.chat.username} ({update.effective_message.chat.last_name}, {update.effective_message.chat.first_name})",
        message_id=update.effective_message.message_id,
        message_text=update.effective_message.text
    )
    return context_logger
