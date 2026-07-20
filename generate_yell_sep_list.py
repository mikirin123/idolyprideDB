from utils import write_page, esc, seo_meta_html, breadcrumb_jsonld, FONT_PRECONNECT_HTML
from db import load_characters

# CSVからエール別アイドル情報を取得
def fetch_idols_by_yell():
    # 入力チェック(0), キャラ(2), カード名(3), エール(22), 入手方法(23)
    yell_dict = {}
    for row in load_characters():
        check, char, card_name, yell, obtain_method = row[0], row[2], row[3], row[22], row[23]
        yell_dict.setdefault(yell, []).append((check, char, card_name, obtain_method))
    return yell_dict

# HTML目次を生成
def generate_toc_html(yell_dict, yell_order):
    toc_html = "<div class='toc'><div class='toc-buttons'>"
    for idx, yell in enumerate(yell_order):
        if yell in yell_dict:
            toc_html += f"<a href=\"#{yell}\"><img src=\"../image/yell/{yell}.webp\" alt=\"{yell}\" style=\"width: 50px; height: 50px;\"></a>"
            if (idx + 1) % 10 == 0:
                toc_html += "</div><div class='toc-buttons'>"
    toc_html += "</div></div>"
    return toc_html

# HTMLアイドルリストを生成
def generate_idol_list_html(yell_dict, yell_order):
    idol_list_html = ""
    for yell in yell_order:
        if yell in yell_dict:
            idols = yell_dict[yell]
            idol_list_html += f"<div class='yell-category' id=\"{yell}\"><h3>{yell}</h3><div class='idol-list'>"
            for check, char, card_name, obtain_method in idols:
                detail_page_url = f"../detail/{esc(char)} {esc(card_name)}.html"
                incomplete_class = ' data-incomplete' if check == '★' else ''
                key = f"{char} {card_name}"
                idol_list_html += f"""
                <div class="idol-card-wrap">
                    <a href="{detail_page_url}" class="idol-item{incomplete_class}">
                        <img src="../image/idol/{esc(char)} {esc(card_name)}.webp" alt="{esc(char)}">
                        <span>{esc(card_name)}<br>{esc(char)}</span>
                        <p>{esc(obtain_method)}</p>
                    </a>
                    <button class="idol-fav-btn" data-key="{esc(key)}" onclick="toggleFav(this)" aria-label="お気に入りに登録" aria-pressed="false">☆</button>
                </div>
                """
            idol_list_html += "</div></div>"
    return idol_list_html

# メイン処理
def main():
    yell_order = [
        "なし", "ボーカルアップ", "ダンスアップ", "ビジュアルアップ", "スタミナアップ", 
        "メンタルアップ", "クリティカルアップ", "ビートスコアアップ", "Aスキルスコアアップ", 
        "SPスキルスコアアップ", "クリティカルスコアアップ", "MEXPアップ【自主トレ】", 
        "コインアップ【自主トレ】", "レッスンピースアップ【自主トレ】", "MEXPアップ【ファンイベント】", 
        "MEXPアップ【プロモーション】", "コインアップ【プロモーション】", "アクセサリアップ", "元気回復アップ"
    ]

    yell_dict = fetch_idols_by_yell()
    toc_html = generate_toc_html(yell_dict, yell_order)
    idol_list_html = generate_idol_list_html(yell_dict, yell_order)

    page_description = "IDOLY PRIDEのエール別アイドルリストを確認できます。各エールごとにアイドルのカード名と入手方法を表示します。"
    page_title = "エール別リスト - IDOLY PRIDE データベース M"
    seo_html = seo_meta_html('content/yell_sep_list.html', page_title, page_description)
    breadcrumb_html = breadcrumb_jsonld([
        ('IDOLY PRIDE データベース M', ''),
        ('エール別リスト', 'content/yell_sep_list.html'),
    ])

    html_content = f"""<!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="{page_description}">
        <meta name="keywords" content="IDOLY PRIDE, エール別リスト, アイドル, カード名, 入手方法">
        <title>{page_title}</title>
        {seo_html}
        {FONT_PRECONNECT_HTML}
        <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="yell_sep_list.css">
        <script src="favorites.js"></script>
        <script src="yell_sep_list.js"></script>
        <link rel="shortcut icon" href="../image/icon.ico">
        <link rel="icon" type="image/png" sizes="32x32" href="../image/icon.png">
        <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
        <link rel="mask-icon" href="../image/icon.svg">
        {breadcrumb_html}
    </head>
    <body>
        <div class="banner">
            <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - エール別リスト</div>
            <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">エール別リスト</div>
        </div>
        <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>エール別リスト</nav>
        <div class="container">
            {toc_html}
            {idol_list_html}
        </div>
        <button id="scrollToTopBtn">ページ上部へ</button>
    </body>
    </html>
    """

    output_path = "content/yell_sep_list.html"
    write_page(output_path, html_content)

    print("HTMLファイルが生成されました: エール別リスト")

if __name__ == "__main__":
    main()
