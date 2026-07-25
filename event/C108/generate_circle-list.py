import csv
import html as html_lib
import os
import re
from datetime import datetime
from urllib.parse import quote

# 実行時のカレントディレクトリに関わらず、常にこのスクリプトと同じ
# フォルダ(event/C108/)でCSVを読み書きするための基準パス
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PAGE_URL = 'event/C108/circle-list.html'

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


def read_csv(path):
    try:
        with open(os.path.join(SCRIPT_DIR, path), encoding='utf-8', newline='') as f:
            return [row for row in csv.DictReader(f)]
    except FileNotFoundError:
        return []

circles = read_csv('circle-list.csv')

group_defs = [
    ("day1", "1日目", lambda r: r.get('日程', '').strip() == '1日目'),
    ("day2", "2日目", lambda r: r.get('日程', '').strip() == '2日目'),
]

grouped = {g[0]: [] for g in group_defs}
for row in circles:
    for key, label, cond in group_defs:
        if cond(row):
            grouped[key].append(row)
            break

def id_sort_key(r):
    try:
        return int(re.sub(r"\D", "", r.get('id', '')) or 0)
    except ValueError:
        return 0

def make_table(rows, anchor, label):
    rows_sorted = sorted(rows, key=id_sort_key)
    # サークル名ごとに複数フラグを集計
    name_to_fukusu = {}
    for r in rows_sorted:
        name = r.get('サークル名', '').strip()
        if name not in name_to_fukusu:
            name_to_fukusu[name] = False
        if r.get('複数', '').strip() == '○':
            name_to_fukusu[name] = True
    rowspans, i = [], 0
    while i < len(rows_sorted):
        name = rows_sorted[i].get('サークル名', '').strip()
        count = 1
        for j in range(i+1, len(rows_sorted)):
            if rows_sorted[j].get('サークル名', '').strip() == name:
                count += 1
            else:
                break
        rowspans.append((i, count))
        i += count
    rowspan_map = {idx: span for idx, span in rowspans if span > 1}
    html = f'<section id="{anchor}-area" class="circlelist-section-anchor"><h3>{esc(label)}</h3>'
    html += '<div class="circle-table-scroll">'
    html += """
    <table class="circle-table">
        <thead>
            <tr>
                <th></th>
                <th>サークル名</th>
                <th>ネットネーム</th>
                <th>配置</th>
                <th>おしながき・告知</th>
                <th>Twitter</th>
                <th>Pixiv</th>
                <th>BOOTH</th>
                <th>メロブ</th>
            </tr>
        </thead>
        <tbody>
    """
    for idx, row in enumerate(rows_sorted):
        name = row.get('サークル名', '').strip()
        joint = row.get('合同', '').strip()
        fukusu = row.get('複数', '').strip()
        # 複数フラグが1つでもあれば【複】を付与
        display_name = name
        if name_to_fukusu.get(name):
            display_name = f"【複】{display_name}"
        if joint == "○":
            display_name = f"【合】{display_name}"
        tw_name = row.get('ネットネーム', '').strip()
        place = row.get('配置', '').strip()
        oshinagaki = row.get('おしながき・告知', '').strip()
        twitter = row.get('Twitter', '').strip()
        pixiv = row.get('Pixiv', '').strip()
        booth = row.get('BOOTH', '').strip()
        melon = row.get('メロブ', '').strip()
        oshinagaki_link = f'<a href="{esc(oshinagaki)}" target="_blank" class="circle-link-btn">おしながき・告知</a>' if oshinagaki else ''
        twitter_link = f'<a href="{esc(twitter)}" target="_blank" class="circle-link-btn">Twitter</a>' if twitter else ''
        pixiv_link = f'<a href="{esc(pixiv)}" target="_blank" class="circle-link-btn">Pixiv</a>' if pixiv else ''
        booth_link = f'<a href="{esc(booth)}" target="_blank" class="circle-link-btn">BOOTH</a>' if booth else ''
        melon_link = f'<a href="{esc(melon)}" target="_blank" class="circle-link-btn">メロブ</a>' if melon else ''
        tr_id = f' id="circle-{esc(place)}" class="circlelist-row-anchor"' if place else ''
        html += f"<tr{tr_id}>"
        copy_btn = f'''<button class="copy-info-btn" data-name="{esc(name)}" data-place="{esc(place)}" data-twitter="{esc(twitter)}">コピー</button>'''
        eval_btn = '''<button class="eval-btn" data-state="-">-</button>'''
        html += f'<td>{copy_btn} {eval_btn}</td>'
        if idx in rowspan_map:
            span = rowspan_map[idx]
            html += f'<td rowspan="{span}">{esc_rich(display_name)}</td>'
        elif idx > 0 and name == rows_sorted[idx-1].get('サークル名', '').strip():
            pass
        else:
            html += f'<td>{esc_rich(display_name)}</td>'
        html += f'<td>{esc(tw_name)}</td><td>{esc(place)}</td><td>{oshinagaki_link}</td><td>{twitter_link}</td><td>{pixiv_link}</td><td>{booth_link}</td><td>{melon_link}</td></tr>\n'
    html += """
        </tbody>
    </table>
    </div>
    </section>
    """
    return html

tables_html = "".join(make_table(grouped[key], key, label) for key, label, _ in group_defs if grouped[key])

# 合同CSVの読み込み・並び替え・HTML生成
gohdo_circles = read_csv("circle-list gohdo.csv")

