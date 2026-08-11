import csv
import html as html_lib
import os
import re
import json
from datetime import datetime
from urllib.parse import quote

# 実行時のカレントディレクトリに関わらず、常にこのスクリプトと同じ
# フォルダ(event/C108/)でCSVを読み書きするための基準パス
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PAGE_URL = 'event/C108/oshinagaki.html'

WEEKDAYS_JA = ['月', '火', '水', '木', '金', '土', '日']


def _load_site_url():
    try:
        with open(os.path.join(REPO_ROOT, 'gitignore', 'setting.txt'), encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('SITE_URL='):
                    url = line.split('=', 1)[1].strip()
                    return url + ('' if url.endswith('/') else '/')
    except FileNotFoundError:
        pass
    return ''


SITE_URL = _load_site_url()

# サイト全体の方針(utils.pyのFONT_PRECONNECT_HTML)に合わせて、
# preconnectだけでなくGoogle Fonts本体のCSSも読み込む。
FONT_PRECONNECT_HTML = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=M+PLUS+1p:wght@400;700&display=swap">'
)


def breadcrumb_jsonld(items):
    """パンくずのBreadcrumbList構造化データ(JSON-LD)。utils.pyのbreadcrumb_jsonldと同じ形式。
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


def esc(value):
    """CSV由来の文字列をHTMLに埋め込む前にエスケープする。"""
    return html_lib.escape(str(value), quote=True)


def esc_rich(value):
    """サークル名など、記入者が<br>改行だけを使っている場合に備えたエスケープ。
    <br>以外のHTMLはすべてエスケープしつつ、<br>だけは改行として復元する。"""
    escaped = html_lib.escape(str(value), quote=True)
    return escaped.replace('&lt;br&gt;', '<br>')


def extract_tweet_id(url):
    m = re.search(r"(?:twitter\.com|x\.com)/[^/]+/status/(\d+)", url)
    return m.group(1) if m else None

def read_csv(path):
    try:
        with open(os.path.join(SCRIPT_DIR, path), encoding='utf-8', newline='') as f:
            return [row for row in csv.DictReader(f)]
    except FileNotFoundError:
        return []

circles = [r for r in read_csv('circle-list.csv') if r.get('サークル名', '').strip()]

group_defs = [
    ("day1", "1日目", lambda r: r.get('日程', '').strip() == '1日目'),
    ("day2", "2日目", lambda r: r.get('日程', '').strip() == '2日目'),
]

def id_sort_key(r):
    try:
        return int(re.sub(r"\D", "", r.get('circle-id', '')) or 0)
    except ValueError:
        return 0


def parse_sanka_names(sanka):
    """参加者欄を個人名のリストに分割する。末尾の@ユーザー名は代表者名との突き合わせのため取り除く。"""
    if not sanka:
        return []
    names = []
    for s in re.split(r'[、,\s]+', sanka):
        s = s.strip()
        if not s:
            continue
        m = re.match(r'^(.*?)@([A-Za-z0-9_]{1,15})$', s)
        names.append(m.group(1) if m else s)
    return names


# 代表者名から本体CSVの行を逆引きするためのマップ(合同誌の参加者名からサークル名・配置等を補うため)
rep_to_circle = {}
for r in circles:
    rep = r.get('代表者', '').strip()
    if rep and rep not in rep_to_circle:
        rep_to_circle[rep] = r

grouped = {g[0]: [] for g in group_defs}
all_items = []
for row in circles:
    place = row.get('配置', '').strip()
    oshinagaki = row.get('おしながき・告知', '').strip()
    tweet_id = extract_tweet_id(oshinagaki)
    if not tweet_id:
        continue
    tw_name = row.get('代表者', '').strip()
    name = row.get('サークル名', '').strip()
    for key, label, cond in group_defs:
        if cond(row):
            item = {
                "name": name,
                "tw_name": tw_name,
                "place": place,
                "tweet_id": tweet_id,
                "tweet_url": oshinagaki,
                "_sort": id_sort_key(row),
            }
            grouped[key].append(item)
            all_items.append(item)
            break

for key, _, _ in group_defs:
    grouped[key].sort(key=lambda it: it['_sort'])

# 合同誌CSVの読み込み・並び替え
# 合同誌CSVには配置・日程・おしながきの列が無いため、参加者名から本体CSV(rep_to_circle)を
# 逆引きして、そのサークルの配置・おしながき等をこの合同誌の代表として補う。
gohdo_circles = [r for r in read_csv("circle-list gohdo.csv") if r.get('内容', '').strip()]
gohdo_items = []
for row in gohdo_circles:
    content = row.get('内容', '').strip()
    matched = None
    for nm in parse_sanka_names(row.get('参加者', '').strip()):
        matched = rep_to_circle.get(nm.strip())
        if matched:
            break
    matched = matched or {}
    place = matched.get('配置', '').strip()
    oshinagaki = matched.get('おしながき・告知', '').strip()
    tweet_id = extract_tweet_id(oshinagaki)
    if not tweet_id:
        continue
    day_order = {'1日目': 0, '2日目': 1}.get(matched.get('日程', '').strip(), 99)
    gohdo_items.append({
        "name": matched.get('サークル名', '').strip() or content,
        "tw_name": "合同",
        "place": place,
        "tweet_id": tweet_id,
        "tweet_url": oshinagaki,
        "content": content,
        "_sort": (day_order, id_sort_key(row)),
    })
gohdo_items.sort(key=lambda it: it['_sort'])

toc_html = '<nav class="toc"><div class="toc-buttons">'
for key, label, _ in group_defs:
    if grouped[key]:
        toc_html += f'<a class="toc-btn-wrap" href="#{key}"><span class="toc-label">{label}</span></a>'
if gohdo_items:
    toc_html += '<a class="toc-btn-wrap" href="#gohdo"><span class="toc-label">合同誌</span></a>'
toc_html += '</div></nav>'

last_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
_now = datetime.now()
footer_updated = f"{_now.year}/{_now.month}/{_now.day}({WEEKDAYS_JA[_now.weekday()]}) {_now.strftime('%H:%M')}"

page_description = "コミックマーケット108(C108)に参加するIDOLY PRIDE関連サークルのおしながき・告知まとめページです。"
page_title = "コミックマーケット108(C108) おしながき・告知 - IDOLY PRIDE データベース M"
canonical_url = SITE_URL + quote(PAGE_URL, safe='/')
og_image = SITE_URL + 'image/icon.png'
breadcrumb_html = breadcrumb_jsonld([
    ('IDOLY PRIDE データベース M', ''),
    ('コミケ108 おしながき・告知', PAGE_URL),
])

html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="IDOLY PRIDE, コミケ108, C108, コミックマーケット, おしながき, 告知">
    <title>{page_title}</title>
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{page_title}">
    <meta property="og:description" content="{page_description}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:site_name" content="IDOLY PRIDE データベース M">
    <meta property="og:image" content="{og_image}">
    <meta property="og:locale" content="ja_JP">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{page_title}">
    <meta name="twitter:description" content="{page_description}">
    <meta name="twitter:image" content="{og_image}">
    {FONT_PRECONNECT_HTML}
    <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
    <link rel="stylesheet" href="../../common.css">
    <link rel="stylesheet" href="circle-list.css">
    <link rel="shortcut icon" href="../../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../../image/icon.png">
    <link rel="mask-icon" href="../../image/icon.svg">
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    {breadcrumb_html}
</head>
<body>
    <header>
        <div class="banner">
            <div class="banner_title" onclick="location.href='../../index.html'" style="cursor:pointer">コミケ108 おしながき・告知</div>
            <div class="banner_title_phone" onclick="location.href='../../index.html'" style="cursor:pointer">コミケ108 おしながき・告知</div>
        </div>
    </header>
    <nav class="breadcrumb"><a href="../../index.html">トップ</a><span>›</span>コミケ108 おしながき・告知</nav>
    <main>
        <div class="container">
            <div class="info-warning">情報は古くなっている場合や誤りを含んでいることがあります。<br>正確性は保証できませんので、必ず最新情報をご確認ください。</div>
            <div class="last-updated" style="font-size:13px;color:#666;margin-bottom:8px;">最終更新: {last_updated} 次回更新: 2026/8/14予定</div>
            {toc_html}
            <div class="circlelist-link-group">
                <a href="circle-list.html" class="circle-link-btn" style="font-size:16px;">サークル一覧はこちら</a>
                <a href="https://forms.gle/DtRN6apeZxKTmWFQ8" class="circle-link-btn" style="font-size:16px;">サークル様問い合わせ</a>
            </div>
"""

