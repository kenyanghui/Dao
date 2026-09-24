#!/usr/bin/env python3
"""卡片流水线：txt(+#png) -> cards-data.json (+压缩jpg)

用法:
  python3 scripts/build_cards.py            # 仅重新生成 JSON
  python3 scripts/build_cards.py --images   # 同时把新增 png 压缩为 jpg
"""
import os, re, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECKS = [
    ('zonghui-daoshi-cards', 'zonghui'),
    ('yunqing-2026-cards', 'yunqing2026'),
]
MAX_WIDTH = 1080
JPEG_QUALITY = 82


def compress_new_images():
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    for d, _ in DECKS:
        p = os.path.join(ROOT, 'assets', d)
        for f in sorted(os.listdir(p)):
            if not f.endswith('.png'):
                continue
            dst = os.path.join(p, f[:-4] + '.jpg')
            if os.path.exists(dst):
                continue
            img = Image.open(os.path.join(p, f))
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
            img.convert('RGB').save(dst, 'JPEG', quality=JPEG_QUALITY,
                                    optimize=True, progressive=True)
            print(f'compressed {d}/{f} -> {os.path.getsize(dst)//1024}KB')


def parse_card(txt_path):
    text = open(txt_path, encoding='utf-8').read().strip()
    blocks = re.split(r'\n\s*\n', text)
    poem = blocks[0].strip()
    m = re.search(r'《(.+?)》', text)
    title = m.group(1) if m else ''
    def grab(pat):
        mm = re.search(pat, text)
        return mm.group(1).strip() if mm else ''
    highlight = grab(r'点睛：(.+)')
    quote_m = re.search(r'“(.+?)”', text)
    return {
        'poem': poem,
        'title': title,
        'quote': quote_m.group(1) if quote_m else '',
        'highlight': highlight,
        'insight': grab(r'今日一悟：(.+)'),
        'question': grab(r'今日一问：(.+)'),
        'action': grab(r'今日一行：「?(.+?)」?\s*$'),
    }


def build_json():
    out = {}
    for d, key in DECKS:
        p = os.path.join(ROOT, 'assets', d)
        cards = []
        for f in sorted(os.listdir(p)):
            if f.endswith('.txt'):
                num = f[:-4]
                jpg = os.path.join(p, num + '.jpg')
                if not os.path.exists(jpg):
                    print(f'WARN: {d}/{num}.jpg missing (run with --images)')
                c = parse_card(os.path.join(p, f))
                c['id'] = num
                c['image'] = f'assets/{d}/{num}.jpg'
                cards.append(c)
        out[key] = cards
        print(f'{key}: {len(cards)} cards')
    dst = os.path.join(ROOT, 'assets', 'cards-data.json')
    with open(dst, 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, indent=1)
    print(f'wrote {dst} ({os.path.getsize(dst)//1024}KB)')


if __name__ == '__main__':
    if '--images' in sys.argv:
        compress_new_images()
    build_json()
