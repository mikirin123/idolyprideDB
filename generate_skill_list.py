from utils import write_page, esc, esc_rich, build_char_options_html, seo_meta_html, breadcrumb_jsonld, FONT_PRECONNECT_HTML
import os
import re
from db import load_characters

def extract_ct(effect):
    """効果テキストから CT 値を抽出する。CT:5 や CT：5 に対応。"""
    m = re.search(r'CT[：:](\d+)', effect or '')
    return int(m.group(1)) if m else None

def detect_skill_type(name):
    """スキル名先頭の【】からスキル種別(SP/A/P)を取得する。"""
    m = re.match(r'^【(.+?)】', name or '')
    return m.group(1) if m else 'A'

def generate_html():
    characters = load_characters()

    rows_html = ''
    for char in characters:
        char_name = char[2]
        card_name = char[3]
        icon_path = f'../image/idol/{char_name} {card_name}.webp'
        detail_path = f'../detail/{char_name} {card_name}.html'
        row_class = ' class="data-incomplete"' if char[0] == '★' else ''

        skills = [
            ('スキル1', char[14], char[15]),
            ('スキル2', char[16], char[17]),
        ]
        if char[18]:
            skills.append(('スキル3', char[18], char[19]))
        if char[20]:
            skills.append(('覚醒スキル', char[20], char[21]))

        trend = char[5]
        char_type = char[6]

        for slot, name, effect in skills:
            if not name:
                continue
            skill_type = detect_skill_type(name)
            ct_val = extract_ct(effect)
            ct_data = str(ct_val) if ct_val is not None else ''
            rows_html += f'''            <tr{row_class} data-char="{esc(char_name)}" data-card="{esc(card_name)}" data-slot="{slot}" data-skill-type="{esc(skill_type)}" data-ct="{ct_data}" data-trend="{esc(trend)}" data-type="{esc(char_type)}">
                <td class="idol-cell">
                    <img src="{esc(icon_path)}" class="idol_icon" alt="{esc(card_name)} {esc(char_name)}" loading="lazy" onerror="this.style.display='none'">
                    <a href="{esc(detail_path)}" class="idol_link">{esc(card_name)}<br>{esc(char_name)}</a>
                </td>
                <td class="type-cell"><span class="badge badge-{esc(skill_type.lower())}">{esc(skill_type)}</span></td>
                <td class="skill-name-cell">{esc(name)}</td>
                <td class="skill-effect-cell">{esc_rich(effect)}</td>
            </tr>\n'''

    char_options = build_char_options_html(characters)


    page_description = "IDOLY PRIDEの全アイドルライブスキル一覧です。効果でキーワード検索できます。"
    page_title = "スキル一覧 - IDOLY PRIDE データベース M"
    seo_html = seo_meta_html('content/skill_list.html', page_title, page_description)
    breadcrumb_html = breadcrumb_jsonld([
        ('IDOLY PRIDE データベース M', ''),
        ('スキル一覧', 'content/skill_list.html'),
    ])

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="IDOLY PRIDE, スキル一覧, ライブスキル, データベース">
    <title>{page_title}</title>
    {seo_html}
    {FONT_PRECONNECT_HTML}
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="skill_list.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
    {breadcrumb_html}
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - スキル一覧</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">スキル一覧</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>スキル一覧</nav>
    <div id="filter-status" class="filter-status" style="display:none">
        <span id="filter-status-text">🔍 フィルタ中</span>
        <button type="button" class="filter-status-reset" onclick="resetFilters()">リセット</button>
    </div>
    <div class="search-bar-container">
        <div class="mode-row">
            <span class="mode-label">表示モード：</span>
            <select id="mode-select">
                <option value="flat">スキル別表示</option>
                <option value="grouped">カード単位表示</option>
            </select>
        </div>
        <div class="search-row">
            <input type="text" id="search-bar" class="search-bar" placeholder="効果でキーワード検索（スペース区切りで複数可）">
            <div class="search-mode">
                <label><input type="radio" name="search-mode" value="and" checked> AND</label>
                <label><input type="radio" name="search-mode" value="or"> OR</label>
            </div>
        </div>
        <div id="result-count" class="result-count"></div>
    </div>
    <div class="container">
        <div class="filters">
            <h2>フィルタ</h2>
            <div class="filter-section">
                <h3>キャラ</h3>
                <select id="filter-char">
                    <option value="">すべて</option>
{char_options}
                </select>
            </div>
            <div class="filter-section">
                <h3>傾向</h3>
                <label><input type="checkbox" class="trend-filter" value="ボーカル" checked> <span class="t_vocal">ボーカル</span></label><br>
                <label><input type="checkbox" class="trend-filter" value="ダンス" checked> <span class="t_dance">ダンス</span></label><br>
                <label><input type="checkbox" class="trend-filter" value="ビジュアル" checked> <span class="t_visual">ビジュアル</span></label>
            </div>
            <div class="filter-section">
                <h3>タイプ</h3>
                <label><input type="checkbox" class="type-filter" value="スコアラー" checked> スコアラー</label><br>
                <label><input type="checkbox" class="type-filter" value="バッファー" checked> バッファー</label><br>
                <label><input type="checkbox" class="type-filter" value="サポーター" checked> サポーター</label>
            </div>
            <div class="filter-section">
                <h3>スキル分類</h3>
                <label><input type="checkbox" class="skilltype-filter" value="SP" checked> <span class="badge badge-sp">SP</span></label><br>
                <label><input type="checkbox" class="skilltype-filter" value="A" checked> <span class="badge badge-a">A</span></label><br>
                <label><input type="checkbox" class="skilltype-filter" value="P" checked> <span class="badge badge-p">P</span></label>
            </div>
            <div class="filter-section">
                <h3>CT値</h3>
                <div class="ct-range">
                    <input type="number" id="ct-min" min="0" placeholder="最小" class="ct-input">
                    <span>〜</span>
                    <input type="number" id="ct-max" min="0" placeholder="最大" class="ct-input">
                </div>
            </div>
            <button type="button" class="reset" onclick="resetFilters()">リセット</button>
        </div>
        <div class="table-container">
            <table id="skill-table">
                <thead>
                    <tr>
                        <th>アイドル</th>
                        <th>種別</th>
                        <th>スキル名</th>
                        <th>効果</th>
                    </tr>
                </thead>
                <tbody>
{rows_html}                </tbody>
            </table>
        </div>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script src="skill_list.js"></script>
</body>
</html>'''

    os.makedirs('content', exist_ok=True)
    write_page('content/skill_list.html', html_content)

if __name__ == '__main__':
    generate_html()
    print('HTMLファイルが生成されました: スキル一覧')
