from pathlib import Path
from urllib.parse import quote, urlparse

from generate import NAV_SECTIONS, EVENT_NAV_SECTIONS, load_page_visibility, load_setting
from utils import write_if_changed, write_page

ROOT = Path(__file__).resolve().parent

# 個別ページを自動収集するディレクトリと優先度
SCAN_DIRS = [
    ("character", 0.5),
    ("group", 0.5),
    ("detail", 0.4),
]


def list_html_files(dir_name):
    dir_path = ROOT / dir_name
    if not dir_path.exists():
        return []
    names = []
    for p in sorted(dir_path.glob('*.html')):
        # データ不備でキャラ名が空のまま生成された ".html" / " .html" を除外
        if not p.stem.strip():
            continue
        names.append(p.name)
    return names


def build_urls():
    visibility = load_page_visibility()
    urls = [("", 1.0)]

    for _title, items in NAV_SECTIONS + EVENT_NAV_SECTIONS:
        for key, href, _icon, _label in items:
            if key and not visibility.get(key, True):
                continue
            urls.append((href, 0.7))

    for dir_name, priority in SCAN_DIRS:
        for name in list_html_files(dir_name):
            urls.append((f"{dir_name}/{name}", priority))

    return urls


def generate_sitemap_xml(urls, base_url):
    entries = ''.join(
        f'  <url>\n'
        f'    <loc>{base_url}{quote(path, safe="/")}</loc>\n'
        f'    <priority>{priority}</priority>\n'
        f'  </url>\n'
        for path, priority in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{entries}'
        '</urlset>\n'
    )
    write_if_changed('sitemap.xml', xml)


def generate_sitemap_html(root_path):
    """人間向けの簡易サイトマップページ。detail/character/groupの大量ページは
    含めず、NAV_SECTIONS・EVENT_NAV_SECTIONSの主要ページだけを一覧表示する。"""
    visibility = load_page_visibility()

    def render_section(title, items):
        visible_items = [item for item in items if not item[0] or visibility.get(item[0], True)]
        if not visible_items:
            return ''
        rows = ''.join(
            f'        <li><a href="{root_path}/{href}">{label}</a></li>\n'
            for _key, href, _icon, label in visible_items
        )
        return f'    <h3>{title}</h3>\n    <ul>\n{rows}    </ul>\n'

    sections_html = ''.join(
        render_section(title, items) for title, items in EVENT_NAV_SECTIONS + NAV_SECTIONS
    )

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>サイトマップ - IDOLY PRIDE データベース M</title>
    <link rel="icon" href="image/icon.ico">
    <link rel="apple-touch-icon" href="image/icon.ico">
    <link rel="shortcut icon" href="image/icon.ico">
    <style>
        a {{ color: blue; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h3><a href="{root_path}">IDOLY PRIDE データベース M</a></h3>
{sections_html}</body>
</html>
'''
    write_page('sitemap.html', html)


if __name__ == "__main__":
    site_url = load_setting('SITE_URL') or ''
    root_path = urlparse(site_url).path.rstrip('/')

    urls = build_urls()
    generate_sitemap_xml(urls, site_url)
    generate_sitemap_html(root_path)
    print(f"サイトマップを生成しました: sitemap.xml ({len(urls)}件) / sitemap.html")
