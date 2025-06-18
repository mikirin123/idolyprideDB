import csv
import re
from collections import defaultdict

with open('circlelist.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    circles = [row for row in reader]

# グループ定義
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

# グループ分け
grouped = {g[0]: [] for g in group_defs}
for row in circles:
    place = row.get('配置', '').strip()
    for key, label, cond in group_defs:
        if cond(place):
            grouped[key].append(row)
            break

# 目次HTML
toc_html = '<nav class="toc"><div class="toc-buttons">'
for key, label, _ in group_defs:
    if grouped[key]:
        toc_html += f'<div class="toc-btn-wrap" onclick="location.href=\'#{key}-area\'"><span class="toc-label">{label}</span></div>'
toc_html += '</div></nav>'

# テーブルHTML
def make_table(rows, anchor, label):
    # サークル名・合同の連続行をrowspanで結合
    rows_sorted = sorted(rows, key=lambda r: r.get('配置', ''))
    rowspans = []
    i = 0
    while i < len(rows_sorted):
        name = rows_sorted[i].get('サークル名', '').strip()
        joint = rows_sorted[i].get('合同', '').strip()
        count = 1
        for j in range(i+1, len(rows_sorted)):
            if rows_sorted[j].get('サークル名', '').strip() == name and rows_sorted[j].get('合同', '').strip() == joint:
                count += 1
            else:
                break
        rowspans.append((i, count))
        i += count
    rowspan_map = {}
    for idx, span in rowspans:
        if span > 1:
            rowspan_map[idx] = span

    html = f'<section id="{anchor}-area" style="scroll-margin-top: 90px;"><h3>{label}</h3>'
    html += '<div class="circle-table-scroll">'  # 追加
    html += """
    <table class="circle-table">
        <thead>
            <tr>
                <th>サークル名</th>
                <th>合同</th>
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
        tw_name = row.get('ネットネーム', '').strip()
        place = row.get('配置', '').strip()
        oshinagaki = row.get('おしながき・告知', '').strip()
        twitter = row.get('Twitter', '').strip()
        pixiv = row.get('Pixiv', '').strip()
        booth = row.get('BOOTH', '').strip()
        melon = row.get('メロブ', '').strip()
        oshinagaki_link = f'<a href="{oshinagaki}" target="_blank" class="circle-link-btn">おしながき・告知</a>' if oshinagaki else ''
        twitter_link = f'<a href="{twitter}" target="_blank" class="circle-link-btn">Twitter</a>' if twitter else ''
        pixiv_link = f'<a href="{pixiv}" target="_blank" class="circle-link-btn">Pixiv</a>' if pixiv else ''
        booth_link = f'<a href="{booth}" target="_blank" class="circle-link-btn">BOOTH</a>' if booth else ''
        melon_link = f'<a href="{melon}" target="_blank" class="circle-link-btn">メロブ</a>' if melon else ''
        html += "<tr>"
        if idx in rowspan_map:
            span = rowspan_map[idx]
            html += f'<td rowspan="{span}">{name}</td>'
            html += f'<td rowspan="{span}">{joint}</td>'
        elif idx > 0 and name == rows_sorted[idx-1].get('サークル名', '').strip() and joint == rows_sorted[idx-1].get('合同', '').strip():
            pass
        else:
            html += f'<td>{name}</td>'
            html += f'<td>{joint}</td>'
        html += f'<td>{tw_name}</td>'
        html += f'<td>{place}</td>'
        html += f'<td>{oshinagaki_link}</td>'
        html += f'<td>{twitter_link}</td>'
        html += f'<td>{pixiv_link}</td>'
        html += f'<td>{booth_link}</td>'
        html += f'<td>{melon_link}</td>'
        html += "</tr>\n"
    html += """
        </tbody>
    </table>
    </div>"""  # 追加
    html += """
    </section>
    """
    return html

tables_html = ""
for key, label, _ in group_defs:
    if grouped[key]:
        tables_html += make_table(grouped[key], key, label)

html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>はちはじ'25 サークル一覧</title>
    <link rel="stylesheet" href="circlelist.css">
    <script src="circlelist.js"></script>
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
</head>
<body>
    <header>
        <div class="banner">
            <div class="banner_title">はちはじ'25 サークル一覧</div>
            <div class="banner_title_phone">サークル一覧</div>
            <a href="../../index.html" class="back-button">トップに戻る</a>
        </div>
    </header>
    <main>
        <div class="container">
            {toc_html}
            <div style="margin-bottom:18px;">
                <a href="oshinagaki.html" class="circle-link-btn" style="font-size:16px;">おしながき・告知ツイート一覧はこちら</a>
                <a href="https://kiyoshimo.wixsite.com/idolypride/%E8%A4%87%E8%A3%BD-%E3%82%B5%E3%83%BC%E3%82%AF%E3%83%AB%E9%85%8D%E7%BD%AE" class="circle-link-btn" style="font-size:16px;">サークルカット・配置図(公式ページ)はこちら</a>
            </div>
            <h2>サークル一覧</h2>
            {tables_html}
        </div>
    </main>
    <button id="scrollToTopBtn" onclick="scrollToTop()">ページ上部へ</button>
</body>
</html>
"""

output_path = "circlelist.html"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTMLファイルが生成されました: サークル一覧ページ")