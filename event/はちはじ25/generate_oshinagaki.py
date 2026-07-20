import csv
import html as html_lib
import os
import re
import json
from datetime import datetime
from urllib.parse import quote

# 実行時のカレントディレクトリに関わらず、常にこのスクリプトと同じ
# フォルダ(event/はちはじ25/)でCSVを読み書きするための基準パス
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PAGE_URL = 'event/はちはじ25/oshinagaki.html'

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

circles = read_csv('circle-list.csv')

group_defs = [
    ("star1_10", "星01～10", lambda p: p.startswith("星") and 1 <= int(re.sub(r"\D", "", p) or 0) <= 10),
    ("star11_20", "星11～20", lambda p: p.startswith("星") and 11 <= int(re.sub(r"\D", "", p) or 0) <= 20),
    ("star21_34", "星21～34", lambda p: p.startswith("星") and 21 <= int(re.sub(r"\D", "", p) or 0) <= 34),
    ("mi1_10", "見01～10", lambda p: p.startswith("見") and 1 <= int(re.sub(r"\D", "", p) or 0) <= 10),
    ("mi11_20", "見11～20", lambda p: p.startswith("見") and 11 <= int(re.sub(r"\D", "", p) or 0) <= 20),
    ("mi21_26", "見21～26", lambda p: p.startswith("見") and 21 <= int(re.sub(r"\D", "", p) or 0) <= 26),
    ("shi1_10", "市01～10", lambda p: p.startswith("市") and 1 <= int(re.sub(r"\D", "", p) or 0) <= 10),
    ("shi11_20", "市11～20", lambda p: p.startswith("市") and 11 <= int(re.sub(r"\D", "", p) or 0) <= 20),
    ("shi21_26", "市21～26", lambda p: p.startswith("市") and 21 <= int(re.sub(r"\D", "", p) or 0) <= 26),
]

grouped = {g[0]: [] for g in group_defs}
all_items = []
for row in circles:
    place = row.get('配置', '').strip()
    oshinagaki = row.get('おしながき・告知', '').strip()
    tweet_id = extract_tweet_id(oshinagaki)
    if not tweet_id:
        continue
    is_goudou = row.get('合同', '').strip() == '○'
    is_fukusu = row.get('複数', '').strip() == '○'
    tw_name = "合同" if is_goudou else row.get('ネットネーム', '').strip()
    # サークル名の先頭に【複】を付与
    name = row.get('サークル名', '').strip()
    if is_fukusu:
        name = f"【複】{name}"
    for key, label, cond in group_defs:
        if cond(place):
            item = {
                "name": name,
                "tw_name": tw_name,
                "place": place,
                "tweet_id": tweet_id,
                "tweet_url": oshinagaki,
            }
            grouped[key].append(item)
            all_items.append(item)
            break

# 合同CSVの読み込み・グループ化
gohdo_circles = read_csv("circle-list gohdo.csv")
gohdo_grouped = {}
for row in gohdo_circles:
    place = row.get('配置', '').strip()
    oshinagaki = row.get('おしながき・告知', '').strip()
    tweet_id = extract_tweet_id(oshinagaki)
    if not tweet_id:
        continue
    if place not in gohdo_grouped:
        gohdo_grouped[place] = []
    gohdo_grouped[place].append({
        "name": row.get('サークル名', '').strip(),
        "tw_name": "合同",
        "place": place,
        "tweet_id": tweet_id,
        "tweet_url": oshinagaki,
        "content": row.get('内容', '').strip(),
    })
gohdo_places_sorted = sorted(gohdo_grouped.keys(), key=lambda p: (
    {'星': 0, '見': 1, '市': 2}.get(p[:1], 99), int(re.sub(r'\D', '', p) or 0))
)

toc_html = '<nav class="toc"><div class="toc-buttons">'
for key, label, _ in group_defs:
    if grouped[key]:
        toc_html += f'<a class="toc-btn-wrap" href="#{key}"><span class="toc-label">{label}</span></a>'
if gohdo_grouped:
    toc_html += '<a class="toc-btn-wrap" href="#gohdo"><span class="toc-label">合同誌</span></a>'
toc_html += '</div></nav>'

last_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
_now = datetime.now()
footer_updated = f"{_now.year}/{_now.month}/{_now.day}({WEEKDAYS_JA[_now.weekday()]}) {_now.strftime('%H:%M')}"

