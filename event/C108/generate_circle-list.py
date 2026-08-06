import csv
import html as html_lib
import json
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


def read_csv(path):
    try:
        with open(os.path.join(SCRIPT_DIR, path), encoding='utf-8', newline='') as f:
            return [row for row in csv.DictReader(f)]
    except FileNotFoundError:
        return []


def id_sort_key(r):
    try:
        return int(re.sub(r"\D", "", r.get('circle-id', '')) or 0)
    except ValueError:
        return 0


def parse_sanka_names(sanka):
    """参加者欄(例: 'みちゃん|st_michan:PURIN|puririn778:')を個人名のリストに分割する。
    '|'以降のTwitter IDは表記ゆれとして取り除き、代表者名との突き合わせに使う。"""
    if not sanka:
        return []
    names = []
    for s in sanka.split(':'):
        s = s.strip()
        if not s:
            continue
        name, _, _uid = s.partition('|')
        names.append(name.strip())
    return names


def sanka_to_html(s):
    """参加者欄の1エントリ('名前|Twitter ID')をリンク付きHTMLに変換する。IDがなければ名前だけを表示する。"""
    name, sep, uid = s.partition('|')
    name = name.strip()
    uid = uid.strip()
    if sep and uid:
        return f'<a href="https://twitter.com/{esc(uid)}" target="_blank" style="color:#3200FF;text-decoration:none;">{esc(name)}</a>'
    return esc(name)


circles = [r for r in read_csv('circle-list.csv') if r.get('サークル名', '').strip()]

# 合同誌CSVの読み込み・並び替え(サークル一覧の各行から合同誌バッジでリンクするため、先に読み込む)
gohdo_circles = [r for r in read_csv("circle-list gohdo.csv") if r.get('内容', '').strip()]
gohdo_sorted = sorted(gohdo_circles, key=id_sort_key)

# circle-idから本体CSVの行を逆引きするためのマップ(合同誌テーブルのサークル名・配置等を補うため)
circles_by_circle_id = {}
for r in circles:
    cid = r.get('circle-id', '').strip()
    name = r.get('サークル名', '').strip()
    if not cid or not name:
        continue
    rows = circles_by_circle_id.setdefault(cid, [])
    if name not in [x.get('サークル名', '').strip() for x in rows]:
        rows.append(r)

# 代表者名 → 合同誌テーブルの該当行アンカー、のマップ(合同誌バッジのリンク先を決めるため)
name_to_gohdo_anchor = {}
for idx, row in enumerate(gohdo_sorted):
    for nm in parse_sanka_names(row.get('参加者', '').strip()):
        name_to_gohdo_anchor.setdefault(nm.strip(), f'gohdo-{idx}')

# 配置の先頭3文字でグルーピングする(circle-id順に現れた並びをそのままセクション順にする)
circles_by_id = sorted(circles, key=id_sort_key)
group_order = []
grouped = {}
for row in circles_by_id:
    prefix = row.get('配置', '').strip()[:3]
    if prefix not in grouped:
        grouped[prefix] = []
        group_order.append(prefix)
    grouped[prefix].append(row)

group_defs = [(f'place-{prefix}', prefix) for prefix in group_order]

