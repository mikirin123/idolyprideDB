from utils import write_page, esc, seo_meta_html, breadcrumb_jsonld, FONT_PRECONNECT_HTML, IN_ARTICLE_AD_HTML
import csv
from collections import defaultdict


def generate_html():
    with open('content/exphoto_list.csv', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        characters = [row for row in reader]

    # キャラ名ごとにグループ化
    char_dict = defaultdict(list)
    for row in characters:
        char_dict[row['キャラ名']].append(row)

    # 目次用リスト（アイコン＋ラベル）
    toc_html = '<nav class="toc"><div class="toc-buttons">'
    char_names = list(char_dict.keys())
    for i, name in enumerate(char_names):
        toc_html += f'''
    <a class="toc-btn-wrap" href="#char-{i}">
        <img src="../image/circle_icon/{esc(name)}.webp" alt="{esc(name)}" class="toc-icon">
        <div class="toc-label">{esc(name)}</div>
    </a>
    '''
    toc_html += "</div></nav>"

    # キャラごとにテーブルを生成
    tables_html = ""
    for i, (char_name, rows) in enumerate(char_dict.items()):
        skill_dict = defaultdict(list)
        for row in rows:
            skill_dict[row['スキル名']].append(row)
        tables_html += f"""
    <section id="char-{i}" class="char-table-section">
        <div class="char-table-box">
            <div class="char-header">
                <img src="../image/circle_icon/{esc(char_name)}.webp" alt="{esc(char_name)}" class="char-header-img">
                <h3 class="char-header-title">{esc(char_name)}</h3>
            </div>
            <table class="char-table">
                <tbody>
    """
        for idx, (skill_name, skill_rows) in enumerate(skill_dict.items()):
            detail_id = f"detail-{i}-{idx}"
            tables_html += f"""
                    <tr class="skill-row" data-detail="{detail_id}">
                        <td class="skill-name clickable">{esc(skill_name)}</td>
                    </tr>
                    <tr id="{detail_id}" class="skill-detail-row" style="display:none;">
                        <td colspan="2">
        """
            for row in skill_rows:
                level = row.get('レベル', '').strip()
                tables_html += f"""
                            <div class="skill-detail-item">
                                <div class="skill-detail-main">
                                    <div><strong>発動条件：</strong>{esc(row['発動条件'])}</div>
                                    <div><strong>スキル効果：</strong>{esc(row['スキル効果'])}</div>
                                    <div><strong>スタミナ：</strong>{esc(row['スタミナ'])} <strong>CT：</strong>{esc(row['CT'])}</div>
                                    <div><strong>オプション：</strong>{esc(row['オプション1'])} {esc(row['オプション2'])} {esc(row['オプション3'])} {esc(row['オプション4'])}</div>
                                </div>
                                <div class="skill-detail-level">
                                    {f"<u>Lv.{esc(level)}</u>" if level else ""}
                                </div>
                            </div>
            """
            tables_html += """
                        </td>
                    </tr>
        """
        tables_html += """
                </tbody>
            </table>
        </div>
    </section>
    """

    page_description = "IDOLY PRIDEの専用フォト一覧です。各キャラクターのスキル詳細や発動条件、効果を確認できます。"
    page_title = "専用フォト - IDOLY PRIDE データベース M"
    seo_html = seo_meta_html('content/exphoto_list.html', page_title, page_description)
    breadcrumb_html = breadcrumb_jsonld([
        ('IDOLY PRIDE データベース M', ''),
        ('専用フォト', 'content/exphoto_list.html'),
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="IDOLY PRIDE,専用フォト,スキル,発動条件,効果">
    <title>{page_title}</title>
    {seo_html}
    {FONT_PRECONNECT_HTML}
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="exphoto_list.css">
    <script src="exphoto_list.js"></script>
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    {breadcrumb_html}
</head>
<body>
    <header>
        <div class="banner">
            <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - 専用フォト</div>
            <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">専用フォト</div>
        </div>
    </header>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>専用フォト</nav>
    <main>
        <div class="container">
            {toc_html}
                <div class="accordion-content">
                    <b>データ提供のお願い</b>
                        <br>情報が不足しているフォトをお持ちの方は<a href="https://forms.gle/2Ume8iWwLtYjiUq17">フォーム</a>までご提供くださいますようお願いいたします。
                        <details>
                            <summary>不足フォト一覧</summary>
                            <a href="https://docs.google.com/spreadsheets/d/1ok0qeXNhI9E3IDgaspBD4HZ9Uys0V5Q1o8jcx23PV80/edit?usp=sharing">Googleスプレッドシート</a>
                            <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTWzfcWHUhgen2ncfEAcHc0vIIp-4FumHf7TJz4ELl1QYzPDMS7UN7Dwgg66yrImLlgC8xrJW5VEhWl/pubhtml?widget=true&amp;chrome=false" style="width: 100%; height: 350px;"></iframe>                </div>
            <hr>
            {IN_ARTICLE_AD_HTML}
            {tables_html}
        </div>
    </main>
    <button id="scrollToTopBtn">ページ上部へ</button>
</body>
</html>
"""

    write_page('content/exphoto_list.html', html_content)
    print("HTMLファイルが生成されました: 専用フォト")


if __name__ == "__main__":
    generate_html()
