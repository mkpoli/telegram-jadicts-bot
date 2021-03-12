import pykakasi
import re

kks = pykakasi.kakasi()

def get_okurigana(a: str, b: str) -> str:
    # Reverse
    ra, rb = a[::-1], b[::-1]
    def _iter():
        for a, b in zip(ra, rb):
            if a == b:
                yield a
            else:
                return
    return ''.join(reversed(list(_iter())))

def format_okurigana(orig: str, hira: str, okurigana: str) -> tuple[str, str, str]:
    okurigana_length = len(okurigana)
    return [orig[:-okurigana_length], hira[:-okurigana_length], okurigana]

EMPTY_PATTERN = re.compile(r"(\s+)")

def convert(text: str) -> str:
    def convert_part(part: str) -> str:
        print(f"part={part}")
        if EMPTY_PATTERN.match(part):
            return part

        converted = kks.convert(part)
        
        def l(item: dict) -> str:
            if item['orig'] == item['hira'] or item['orig'] == item['kana']:
                return item['orig']
            elif len(okurigana := get_okurigana(item['orig'], item['hira'])):
                # 送り仮名
                orig, hira, okrgn = format_okurigana(item['orig'], item['hira'], okurigana)
                return f"{ orig }（{ hira }）{okrgn}"
            else:
                return f"{ item['orig'] }（{ item['hira'] }）"
        
        return "".join(map(l, converted))

    return "".join(map(convert_part, EMPTY_PATTERN.split(text)))