def gohdo_sort_key(r):
    day_order = {'1日目': 0, '2日目': 1}.get(r.get('日程', '').strip(), 99)
    return (day_order, id_sort_key(r))

gohdo_sorted = sorted(gohdo_circles, key=gohdo_sort_key)

def make_gohdo_table(rows):
    html = '<section id="gohdo-area" class="circlelist-section-anchor"><h3>合同誌</h3>'
    html += '<div class="circle-table-scroll">'
    html += """
    <table class="circle-table">
        <thead>
            <tr>
                <th>サークル名</th>
                <th>内容</th>
                <th>配置</th>
                <th>参加者</th>
                <th>おしながき・告知</th>
            </tr>
        </thead>
        <tbody>
    """
    for row in rows:
        name = row.get('サークル名', '').strip()
        content = row.get('内容', '').strip()
        place = row.get('配置', '').strip()
        sanka = row.get('参加者', '').strip()
        # 参加者をカンマ・読点・スペースで分割し、名前@ユーザー名はまとめてTwitterリンク化
        if sanka:
            import re
            sanka_list = [x.strip() for x in re.split(r'[、,\s]+', sanka) if x.strip()]
            def sanka_to_html(s):
                m = re.match(r'^(.*?)(@([A-Za-z0-9_]{1,15}))$', s)
                if m:
                    disp = m.group(1) + m.group(2)
                    user = m.group(3)
                    return f'<a href="https://twitter.com/{esc(user)}" target="_blank" style="color:#3200FF;">{esc(disp)}</a>'
                return esc(s)
            sanka_html = '<br>'.join([sanka_to_html(x) for x in sanka_list])
        else:
            sanka_html = ''
        oshinagaki = row.get('おしながき・告知', '').strip()
        oshinagaki_link = f'<a href="{esc(oshinagaki)}" target="_blank" class="circle-link-btn">おしながき・告知</a>' if oshinagaki else ''
        html += f"<tr><td>{esc(name)}</td><td>{esc(content)}</td><td>{esc(place)}</td><td style='text-align:left;font-size:13px;'>{sanka_html}</td><td>{oshinagaki_link}</td></tr>\n"
    html += """
        </tbody>
    </table>
    </div>
    </section>
    """
    return html

# 目次HTML生成
toc_html = '<nav class="toc"><div class="toc-buttons">'
for key, label, _ in group_defs:
    if grouped[key]:
        toc_html += f'<a class="toc-btn-wrap" href="#{key}-area"><span class="toc-label">{label}</span></a>'
if gohdo_sorted:
    toc_html += '<a class="toc-btn-wrap" href="#gohdo-area"><span class="toc-label">合同誌</span></a>'
toc_html += '</div></nav>'

if gohdo_sorted:
    tables_html += make_gohdo_table(gohdo_sorted)

last_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
_now = datetime.now()
footer_updated = f"{_now.year}/{_now.month}/{_now.day}({WEEKDAYS_JA[_now.weekday()]}) {_now.strftime('%H:%M')}"

page_description = "コミックマーケット108(C108)に参加するIDOLY PRIDE関連サークルの一覧ページです。"
page_title = "コミックマーケット108(C108) サークル - IDOLY PRIDE データベース M"
canonical_url = SITE_URL + quote(PAGE_URL, safe='/')
og_image = SITE_URL + 'image/icon.png'

html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="IDOLY PRIDE, コミケ108, C108, コミックマーケット, サークル一覧">
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
    <script src="circle-list.js"></script>
    <link rel="shortcut icon" href="../../image/icon.ico">
    <link rel="icon" type="image/png" sizes="180x180" href="../../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../../image/icon.png">
    <link rel="mask-icon" href="../../image/icon.svg">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="banner">
            <div class="banner_title" onclick="location.href='../../index.html'" style="cursor:pointer">コミケ108 サークル</div>
            <div class="banner_title_phone" onclick="location.href='../../index.html'" style="cursor:pointer">コミケ108 サークル</div>
        </div>
    </header>
    <nav class="breadcrumb"><a href="../../index.html">トップ</a><span>›</span>コミケ108 サークル</nav>
    <main>
        <div class="container">
            <div class="info-warning">非公式のページであり、情報は公式ページやTwitterからの引用になります。<br>情報の正確性は保証できませんので、必ず公式情報をご確認ください。</div>
            <div class="last-updated" style="font-size:13px;color:#666;margin-bottom:8px;">最終更新: {last_updated}</div>
            {toc_html}
            <div class="circlelist-link-group">
                <a href="oshinagaki.html" class="circle-link-btn" style="font-size:16px;">おしながき・告知まとめはこちら</a>
                <a href="https://forms.gle/DtRN6apeZxKTmWFQ8" class="circle-link-btn" style="font-size:16px;">サークル様問い合わせ</a>
            </div>
            <div class="info-text">
                コピーを押すと、サークル情報をクリップボードにコピーできます。
                <br>「-」を押すと、サークルの評価状態が切り替わります。
                <br>合同サークルには、サークル名の先頭に【合】を付けています。
                <br>複数の方が同じサークル名で個別に参加されている場合に【複】を付けています。
            </div>
            {tables_html}
        </div>
    </main>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <footer class="site-footer">最終更新: {footer_updated}</footer>
</body>
</html>
"""

with open(os.path.join(SCRIPT_DIR, "circle-list.html"), "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTMLファイルが生成されました: サークルページ")