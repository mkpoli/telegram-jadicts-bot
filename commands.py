import urllib

from _version import __version__
from command_helper import Parameter, BadUsage, parse_command, reply
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
        text=f'<a href="https://www.weblio.jp/content/{urllib.parse.quote(word)}">https://www.weblio.jp/content/{word}</a>',
    )

def version(update: Update, context: CallbackContext) -> None:
    DESCRIPTION = "バージョン表示"
    PARAMETERS = []
    
    try:
        parse_command(PARAMETERS, DESCRIPTION, update)
    except BadUsage:
        return

    reply(f"<pre>v{ __version__ }</pre>")