for key, label, _ in group_defs:
    items = grouped[key]
    if not items:
        continue
    html_content += f'<div id="{key}" class="tweet-embed-group-title">{label}</div>'
    html_content += '<div class="tweet-embed-list">'
    for item in items:
        place_id = esc(item['place'])
        html_content += f"""
            <div class="tweet-embed-item">
                <div class="tweet-embed-caption">
                    <a href="circle-list.html#circle-{place_id}" style="color:#3200FF;text-decoration:underline;" target="_blank">{esc(item['place'][3:])} {esc_rich(item['name'])}</a>（{esc(item['tw_name'])}）
                </div>
                <div class="tweet-lazy-embed" data-tweet-id="{esc(item['tweet_id'])}"></div>
            </div>
        """
    html_content += '</div>'

if gohdo_items:
    html_content += '<div id="gohdo" class="tweet-embed-group-title">合同誌</div>'
    html_content += '<div class="tweet-embed-list">'
    for item in gohdo_items:
        place_id = esc(item['place'])
        html_content += f"""
            <div class="tweet-embed-item">
                <div class="tweet-embed-caption">
                    <a href="circle-list.html#circle-{place_id}" style="color:#3200FF;text-decoration:underline;" target="_blank">{esc(item['place'][3:])} {esc_rich(item['name'])}</a>（合同）<br>
                    <span style="font-size:12px;color:#666;">{esc(item['content'])}</span>
                </div>
                <div class="tweet-lazy-embed" data-tweet-id="{esc(item['tweet_id'])}"></div>
            </div>
        """
    html_content += '</div>'

html_content += """
            <p style="margin-top:2em;font-size:13px;color:#666;">
                ※ツイートが表示されない場合は、Twitter側の埋め込み制限や非公開設定等の可能性があります。
            </p>
        </div>

    </main>
    <script>
        window.ALL_TWEET_ITEMS = """ + json.dumps([{k: v for k, v in it.items() if k != '_sort'} for it in all_items], ensure_ascii=False).replace('<', '\\u003c') + """;
    </script>
    <script src="tweet_lazyload.js"></script>
    <footer class="site-footer">最終更新: """ + footer_updated + """ 次回更新: 2026/8/14予定</footer>
</body>
</html>
"""

with open(os.path.join(SCRIPT_DIR, "oshinagaki.html"), "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTMLファイルが生成されました: おしながき・告知ページ")