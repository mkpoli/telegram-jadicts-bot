import urllib

from _env import PRODUCTION_MODE
from _version import __version__
from command_helper import Command, Parameter, reply
from kana_convert import convert
from telegram import Update
from telegram.ext import CallbackContext
from typing import Any, Sequence

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

# Generate Dictionary Comamnds
DICTIONARYS = {
    'weblio': {
        'desc': 'Weblio 辞書',
        'link': 'https://www.weblio.jp/content/{}',
    },
    'goo': {
        'desc': 'goo 国語辞書',
        'link': 'https://dictionary.goo.ne.jp/word/{}/'
    }
}

def get_dictionary_commands():
    for name, info in DICTIONARYS.items():
        desc = info['desc']
        link = info['link']
        def handler(update: Update, context: CallbackContext, command: Command, args: Sequence[Any]) -> None:
            word = args['word']
            reply(
                update, context,
                text=f'<a href="{ link.format(urllib.parse.quote(word)) }">{ link.format(word) }</a>',
            )
        yield Command(name, handler, desc, [Parameter('word', str, '調べたい内容')])
