import hashlib
import html
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

WEEKDAYS_JA = ['月', '火', '水', '木', '金', '土', '日']
# 日本時間はDSTが無い固定UTC+9のため、tzdataへの依存を避けて固定オフセットで表す
# (WindowsのPython標準環境にはzoneinfo用のtzdataが同梱されていないため)
JST = timezone(timedelta(hours=9))

SITE_NAME = 'IDOLY PRIDE データベース M'
# サイト全体で使うOGP用の代表画像(favicon兼用)
OG_IMAGE_PATH = 'image/icon.png'


def now_jst():
    """実行環境のタイムゾーンに関わらず日本時間の現在時刻を返す(naive datetime)。
    GitHub ActionsのランナーはUTCで動作するため、datetime.now()をそのまま使うと
    9時間ずれてしまう。"""
    return datetime.now(JST).replace(tzinfo=None)


def load_setting(key):
    """gitignore/setting.txt から `key=value` 形式の設定値を読む。
    generate.py・generate_sitemap.py・utils.py(本ファイル)で共通利用する。"""
    with open('gitignore/setting.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith(f'{key}='):
                val = line.split('=', 1)[1].strip()
                return val if val else None
    return None


def _site_url():
    url = load_setting('SITE_URL') or ''
    if url and not url.endswith('/'):
        url += '/'
    return url


SITE_URL = _site_url()


def seo_meta_html(page_url, title, description):
    """canonical・OGP・Twitter CardのHTMLブロックを返す。
    page_url はサイトルート基準の相対パス(例: 'content/idol_list.html'、トップページは'')。
    ファイル名にスペースを含むページがあるため、sitemap.xmlと同様にURLエンコードする。"""
    canonical = SITE_URL + quote(page_url, safe='/')
    og_image = SITE_URL + OG_IMAGE_PATH
    title_esc = esc(title)
    description_esc = esc(description)
    return f'''<link rel="canonical" href="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{title_esc}">
    <meta property="og:description" content="{description_esc}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:site_name" content="{esc(SITE_NAME)}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:locale" content="ja_JP">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title_esc}">
    <meta name="twitter:description" content="{description_esc}">
    <meta name="twitter:image" content="{og_image}">'''


# Google Fonts / Font AwesomeはCSS内の@importではなくHTML側でpreconnectしてから
# 読み込むことで、フォント取得の開始を早めレンダリングブロックを軽減する
FONT_PRECONNECT_HTML = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    "    <link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=M+PLUS+1p:wght@400;700&display=swap\">"
)
FA_PRECONNECT_HTML = '<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>'

# 記事内広告(in-article)。テキスト・データ量の多い詳細/プロフィール系ページにのみ
# 挿入する(検索・フィルタ操作が中心の一覧/ツール系ページには置かない)。
IN_ARTICLE_AD_HTML = '''<div class="in-article-ad">
    <ins class="adsbygoogle"
         style="display:block; text-align:center;"
         data-ad-layout="in-article"
         data-ad-format="fluid"
         data-ad-client="ca-pub-9647262951514669"
         data-ad-slot="8576527386"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>'''


def breadcrumb_jsonld(items):
    """パンくずのBreadcrumbList構造化データ(JSON-LD)を返す。
    items: [(name, url), ...] urlはサイトルート基準の相対パス。"""
    element_list = [
        {
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": SITE_URL + quote(url, safe='/'),
        }
        for i, (name, url) in enumerate(items, 1)
    ]
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": element_list,
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'

# キャラプロフィール(data/profiles.json)が未登録のときのフォールバック値。
# generate_detail.py と generate_char_info.py の両方で使うため共通化している。
DEFAULT_PROFILE = ["-", "-", "-", "-", "-", "-", "", "", "", "-", "-", "", "", "-", "", "", "-", "", "", "", "", "-"]


def esc(value):
    """CSV/JSONなど外部データ由来の文字列をHTMLに埋め込む前にエスケープする。"""
    return html.escape(str(value), quote=True)


def esc_rich(value):
    """スキル効果文など、意図的に<br>改行タグだけを含むCSVテキスト用のエスケープ。
    それ以外のHTMLはすべてエスケープしつつ、<br>だけは改行として復元する。"""
    escaped = html.escape(str(value), quote=True)
    return escaped.replace('&lt;br&gt;', '<br>')


def build_char_options_html(characters):
    seen = set()
    options = []
    for c in characters:
        name = c[2]
        if name not in seen:
            seen.add(name)
            options.append(f'<option value="{esc(name)}">{esc(name)}</option>')
    return '\n'.join(options)


def write_if_changed(path, content):
    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    hash_path = f'gitignore/{os.path.basename(path)}.hash'
    os.makedirs('gitignore', exist_ok=True)
    if os.path.exists(path) and os.path.exists(hash_path):
        with open(hash_path, 'r') as f:
            if f.read().strip() == new_hash:
                print(f"変更なし: {path} をスキップ")
                return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    with open(hash_path, 'w') as f:
        f.write(new_hash)
    return True


def _format_footer_date(dt):
    return f"{dt.year}/{dt.month}/{dt.day}({WEEKDAYS_JA[dt.weekday()]}) {dt.strftime('%H:%M')}"


def _get_last_updated(path, content):
    """contentのハッシュが前回記録時から変わっていなければ、前回の最終更新日時を
    そのまま返す。フッター自体の文言はcontentに含めずに判定するため、実質的な
    変更が無い再生成では日時が動かず、write_if_changedの無駄な書き込み抑止とも
    整合する。"""
    meta_path = f'gitignore/{os.path.basename(path)}.updated'
    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    os.makedirs('gitignore', exist_ok=True)
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        if len(lines) == 2 and lines[0] == new_hash:
            return datetime.fromisoformat(lines[1])
    now = now_jst()
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(f'{new_hash}\n{now.isoformat()}')
    return now


def write_page(path, content):
    """ページ内容が実際に変わった日時を示すフッターを</body>直前に挿入してから書き出す。"""
    last_updated = _get_last_updated(path, content)
    footer = f'<footer class="site-footer">最終更新: {_format_footer_date(last_updated)}</footer>\n'
    if '</body>' in content:
        content = content.replace('</body>', footer + '</body>', 1)
    else:
        content += footer
    return write_if_changed(path, content)
