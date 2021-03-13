import pykakasi
import regex
import jaconv

kks = pykakasi.kakasi()

KANJI_PATTERN = regex.compile(r"(\p{Han}+)")
def okurigana(orig, hira):
    # e.g. お悔やみ申し上げる
    new_pattern = KANJI_PATTERN.sub(r"(\p{Hiragana}+)", orig) # お(\p{Hiragana}+)やみ(\p{Hiragana}+)し(\p{Hiragana}+)げる
    mgroups = regex.match(new_pattern, hira).groups() # く, もう, あ
    filling = KANJI_PATTERN.sub(r"\1{}", orig) # お悔{}やみ申{}し上{}げる
    return filling.format(*[f"（{x}）" for x in mgroups]) # お悔（く）やみ申（もう）し上（あ）げる

EMPTY_PATTERN = regex.compile(r"(\s+)")

def convert(text: str) -> str:
    def convert_part(part: str) -> str:
        print(f"part={part}")
        if EMPTY_PATTERN.match(part):
            return part

        converted = kks.convert(part)
        
        def l(item: dict) -> str:
            if jaconv.kata2hira(item['orig']) == item['hira']:
                return item['orig']
            return okurigana(item['orig'], item['hira'])

        return "".join(map(l, converted))

    return "".join(map(convert_part, EMPTY_PATTERN.split(text)))
