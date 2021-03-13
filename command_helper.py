from distutils.util import strtobool
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
    
    def __repr__(self) -> str:
        return f"Parameter({self.name}, {self.type}, {self.desc})"

def parse_command(parameters: Sequence[Parameter], description: str, update: Update, last_ignore_space=False) -> Tuple[str, dict]:
    # TODO: maxsplit = arg - rparameter + 1 = (1 - 1 + 1) | (2 - 1 + 1)
    
    required_parameters = list(filter(lambda x: not x.optional, parameters))

    if last_ignore_space and len(required_parameters) != len(parameters):
        raise IndexError("Optional parameters cannot co-exist with last_ignore_space=True !")

    command_parts = update.effective_message.text.split()
    command, args = command_parts[0], command_parts[1:]
    print(len)
    if last_ignore_space:
        args = update.effective_message.text.split(maxsplit = max(1, len(parameters) - 1))[1:]

    bind_logger(update).debug(f"command={command}, args={','.join(args)}")
    
    bad_usage_cases = [
        len(args) < len(required_parameters), # less than required
        not last_ignore_space and len(args) > len(parameters), # over argument when not ignoring last
    ]

    if any(bad_usage_cases):
        raise BadUsage

    TYPE_CONVERSION = {
        int: int,
        float: float,
        bool: lambda x: bool(strtobool(x))
    }

    result = {}

    try:
        for i, param in enumerate(parameters):
            try:
                arg = args[i]
            except IndexError:
                break
            
            if param.type in TYPE_CONVERSION:
                try:
                    arg = TYPE_CONVERSION(arg)
                except ValueError:
                    raise BadUsage
                    
            if param.checker and not param.checker(arg):
                raise BadUsage
            result[param.name] = arg

        return command, result
    except ValueError:
        command_usage(command, parameters, description, update)
        
        # command, args = update.effective_message.text, []

def command_usage(command: str, parameters: Sequence[Parameter], description: str, update: Update) -> None: 
    command_repr = f"{command} {' '.join(f'⟨{param.name}⟩' for param in parameters)}"
    if parameters:
        max_length = max(len(param.name) for param in parameters)
        paramtr_desc = "\n".join(f"    <code>{param.name.rjust(max_length)}</code> - {param.desc} " for param in parameters)
    else:
        paramtr_desc = "〈引数なし〉"
    update.effective_message.reply_text(
        f"<b>コマンドヘルプ</b>\n<code>{ command_repr }</code>\n\n{ description }\n{ paramtr_desc }")

MAX_MESSAGE_TXT_LENGTH = 4096
RESERVE_SPACE = 10

def page_message(update: Update, context: CallbackContext, text: str, reply: bool=False) -> Sequence[Message]:
    chat_id = update.effective_message.chat_id

    def send(text):
        if reply:
            return update.effective_message.reply_text(text=text)
        else:
            return context.bot.send_message(chat_id=chat_id, text=text)

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

def reply(update: Update, context: CallbackContext, text: str) -> None:
    if update.effective_message:
        update.effective_message.reply_text(text=text)
    else:
        return context.bot.send_message(chat_id=update.effective_message.chat_id, text=text)