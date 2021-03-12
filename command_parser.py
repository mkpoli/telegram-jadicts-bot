from telegram import Update, Message
from telegram.ext import CallbackContext
from typing import Callable, Optional, Sequence, Tuple
from logging_utils import bind_logger

class BadUsage(ValueError):
    pass

class Parameter: 
    def __init__(self, name: str, type: type, desc: str, checker: Optional[Callable]=None, optional: bool=False) -> None:
        self.name = name
        self.type = type
        self.desc = desc
        self.checker = checker
        self.optional = optional

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"Parameter({self.name})"

def parse_command(parameters: Sequence[Parameter], description: str, update: Update) -> Tuple[str, dict]:
    splited = update.effective_message.text.split()
    command = splited[0]
    try:
        args = splited[1:]
        bind_logger(update).debug(f"args={args}")
        result = {}

        bind_logger(update).debug(f"len(parameters)={len(parameters)}, len(args)={len(args)}, filter(lambda x: not x.optional, parameters)={list(filter(lambda x: not x.optional, parameters))}")
        if len(parameters) != len(args) and not len(list(filter(lambda x: not x.optional, parameters))) <= len(args) <= len(parameters):
            raise BadUsage

        for i, param in enumerate(parameters):
            try:
                arg = args[i]
            except IndexError:
                break
            if param.type == int:
                arg = int(arg)
            # if not param.checker or param.checker():
            if param.checker and not param.checker(arg):
                raise BadUsage
            # Arguemnts = type("Arguments")
            result[param.name] = arg
        return command, result
    except ValueError:
        command_usage(command, parameters, description, update)
        raise BadUsage
        # command, args = update.effective_message.text, []

def command_usage(command: str, parameters: Sequence[Parameter], description: str, update: Update) -> None: 
    command_repr = f"{command} {' '.join(f'⟨{param.name}⟩' for param in parameters)}"
    max_length = max(len(param.name) for param in parameters)
    paramtr_desc = "\n".join(f"    <code>{param.name.rjust(max_length)}</code> - {param.desc} " for param in parameters)
    update.effective_message.reply_text(
        f"<b>コマンドヘルプ</b>\n<code>{command_repr}</code>\n\n{description}\n{paramtr_desc}")

MAX_MESSAGE_TXT_LENGTH = 4096
RESERVE_SPACE = 10

def page_message(update: Update, context: CallbackContext, text: str, reply: bool=False) -> Sequence[Message]:
    chat_id = update.effective_message.chat_id

    def send(text):
        if reply:
            return update.effective_message.reply_text(text=text)
        else:
            return context.bot.send_message(chat_id = chat_id, text=text)

    if len(text) < MAX_MESSAGE_TXT_LENGTH:
        return [send(text=text)]

    page_length = MAX_MESSAGE_TXT_LENGTH - RESERVE_SPACE
    parts = [text[i:i + page_length] for i in range(0, len(text), page_length)]
    # we are reserving 8 characters for adding the page number in
    # the following format: [01/10]

    parts = [f"[{i + 1}/{len(parts)}] \n{part}" for i, part in enumerate(parts)]

    bind_logger(update).debug(f"Sending message in {len(parts)} pages")
    
    messages = []
    for part in parts:
        messages.append(send(text=part))
    return messages
