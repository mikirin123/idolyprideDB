from utils import write_page, esc, seo_meta_html, breadcrumb_jsonld, FONT_PRECONNECT_HTML
from db import load_characters

character_order = [
    "長瀬琴乃", "伊吹渚", "白石沙季", "成宮すず", "早坂芽衣", "川咲さくら", "兵藤雫",
    "白石千紗", "一ノ瀬怜", "佐伯遙子", "天動瑠依", "鈴村優", "奥山すみれ", "神崎莉央",
    "井川葵", "小美山愛", "赤崎こころ", "fran", "kana", "miho", "長瀬麻奈", "他"
]


def fetch_idols_by_character():
    character_dict = {}
    for row in load_characters():
        check, char, card_name, yell, obtain_method = row[0], row[2], row[3], row[22], row[23]
        character_dict.setdefault(char, []).append((check, card_name, yell, obtain_method))
    return character_dict


def build_idol_card(char, check, card_name, yell, obtain_method):
    detail_page_url = f"../detail/{esc(char)} {esc(card_name)}.html"
    incomplete_class = ' data-incomplete' if check == '★' else ''
    key = f"{char} {card_name}"
    return f"""
            <div class="idol-card-wrap">
                <a href="{detail_page_url}" class="idol-item{incomplete_class}">
                    <img src="../image/idol/{esc(char)} {esc(card_name)}.webp" alt="{esc(char)}">
                    <span>{esc(card_name)}<br>{esc(char)}</span>
                    <p>{esc(obtain_method)}</p>
                </a>
                <button class="idol-fav-btn" data-key="{esc(key)}" onclick="toggleFav(this)" aria-label="お気に入りに登録" aria-pressed="false">☆</button>
            </div>"""


def generate_html():
    character_dict = fetch_idols_by_character()

    toc_html = "<div class='toc'><div class='toc-buttons'>"
    for index, char in enumerate(character_order):
        if char in character_dict:
            toc_html += f"""
        <a class="toc-btn-wrap" href="#{char}">
            <img src="../image/circle_icon/{char}.webp" alt="{char}" class="toc-icon">
            <div class="toc-label">{char}</div>
        </a>"""
            if (index + 1) % 10 == 0:
                toc_html += "</div><div class='toc-buttons'>"

    other_characters = sorted(set(character_dict.keys()) - set(character_order))
    if other_characters:
        toc_html += """
    <a class="toc-btn-wrap" href="#他">
        <img src="../image/circle_icon/コラボ.webp" alt="他" class="toc-icon">
        <div class="toc-label">他</div>
    </a>"""

    toc_html += "</div></div>"

    idol_sep_list_html = ""
    for char in character_order:
        if char in character_dict:
            idol_sep_list_html += f"<div class='character-category' id=\"{char}\"><h3>{char}</h3><div class='idol-list'>"
            for check, card_name, yell, obtain_method in character_dict[char]:
                idol_sep_list_html += build_idol_card(char, check, card_name, yell, obtain_method)
            idol_sep_list_html += "</div></div>"

    if other_characters:
        idol_sep_list_html += "<div class='character-category' id=\"他\"><h3>他</h3><div class='idol-list'>"
        for char in other_characters:
            for check, card_name, yell, obtain_method in character_dict[char]:
                idol_sep_list_html += build_idol_card(char, check, card_name, yell, obtain_method)
        idol_sep_list_html += "</div></div>"

    page_description = "IDOLY PRIDEのキャラ別リストです。各アイドルのカード情報や入手方法を確認できます。"
    page_title = "キャラ別リスト - IDOLY PRIDE データベース M"
    seo_html = seo_meta_html('content/idol_sep_list.html', page_title, page_description)
    breadcrumb_html = breadcrumb_jsonld([
        ('IDOLY PRIDE データベース M', ''),
        ('キャラ別リスト', 'content/idol_sep_list.html'),
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="IDOLY PRIDE, アイドル, キャラ別リスト, カード情報, 入手方法">
    <title>{page_title}</title>
    {seo_html}
    {FONT_PRECONNECT_HTML}
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="idol_sep_list.css">
    <script src="favorites.js"></script>
    <script src="idol_sep_list.js"></script>
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    {breadcrumb_html}
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - キャラ別リスト</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">キャラ別リスト</div>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>キャラ別リスト</nav>
    <div class="container">
        {toc_html}
        {idol_sep_list_html}
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
</body>
</html>
"""

    write_page('content/idol_sep_list.html', html_content)
    print("HTMLファイルが生成されました: キャラ別リスト")


if __name__ == "__main__":
    generate_html()
