#!/usr/bin/env python3
"""站点漂移守卫：发布前一致性检查。

用法: python3 scripts/check_site.py   (退出码非 0 = 有问题)
"""
import os, re, sys, json, html.parser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
failures = []


def fail(msg):
    failures.append(msg)
    print('FAIL:', msg)


class LinkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.local_refs = []

    def handle_starttag(self, tag, attrs):
        if tag not in ('a', 'img', 'link', 'script'):
            return
        for name, value in attrs:
            if name in ('href', 'src') and value:
                v = value.split('#')[0].split('?')[0]
                if v and not v.startswith(('http', '//', 'mailto:', 'data:')):
                    self.local_refs.append(v)


# 1. 本地链接完好
pages = [f for f in os.listdir(ROOT) if f.endswith('.html')]
if not pages:
    fail('根目录没有任何 html 页面')
for page in pages:
    parser = LinkParser()
    parser.feed(open(os.path.join(ROOT, page), encoding='utf-8').read())
    for ref in parser.local_refs:
        if ref == '/':
            continue
        if not os.path.exists(os.path.join(ROOT, ref)):
            fail(f'{page} -> 引用不存在: {ref}')

# 2. 图片体积守卫（README 约定 <500KB）
LIMIT_KB = 500
for dirpath, _, files in os.walk(os.path.join(ROOT, 'assets')):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            size_kb = os.path.getsize(os.path.join(dirpath, f)) // 1024
            if size_kb > LIMIT_KB:
                fail(f'图片超限 {size_kb}KB > {LIMIT_KB}KB: {os.path.relpath(os.path.join(dirpath, f), ROOT)}')

# 3. cards-data.json 与卡组目录一致
data_path = os.path.join(ROOT, 'assets', 'cards-data.json')
DECKS = {'zonghui': 'zonghui-daoshi-cards', 'yunqing2026': 'yunqing-2026-cards'}
if not os.path.exists(data_path):
    fail('assets/cards-data.json 不存在（先运行 scripts/build_cards.py）')
else:
    data = json.load(open(data_path, encoding='utf-8'))
    for key, d in DECKS.items():
        txts = {f[:-4] for f in os.listdir(os.path.join(ROOT, 'assets', d)) if f.endswith('.txt')}
        json_ids = {c['id'] for c in data.get(key, [])}
        if txts != json_ids:
            fail(f'{key}: txt({len(txts)}) 与 json({len(json_ids)}) 不一致，差集: {txts ^ json_ids}')
        for c in data.get(key, []):
            for field in ('title', 'poem', 'insight'):
                if not c.get(field):
                    fail(f'{key}/{c.get("id")}: 字段缺失 {field}')
            if not os.path.exists(os.path.join(ROOT, c['image'])):
                fail(f'{key}/{c["id"]}: 图片缺失 {c["image"]}')

# 4. 编码健康（无 GBK 乱码残留）
MOJIBAKE = re.compile(r'[ÃÂ¢â€Œï¿½]')
for f in pages + ['sitemap.xml', 'robots.txt']:
    p = os.path.join(ROOT, f)
    if not os.path.exists(p):
        fail(f'缺失文件: {f}')
        continue
    content = open(p, encoding='utf-8', errors='strict').read()
    if MOJIBAKE.search(content):
        fail(f'{f}: 疑似 mojibake 字符')

# 5. SEO 基本面（description/canonical）
for page in pages:
    content = open(os.path.join(ROOT, page), encoding='utf-8').read()
    if 'name="description"' not in content:
        fail(f'{page}: 缺少 meta description')
    if 'rel="canonical"' not in content:
        fail(f'{page}: 缺少 canonical')

print(f'\n检查完成: {"全部通过 ✓" if not failures else f"{len(failures)} 项失败"}')
sys.exit(1 if failures else 0)
