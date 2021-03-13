import urllib

from _env import PRODUCTION_MODE
from _version import __version__
from command_helper import Parameter, BadUsage, parse_command, reply
from kana_convert import convert
from telegram import Update
from telegram.ext import CallbackContext

def weblio(update: Update, context: CallbackContext) -> None:
    DESCRIPTION = "Weblio 辞書"
    PARAMETERS = [
        Parameter('word', str, "調べたい内容")
    ]
    
    try:
        word = parse_command(PARAMETERS, DESCRIPTION, update)[1]["word"]
    except BadUsage:
        return
    
    reply(
        update, context,
        text=f'<a href="https://www.weblio.jp/content/{urllib.parse.quote(word)}">https://www.weblio.jp/content/{word}</a>',
    )

def kana(update: Update, context: CallbackContext) -> None:
    DESCRIPTION = "ふりがな"
    PARAMETERS = [
        Parameter('text', str, "原文")
    ]
    
    try:
        text = parse_command(PARAMETERS, DESCRIPTION, update, last_ignore_space=True)[1]["text"]
    except BadUsage:
        return
    
    reply(
        update, context,
        text=convert(text)
    )

def version(update: Update, context: CallbackContext) -> None:
    DESCRIPTION = "バージョン表示"
    PARAMETERS = []
    
    try:
        parse_command(PARAMETERS, DESCRIPTION, update)
    except BadUsage:
        return

    reply(
        update, context,
        f"<pre>v{ __version__ } { '[dev]' if not PRODUCTION_MODE else '' }</pre>",
    )
