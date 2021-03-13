from typing import Any, Sequence
import urllib

from _env import PRODUCTION_MODE
from _version import __version__
from command_helper import Command, reply
from kana_convert import convert
from telegram import Update
from telegram.ext import CallbackContext

def weblio(update: Update, context: CallbackContext, command: Command, args: Sequence[Any]) -> None:
    word = args['word']
    reply(
        update, context,
        text=f'<a href="https://www.weblio.jp/content/{urllib.parse.quote(word)}">https://www.weblio.jp/content/{word}</a>',
    )

def kana(update: Update, context: CallbackContext, command: Command, args: Sequence[Any]) -> None:
    text = args['text']    
    reply(
        update, context,
        text=convert(text)
    )

def version(update: Update, context: CallbackContext, command: Command, args: Sequence[Any]) -> None:
    reply(
        update, context,
        f"<pre>v{ __version__ } { '[dev]' if not PRODUCTION_MODE else '' }</pre>",
    )
