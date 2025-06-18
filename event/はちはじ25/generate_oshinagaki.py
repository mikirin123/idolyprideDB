import csv
import re

def extract_tweet_id(url):
    # x.com or twitter.com のツイートURLからIDを抽出
    m = re.search(r"(?:twitter\.com|x\.com)/[^/]+/status/(\d+)", url)
    return m.group(1) if m else None

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
    oshinagaki = row.get('おしながき・告知', '').strip()
    tweet_id = extract_tweet_id(oshinagaki)
    if not tweet_id:
        continue
    for key, label, cond in group_defs:
        if cond(place):
            grouped[key].append({
                "name": row.get('サークル名', '').strip(),
                "tw_name": row.get('ネットネーム', '').strip(),
                "place": place,
                "tweet_id": tweet_id,
                "tweet_url": oshinagaki,
            })
            break

# 目次HTML
toc_html = '<nav class="toc"><div class="toc-buttons">'
for key, label, _ in group_defs:
    if grouped[key]:
        toc_html += f'<div class="toc-btn-wrap" onclick="location.href=\'#{key}\'"><span class="toc-label">{label}</span></div>'
toc_html += '</div></nav>'

# --- ここからf-stringでtoc_htmlを展開 ---
html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>はちはじ'25 おしながき・告知ツイート一覧</title>
    <link rel="stylesheet" href="circlelist.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    <style>
        .tweet-embed-list {{ display: flex; flex-wrap: wrap; gap: 24px 10px; }}
        .tweet-embed-item {{
            width: 320px;
            min-width: 220px;
            max-width: 100%;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(50,0,255,0.06);
            padding: 6px 6px 2px 6px;
            margin-bottom: 6px;
        }}
        .tweet-embed-caption {{
            font-size: 14px;
            font-weight: bold;
            color: #3200FF;
            margin-bottom: 4px;
            word-break: break-all;
        }}
        @media (max-width: 900px) {{
            .tweet-embed-list {{ flex-direction: column; gap: 14px 0; }}
            .tweet-embed-item {{ width: 98vw; min-width: 0; }}
        }}
        @media (max-width: 600px) {{
            body {{
                min-width: 100vw;
                padding: 0;
                margin: 0;
                background: #f8f8f8;
            }}
            .container {{
                padding: 6px 2px 10px 2px;
                margin: 60px 0 0 0;
                width: 100vw;
                border-radius: 0;
                box-shadow: none;
            }}
            .tweet-embed-list {{
                gap: 8px 0;
                padding: 0;
            }}
            .tweet-embed-item {{
                width: 99vw;
                min-width: 0;
                max-width: 100vw;
                margin-bottom: 6px;
                padding: 4px 1vw 1px 1vw;
                border-radius: 0;
                box-shadow: none;
            }}
            .tweet-embed-caption {{
                font-size: 12px;
                margin-bottom: 2px;
                padding-left: 2px;
                padding-right: 2px;
            }}
            .tweet-embed-group-title {{
                font-size: 16px;
                margin: 22px 0 5px 0;
                scroll-margin-top: 65px;
            }}
            h2 {{
                font-size: 16px;
                margin-top: 8px;
            }}
        }}
        .tweet-embed-group-title {{
            font-size: 18px;
            color: #3200FF;
            font-weight: bold;
            margin: 30px 0 8px 0;
            scroll-margin-top: 90px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="banner">
            <div class="banner_title">おしながき・告知ツイート一覧</div>
            <div class="banner_title_phone">おしながき・告知ツイート一覧</div>
            <a href="circlelist.html" class="back-button">サークル一覧に戻る</a>
        </div>
    </header>
    <main>
        <div class="container">
            {toc_html}
            <h2>おしながき・告知ツイート埋め込み一覧</h2>
"""

for key, label, _ in group_defs:
    items = grouped[key]
    if not items:
        continue
    html_content += f'<div id="{key}" class="tweet-embed-group-title">{label}</div>'
    html_content += '<div class="tweet-embed-list">'
    for item in items:
        html_content += f"""
            <div class="tweet-embed-item">
                <div class="tweet-embed-caption">{item['place']} {item['name']}（{item['tw_name']}）</div>
                <blockquote class="twitter-tweet">
                    <a href="https://twitter.com/i/status/{item['tweet_id']}"></a>
                </blockquote>
            </div>
        """
    html_content += '</div>'

html_content += """
            <p style="margin-top:2em;font-size:13px;color:#666;">
                ※ツイートが表示されない場合は、X(Twitter)側の埋め込み制限や非公開設定等の可能性があります。
            </p>
        </div>
    </main>
</body>
</html>
"""

output_path = "oshinagaki.html"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTMLファイルが生成されました: おしながき・告知ツイート埋め込み一覧")
