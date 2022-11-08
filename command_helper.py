import time

from distutils.util import strtobool
from loguru import logger
from telegram import Update, Message
from telegram.ext import CallbackContext, Dispatcher
from typing import Callable, Optional, Sequence, TypeVar, Dict
from logging_utils import bind_logger


class BadUsage(ValueError):
    pass


class Parameter:
    def __init__(
        self,
        name: str,
        type: type,
        desc: str,
        checker: Optional[Callable] = None,
        optional: bool = False,
    ) -> None:
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


class Command:
    def __init__(
        self,
        name: str,
        handler: Callable,
        description: str,
        parameters: Sequence[Parameter],
        last_ignore_space: bool = False,
    ) -> None:
        self.name = name
        self.handler = handler
        self.description = description
        self.parameters = parameters
        self.last_ignore_space = last_ignore_space

    def __str__(self) -> str:
        return f"Command({self.name}, {self.description})"

    def get_handler(self) -> Callable:
        def handler(update: Update, context: CallbackContext):
            try:
                args = parse_command(
                    self.parameters, self.description, update, self.last_ignore_space
                )
            except BadUsage as e:
                command_usage(
                    self.name,
                    self.parameters,
                    self.description,
                    update.effective_message,
                )
                bind_logger(update).debug(f"BadUsage: {e}")
                return
            self.handler(update, context, self, args)

        return handler


def parse_command(
    parameters: Sequence[Parameter],
    description: str,
    update: Update,
    last_ignore_space=False,
) -> Dict[str, str]:
    required_parameters = list(filter(lambda x: not x.optional, parameters))

    if last_ignore_space and len(required_parameters) != len(parameters):
        raise IndexError(
            "Optional parameters cannot co-exist with last_ignore_space=True !"
        )

    command_parts = update.message.text.split()
    command, args = command_parts[0], command_parts[1:]
    if last_ignore_space:
        args = update.message.text.split(maxsplit=max(1, len(parameters) - 1))[1:]

    bind_logger(update).debug(f"command={command}, args={','.join(args)}")

    if len(args) < len(required_parameters):
        raise BadUsage("args less than required")

    if not last_ignore_space and len(args) > len(parameters):
        raise BadUsage("over argument")

    TYPE_CONVERSION: Dict[type, Callable] = {
        int: int,
        float: float,
        bool: lambda x: bool(strtobool(x)),
    }

    result = {}

    for i, param in enumerate(parameters):
        try:
            arg = args[i]
        except IndexError:
            break

        if param.type in TYPE_CONVERSION:
            try:
                arg = TYPE_CONVERSION[param.type](arg)
            except ValueError:
                raise BadUsage("bad value of type")

        if param.checker and not param.checker(arg):
            raise BadUsage("failed check")

        result[param.name] = arg

    return result


def _delete_after(delay: int, message: Message):
    """Delete message after specified seconds.

    Args:
        delay (int): Delay in secs
        message (Message): Message to delete
    """
    time.sleep(delay)
    message.delete()
    logger.debug(
        f"Message {message.message_id} in {message.chat.type} chat {message.chat.id} deleted:\n{message.text}"
    )
    return


RT = TypeVar("RT")


def delete_after(delay: int) -> Callable[[Callable[..., Message]], Callable[..., None]]:
    def decorator(func: Callable[..., Message]) -> Callable[..., None]:
        def wrapper(*args, **kwargs) -> None:
            sent_message = func(*args, **kwargs)
            if not isinstance(sent_message, Message):
                raise TypeError("Message sender is not returning sent message")
            dispatcher = Dispatcher.get_instance()
            dispatcher.run_async(_delete_after, delay, sent_message)

        return wrapper

    return decorator


@delete_after(10)
def command_usage(
    command: str, parameters: Sequence[Parameter], description: str, reply_to: Message
) -> Message:
    """Reply to user when a bad command usage is found.

    Args:
        command (str): Command Name
        parameters (Sequence[Parameter]): Parameters of Command
        description (str): Description of Command
        reply_to (Message): User Message of Bad Usage
    """
    command_repr = f"/{command} {' '.join(f'⟨{param.name}⟩' for param in parameters)}"
    if parameters:
        max_length = max(len(param.name) for param in parameters)
        paramtr_desc = "\n".join(
            f"    <code>{param.name.rjust(max_length)}</code> - {param.desc} "
            for param in parameters
        )
    else:
        paramtr_desc = "〈引数なし〉"
    sent_message = reply_to.reply_text(
        f"<b>コマンドヘルプ</b>\n<code>{ command_repr }</code>\n\n{ description }\n{ paramtr_desc }"
    )

    return sent_message


MAX_MESSAGE_TXT_LENGTH = 4096
RESERVE_SPACE = 10


def page_message(
    update: Update, context: CallbackContext, text: str, reply: bool = False
) -> Sequence[Message]:
    def send(text):
        if reply and update.effective_message:
            return update.effective_message.reply_text(text=text)
        else:
            return context.bot.send_message(chat_id=update.message.chat_id, text=text)

    if len(text) < MAX_MESSAGE_TXT_LENGTH:
        return [send(text=text)]

    page_length = MAX_MESSAGE_TXT_LENGTH - RESERVE_SPACE
    parts = [text[i : i + page_length] for i in range(0, len(text), page_length)]
    # we are reserving 8 characters for adding the page number in
    # the following format: [01/10]

    parts = [f"[{i + 1}/{len(parts)}] \n{part}" for i, part in enumerate(parts)]

    bind_logger(update).debug(f"Sending message in {len(parts)} pages")

    messages = []
    for part in parts:
        messages.append(send(text=part))
    return messages


def reply(update: Update, context: CallbackContext, text: str) -> Message:
    if update.effective_message:
        return update.effective_message.reply_text(text=text)
    else:
        return context.bot.send_message(chat_id=update.message.chat_id, text=text)