def make_table(rows, anchor, label):
    rows_sorted = sorted(rows, key=id_sort_key)
    # サークル名ごとに合同誌バッジのリンク先を集計
    name_to_gohdo_anchors = {}
    for r in rows_sorted:
        name = r.get('サークル名', '').strip()
        if r.get('合同誌', '').strip() == '○':
            anchor_id = name_to_gohdo_anchor.get(r.get('代表者', '').strip(), 'gohdo-area')
            anchors = name_to_gohdo_anchors.setdefault(name, [])
            if anchor_id not in anchors:
                anchors.append(anchor_id)
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
            </tr>
        </thead>
        <tbody>
    """
    for idx, row in enumerate(rows_sorted):
        name = row.get('サークル名', '').strip()
        display_name = name
        content = row.get('内容', '').strip()
        content_html = f'<br><span class="circle-content-note">{esc(content)}</span>' if content else ''
        gohdo_badges = name_to_gohdo_anchors.get(name, [])
        gohdo_badge_html = ('<br>' if gohdo_badges else '') + ''.join(
            f'<a href="#{a}" class="circle-link-btn gohdo-badge-link">合同誌</a>'
            for a in gohdo_badges
        )
        tw_name = row.get('代表者', '').strip()
        place = row.get('配置', '').strip()
        place_display = place[3:]
        oshinagaki = row.get('おしながき・告知', '').strip()
        twitter = row.get('Twitter', '').strip()
        oshinagaki_link = f'<a href="{esc(oshinagaki)}" target="_blank" class="circle-link-btn">おしながき・告知</a>' if oshinagaki else ''
        twitter_link = f'<a href="{esc(twitter)}" target="_blank" class="circle-link-btn">Twitter</a>' if twitter else ''
        tr_id = f' id="circle-{esc(place)}" class="circlelist-row-anchor"' if place else ''
        html += f"<tr{tr_id}>"
        copy_btn = f'''<button class="copy-info-btn" data-name="{esc(name)}" data-place="{esc(place)}" data-twitter="{esc(twitter)}">コピー</button>'''
        eval_btn = '''<button class="eval-btn" data-state="-">-</button>'''
        html += f'<td>{copy_btn} {eval_btn}</td>'
        if idx in rowspan_map:
            span = rowspan_map[idx]
            html += f'<td rowspan="{span}">{esc_rich(display_name)}{content_html}{gohdo_badge_html}</td>'
        elif idx > 0 and name == rows_sorted[idx-1].get('サークル名', '').strip():
            pass
        else:
            html += f'<td>{esc_rich(display_name)}{content_html}{gohdo_badge_html}</td>'
        html += f'<td>{esc(tw_name)}</td><td>{esc(place_display)}</td><td>{oshinagaki_link}</td><td>{twitter_link}</td></tr>\n'
    html += """
        </tbody>
    </table>
    </div>
    </section>
    """
    return html

tables_html = "".join(make_table(grouped[label], anchor, label) for anchor, label in group_defs if grouped[label])

def circle_ref_html(r):
    """本体CSVの行から、サークル一覧側の該当行へリンクするサークル名セルを作る。"""
    name = r.get('サークル名', '').strip()
    place = r.get('配置', '').strip()
    if place:
        return f'<a href="#circle-{esc(place)}" style="color:#3200FF;text-decoration:none;">{esc(name)}</a>'
    return esc(name)


def make_gohdo_table(rows, circles_by_circle_id):
    html = '<section id="gohdo-area" class="circlelist-section-anchor"><h3>合同誌</h3>'
    html += '<div class="circle-table-scroll">'
    html += """
    <table class="circle-table">
        <thead>
            <tr>
                <th>サークル名</th>
                <th>内容</th>
                <th>参加者</th>
            </tr>
        </thead>
        <tbody>
    """
    for idx, row in enumerate(rows):
        content = row.get('内容', '').strip()
        sanka = row.get('参加者', '').strip()
        # circle-idから本体CSVの行を逆引きし、サークル名・配置・おしながき等を補う
        matched_rows = circles_by_circle_id.get(row.get('circle-id', '').strip(), [])
        if matched_rows:
            name_cell = '<br>'.join(circle_ref_html(r) for r in matched_rows)
        else:
            name_cell = esc(content)
        if sanka:
            sanka_list = [x.strip() for x in sanka.split(':') if x.strip()]
            sanka_html = '<br>'.join(sanka_to_html(x) for x in sanka_list)
        else:
            sanka_html = ''
        html += f"<tr id=\"gohdo-{idx}\"><td>{name_cell}</td><td>{esc(content)}</td><td style='text-align:left;font-size:13px;'>{sanka_html}</td></tr>\n"
    html += """
        </tbody>
    </table>
    </div>
    </section>
    """
    return html

# 目次HTML生成
toc_html = '<nav class="toc"><div class="toc-buttons">'
for anchor, label in group_defs:
    if grouped[label]:
        toc_html += f'<a class="toc-btn-wrap" href="#{anchor}-area"><span class="toc-label">{label}</span></a>'
if gohdo_sorted:
    toc_html += '<a class="toc-btn-wrap" href="#gohdo-area"><span class="toc-label">合同誌</span></a>'
toc_html += '</div></nav>'

if gohdo_sorted:
    tables_html += make_gohdo_table(gohdo_sorted, circles_by_circle_id)

last_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
_now = datetime.now()
footer_updated = f"{_now.year}/{_now.month}/{_now.day}({WEEKDAYS_JA[_now.weekday()]}) {_now.strftime('%H:%M')}"

page_description = "コミックマーケット108(C108)に参加するIDOLY PRIDE関連サークルの一覧ページです。"
page_title = "コミックマーケット108(C108) サークル - IDOLY PRIDE データベース M"
canonical_url = SITE_URL + quote(PAGE_URL, safe='/')
og_image = SITE_URL + 'image/icon.png'
breadcrumb_html = breadcrumb_jsonld([
    ('IDOLY PRIDE データベース M', ''),
    ('コミケ108 サークル', PAGE_URL),
])

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
    <meta property="og:locale" content="ja_JP">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{page_title}">
    <meta name="twitter:description" content="{page_description}">
    <meta name="twitter:image" content="{og_image}">
    {FONT_PRECONNECT_HTML}
    <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
    <link rel="stylesheet" href="../../common.css">
    <link rel="stylesheet" href="circle-list.css">
    <script src="circle-list.js"></script>
    <link rel="shortcut icon" href="../../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../../image/icon.png">
    <link rel="mask-icon" href="../../image/icon.svg">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    {breadcrumb_html}
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
            <div class="info-warning">情報は古くなっている場合や誤りを含んでいることがあります。<br>正確性は保証できませんので、必ず最新情報をご確認ください。<br><br>サークル名の下に記載している内容は、実際の活動内容と異なる場合があります。参考程度にご覧ください。<br>合同誌の情報は正確でない可能性が高く、把握し次第更新していきます。</div>
            <div class="last-updated" style="font-size:13px;color:#666;margin-bottom:8px;">最終更新: {last_updated} 次回更新: 2026-08-01予定</div>
            {toc_html}
            <div class="circlelist-link-group">
                <a href="oshinagaki.html" class="circle-link-btn" style="font-size:16px;">おしながき・告知まとめはこちら</a>
                <a href="https://forms.gle/DtRN6apeZxKTmWFQ8" class="circle-link-btn" style="font-size:16px;">サークル様問い合わせ</a>
            </div>
            <div class="info-text">
                コピーを押すと、サークル情報をクリップボードにコピーできます。
                <br>「-」を押すと、サークルの評価状態が切り替わります。
                <br>合同誌に参加しているサークルには、「合同誌」バッジを表示しています(押すと合同誌の詳細に移動します)。
            </div>
            {tables_html}
        </div>
    </main>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <footer class="site-footer">最終更新: {footer_updated} 次回更新: 2026-08-01予定</footer>
</body>
</html>
"""

with open(os.path.join(SCRIPT_DIR, "circle-list.html"), "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTMLファイルが生成されました: サークルページ")
