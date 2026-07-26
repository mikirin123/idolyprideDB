import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse

from generate import NAV_SECTIONS, HACHIHAJI_NAV_SECTION, C108_NAV_SECTION, load_page_visibility
from utils import write_if_changed, write_page, load_setting, now_jst, WEEKDAYS_JA

ROOT = Path(__file__).resolve().parent

# robots.txtはドメインルート(https://mikirin123.github.io/robots.txt)に
# 置かないとcrawlerに認識されないため、idolyprideDBとは別のユーザーページ
# リポジトリ側に生成する。ローカル(このリポジトリと兄弟フォルダに
# mikirin123.github.ioがcloneされている環境)専用で、CI環境には存在しない
# ため、無ければ何もせずスキップする。
ROOT_SITE_DIR = Path(r"C:\Users\oya02\Documents\GitHub\mikirin123.github.io")

# 個別ページを自動収集するディレクトリと優先度
SCAN_DIRS = [
    ("character", 0.5),
    ("group", 0.5),
    ("detail", 0.4),
]

# ホーム画面のサイドバー(ハンバーガーメニュー外)から直接リンクされているページ
HOME_EXTRA_PAGES = [
    ("content/events_list.html", 0.6, "開催中のイベント"),
    ("content/updates_list.html", 0.6, "更新情報"),
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

    for href, priority, _label in HOME_EXTRA_PAGES:
        urls.append((href, priority))

    for _title, items in [C108_NAV_SECTION] + NAV_SECTIONS + [HACHIHAJI_NAV_SECTION]:
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


def _root_last_updated(tracking_key, content):
    """ROOT_SITE_DIR向けページの最終更新日時を、実質的な内容(フッター抜き)の
    ハッシュが変わった時だけ更新する。utils._get_last_updatedと同じ考え方だが、
    ローカル側のindex.html(gitignore/index.html.updated)と同名衝突しないよう
    ROOT_SITE_DIR専用のキーで別管理する。"""
    meta_path = ROOT / 'gitignore' / f'root_{tracking_key}.updated'
    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    if meta_path.exists():
        lines = meta_path.read_text(encoding='utf-8').splitlines()
        if len(lines) == 2 and lines[0] == new_hash:
            return datetime.fromisoformat(lines[1])
    now = now_jst()
    meta_path.write_text(f'{new_hash}\n{now.isoformat()}', encoding='utf-8')
    return now


def _write_root_page(name, tracking_key, content):
    """ROOT_SITE_DIR(mikirin123.github.io)側にページを書き出す。
    CI環境などROOT_SITE_DIRが存在しない場合は何もしない。"""
    if not ROOT_SITE_DIR.exists():
        print(f"スキップ: {ROOT_SITE_DIR} が無いため{name}は生成しません")
        return
    last_updated = _root_last_updated(tracking_key, content)
    footer_date = f"{last_updated.year}/{last_updated.month}/{last_updated.day}({WEEKDAYS_JA[last_updated.weekday()]}) {last_updated.strftime('%H:%M')}"
    full_content = content.replace(
        '</body>', f'<footer class="site-footer">最終更新: {footer_date}</footer>\n</body>', 1
    )
    dest = ROOT_SITE_DIR / name
    if dest.exists() and dest.read_text(encoding='utf-8') == full_content:
        print(f"変更なし: {name}(ルート) をスキップ")
        return
    dest.write_text(full_content, encoding='utf-8')
    print(f"{name}を生成しました: {dest}")


def generate_robots_txt(base_url):
    content = (
        'User-agent: *\n'
        'Allow: /\n'
        f'Sitemap: {base_url}sitemap.xml\n'
    )
    if not ROOT_SITE_DIR.exists():
        print(f"スキップ: {ROOT_SITE_DIR} が無いためrobots.txtは生成しません")
        return
    dest = ROOT_SITE_DIR / 'robots.txt'
    if dest.exists() and dest.read_text(encoding='utf-8') == content:
        print("変更なし: robots.txt(ルート) をスキップ")
        return
    dest.write_text(content, encoding='utf-8')
    print(f"robots.txtを生成しました: {dest}")


def generate_sitemap_html(root_path):
    """人間向けの簡易サイトマップページ。detail/character/groupの大量ページは
    含めず、NAV_SECTIONS・HACHIHAJI_NAV_SECTION・C108_NAV_SECTIONの主要ページだけを一覧表示する。"""
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

    home_extra_rows = ''.join(
        f'        <li><a href="{root_path}/{href}">{label}</a></li>\n'
        for href, _priority, label in HOME_EXTRA_PAGES
    )
    home_extra_html = f'    <ul>\n{home_extra_rows}    </ul>\n' if home_extra_rows else ''

    sections_html = ''.join(
        render_section(title, items)
        for title, items in [C108_NAV_SECTION] + NAV_SECTIONS + [HACHIHAJI_NAV_SECTION]
    )

    def render(icon_href):
        return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>サイトマップ - IDOLY PRIDE データベース M</title>
    <link rel="icon" href="{icon_href}">
    <link rel="apple-touch-icon" href="{icon_href}">
    <link rel="shortcut icon" href="{icon_href}">
    <style>
        a {{ color: blue; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h3><a href="{root_path}">IDOLY PRIDE データベース M</a></h3>
{home_extra_html}{sections_html}</body>
</html>
'''

    write_page('sitemap.html', render('image/icon.ico'))
    # mikirin123.github.io(ドメインルート)にも同内容を配置し、ルートに
    # アクセスした際にサイト全体のサイトマップを表示できるようにする。
    # ROOT_SITE_DIR側は独自のicon.icoを直下に持つため、パスもそれに合わせる。
    _write_root_page('index.html', 'sitemap_index', render('icon.ico'))


if __name__ == "__main__":
    site_url = load_setting('SITE_URL') or ''
    root_path = urlparse(site_url).path.rstrip('/')

    urls = build_urls()
    generate_sitemap_xml(urls, site_url)
    generate_sitemap_html(root_path)
    generate_robots_txt(site_url)
    print(f"サイトマップを生成しました: sitemap.xml ({len(urls)}件) / sitemap.html")