page_description = "2025年に開催されるIDOLY PRIDEオンリーイベント『八景から始まる物語』stage3、通称『はちはじ3』の参加サークルのおしながき・告知まとめページです。"
page_title = "八景から始まる物語 stage3 おしながき・告知 - IDOLY PRIDE データベース M"
canonical_url = SITE_URL + quote(PAGE_URL, safe='/')
og_image = SITE_URL + 'image/icon.png'

html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="IDOLY PRIDE, はちはじ3, 八景から始まる物語, おしながき, 告知">
    <title>{page_title}</title>
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{page_title}">
    <meta property="og:description" content="{page_description}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:site_name" content="IDOLY PRIDE データベース M">
    <meta property="og:image" content="{og_image}">
    <meta name="twitter:card" content="summary">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
    <link rel="stylesheet" href="circle-list.css">
    <link rel="shortcut icon" href="../../image/icon.ico">
    <link rel="icon" type="image/png" sizes="180x180" href="../../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../../image/icon.png">
    <link rel="mask-icon" href="../../image/icon.svg">
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="banner">
            <div class="banner_title" onclick="location.href='../../index.html'" style="cursor:pointer">おしながき・告知</div>
            <div class="banner_title_phone" onclick="location.href='../../index.html'" style="cursor:pointer">おしながき・告知</div>
            <a href="javascript:history.back()" class="back-button">戻る</a>
        </div>
    </header>
    <nav class="breadcrumb"><a href="../../index.html">トップ</a><span>›</span>おしながき・告知</nav>
    <main>
        <div class="container">
            <div class="info-warning">非公式のページであり、情報は公式ページやTwitterからの引用になります。<br>情報の正確性は保証できませんので、必ず公式情報をご確認ください。</div>
            <div class="last-updated" style="font-size:13px;color:#666;margin-bottom:8px;">最終更新: {last_updated} はちはじ3お疲れ様でした！</div>
            {toc_html}
            <div class="circlelist-link-group">
                <a href="circle-list.html" class="circle-link-btn" style="font-size:16px;">サークル一覧はこちら</a>
                <a href="https://kiyoshimo.wixsite.com/idolypride/%E8%A4%87%E8%A3%BD-%E3%82%B5%E3%83%BC%E3%82%AF%E3%83%AB%E9%85%8D%E7%BD%AE" class="circle-link-btn" style="font-size:16px;">サークルカット・配置図(公式ページ)はこちら</a>
                <a href="https://forms.gle/DtRN6apeZxKTmWFQ8" class="circle-link-btn" style="font-size:16px;">サークル様問い合わせ</a>
            </div>
            <div id="random-pickup" class="tweet-embed-group-title random-pickup-margin">ランダムピックアップ</div>
            <div id="random-pickup-list" class="tweet-embed-list"></div>
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
                    <a href="circle-list.html#circle-{place_id}" style="color:#3200FF;text-decoration:underline;" target="_blank">{esc(item['place'])} {esc_rich(item['name'])}</a>（{esc(item['tw_name'])}）
                </div>
                <div class="tweet-lazy-embed" data-tweet-id="{esc(item['tweet_id'])}"></div>
            </div>
        """
    html_content += '</div>'

if gohdo_grouped:
    html_content += '<div id="gohdo" class="tweet-embed-group-title">合同誌</div>'
    html_content += '<div class="tweet-embed-list">'
    for place in gohdo_places_sorted:
        for item in gohdo_grouped[place]:
            place_id = esc(item['place'])
            html_content += f"""
                <div class="tweet-embed-item">
                    <div class="tweet-embed-caption">
                        <a href="circle-list.html#circle-{place_id}" style="color:#3200FF;text-decoration:underline;" target="_blank">{esc(item['place'])} {esc_rich(item['name'])}</a>（合同）<br>
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
        window.ALL_TWEET_ITEMS = """ + json.dumps(all_items, ensure_ascii=False).replace('<', '\\u003c') + """;
    </script>
    <script src="random_pickup.js"></script>
    <script src="tweet_lazyload.js"></script>
    <footer class="site-footer">最終更新: """ + footer_updated + """</footer>
</body>
</html>
"""

with open(os.path.join(SCRIPT_DIR, "oshinagaki.html"), "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTMLファイルが生成されました: おしながき・告知ページ")