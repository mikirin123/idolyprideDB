from utils import write_page
import os
import json
from db import load_characters

def generate_html():
    characters = load_characters()

    cards = []
    for c in characters:
        power = (int(int(c[10]) * 0.5) + int(int(c[11]) * 0.5) +
                 int(int(c[12]) * 0.5) + int(int(c[13]) * 0.8) + 500)
        cards.append({
            'char': c[2],
            'card': c[3],
            'key': f'{c[2]} {c[3]}',
            'incomplete': c[0] == '★',
            'rarity': c[4],
            'trend': c[5],
            'type': c[6],
            'skills_comp': c[7],
            'vocal': int(c[10]),
            'dance': int(c[11]),
            'visual': int(c[12]),
            'stamina': int(c[13]),
            'power': power,
            'skill1_name': c[14],
            'skill1_effect': c[15],
            'skill2_name': c[16],
            'skill2_effect': c[17],
            'skill3_name': c[18],
            'skill3_effect': c[19],
            'awakening_name': c[20],
            'awakening_effect': c[21],
            'yell': c[22],
            'obtain': c[23],
            'release_date': c[24],
        })

    # </script> のようなシーケンスがカードデータ内に含まれていても
    # <script> タグが途中で閉じられないようにエスケープする
    cards_json = json.dumps(cards, ensure_ascii=False).replace('<', '\\u003c')

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="IDOLY PRIDEのアイドル比較ページです。最大5枚のカードを並べてステータス・スキルを比較できます。">
    <meta name="keywords" content="IDOLY PRIDE, アイドル比較, ステータス, スキル, データベース">
    <title>アイドル比較 - IDOLY PRIDE データベース M</title>
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="compare.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - アイドル比較</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">アイドル比較</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>アイドル比較</nav>
    <div class="selector-container">
        <h2>比較するカードを選んでください（最大5枚）</h2>
        <div class="card-selectors">
            <div class="card-selector">
                <label for="combo-1-input">カード 1</label>
                <div class="combobox" id="combo-1"></div>
            </div>
            <div class="card-selector">
                <label for="combo-2-input">カード 2</label>
                <div class="combobox" id="combo-2"></div>
            </div>
            <div class="card-selector">
                <label for="combo-3-input">カード 3（任意）</label>
                <div class="combobox" id="combo-3" data-optional="true"></div>
            </div>
            <div class="card-selector">
                <label for="combo-4-input">カード 4（任意）</label>
                <div class="combobox" id="combo-4" data-optional="true"></div>
            </div>
            <div class="card-selector">
                <label for="combo-5-input">カード 5（任意）</label>
                <div class="combobox" id="combo-5" data-optional="true"></div>
            </div>
        </div>
        <div class="compare-actions">
            <button id="copy-url-btn" onclick="copyCompareUrl()" class="copy-url-btn">URLをコピー</button>
            <span id="copy-url-msg" class="copy-url-msg" style="display:none">コピーしました！</span>
        </div>
    </div>
    <div id="compare-result" class="compare-result">
        <p class="hint">カードを2枚以上選択してください。</p>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script>
    const ALL_CARDS = {cards_json};
    </script>
    <script src="compare.js"></script>
</body>
</html>'''

    os.makedirs('content', exist_ok=True)
    write_page('content/compare.html', html_content)

if __name__ == '__main__':
    generate_html()
    print('HTMLファイルが生成されました: アイドル比較')
