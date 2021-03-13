import pykakasi
import regex
import jaconv

from loguru import logger

kks = pykakasi.kakasi()

KANJI_PATTERN = regex.compile(r"(\p{Han}+)")
def okurigana(orig, hira):
    # e.g. お悔やみ申し上げる
    new_pattern = KANJI_PATTERN.sub(r"([\p{Hiragana}\p{Katakana}]+)", jaconv.kata2hira(orig)) # お(\p{Hiragana}+)やみ(\p{Hiragana}+)し(\p{Hiragana}+)げる
    try:
        mgroups = regex.match(new_pattern, hira).groups() # く, もう, あ
    except AttributeError as e:
        logger.error(f"No matched groups. orig={orig}, hira={hira} | new_pattern='{new_pattern}'")
        raise e
    filling = KANJI_PATTERN.sub(r"\1{}", orig) # お悔{}やみ申{}し上{}げる
    return filling.format(*[f"（{x}）" for x in mgroups]) # お悔（く）やみ申（もう）し上（あ）げる

EMPTY_PATTERN = regex.compile(r"(\s+)")

def convert(text: str) -> str:
    def convert_part(part: str) -> str:
        if EMPTY_PATTERN.match(part):
            return part

        converted = kks.convert(part)
        
        def l(item: dict) -> str:
            if jaconv.kata2hira(item['orig']) == item['hira']:
                return item['orig']
            return okurigana(item['orig'], item['hira'])

        return "".join(map(l, converted))
    parts = EMPTY_PATTERN.split(text)
    logger.debug(f"Convert parts = {parts}")
    return "".join(map(convert_part, parts))
