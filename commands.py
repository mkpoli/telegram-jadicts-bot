import urllib

from _env import PRODUCTION_MODE
from single_source import __version__
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

class Dictionary:
    def __init__(self, name: str, desc: str, link: str) -> None:
        self.name = name
        self.desc = desc
        self.link = link
        
    def generate_command(self) -> Command:
        def handler(update: Update, context: CallbackContext, command: Command, args: Sequence[Any]) -> None:
            word = args['word']
            reply(
                update, context,
                text=f'<a href="{ self.link.format(urllib.parse.quote(word)) }">{ self.link.format(word) }</a>',
            )
        return Command(self.name, handler, self.desc, [Parameter('word', str, '調べたい内容')])

# Generate Dictionary Comamnds
DICTIONARYS = [
    # Weblio
    Dictionary('weblio', 'Weblio 辞書', 'https://www.weblio.jp/content/{}'),
    Dictionary('cjjc', 'Weblio 日中・中日辞典', 'https://cjjc.weblio.jp/content/{}'),
    # goo
    Dictionary('goo', 'goo 国語辞書', 'https://dictionary.goo.ne.jp/srch/all/{}/m0u/')
]

def get_dictionary_commands():
    for dictionary in DICTIONARYS:
        yield dictionary.generate_command()
