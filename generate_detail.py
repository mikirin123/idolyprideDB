import os
import json
from urllib.parse import quote
from db import load_characters
from utils import (
    write_page, esc, esc_rich, DEFAULT_PROFILE,
    seo_meta_html, breadcrumb_jsonld, FONT_PRECONNECT_HTML,
)

def load_profiles():
    with open('data/profiles.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html():
    characters = load_characters()
    profiles = load_profiles()
    generate_detail_pages(characters, profiles)

def generate_detail_pages(characters, profiles):
    def rank_with_ties(sorted_list, value):
        return next(i for i, v in enumerate(sorted_list, 1) if v == value)

    vocal_ranks = sorted([int(x[10]) for x in characters], reverse=True)
    dance_ranks = sorted([int(x[11]) for x in characters], reverse=True)
    visual_ranks = sorted([int(x[12]) for x in characters], reverse=True)
    stamina_ranks = sorted([int(x[13]) for x in characters], reverse=True)

    power_ranks = sorted([int(int(x[10]) * 0.5) + int(int(x[11]) * 0.5) + int(int(x[12]) * 0.5)+ int(int(x[13]) * 0.8) + 500 for x in characters], reverse=True)

    total_idols = len(characters)

    for character in characters:
        vocal_rank = rank_with_ties(vocal_ranks, int(character[10]))
        dance_rank = rank_with_ties(dance_ranks, int(character[11]))
        visual_rank = rank_with_ties(visual_ranks, int(character[12]))
        stamina_rank = rank_with_ties(stamina_ranks, int(character[13]))


        power_stat = int(int(character[10]) * 0.5) + int(int(character[11]) * 0.5) + int(int(character[12]) * 0.5) + int(int(character[13]) * 0.8)+ 500
        power_rank = rank_with_ties(power_ranks, power_stat)

        total_idol = total_idols
        compare_param = quote(f'{character[2]} {character[3]}')

        personal_details = profiles.get(character[2], DEFAULT_PROFILE)

        pd = [esc(v) for v in personal_details]
        personal_details_table = f'''
            <h2>{esc(character[2])}-プロフィール</h2>
            <table class="personal-details-table">
                <tr><th>CV</th><td>{pd[0]}</td></tr>
                <tr><th>誕生日</th><td>{pd[1]}</td></tr>
                <tr><th>星座</th><td>{pd[2]}</td></tr>
                <tr><th>年齢</th><td>{pd[3]}</td></tr>
                <tr><th>身長</th><td>{pd[4]}</td></tr>
                <tr><th>体重</th><td>{pd[5]}</td></tr>
                <tr><th>スリーサイズ</th><td>{pd[6]}-{pd[7]}-{pd[8]}</td></tr>
                <tr><th>学校</th><td>{pd[9]}</td></tr>
                <tr><th>好き</th><td>{pd[10]} {pd[11]} {pd[12]}</td></tr>
                <tr><th>嫌い</th><td>{pd[13]} {pd[14]} {pd[15]}</td></tr>
                <tr><th>趣味</th><td>{pd[16]} {pd[17]} {pd[18]} {pd[19]} {pd[20]}</td></tr>
                <tr><th>その他</th><td>{pd[21]}</td></tr>
            </table>
            '''

        elseidols = []
        for i in characters:
            if i[2] == character[2]:
                i_incomplete = ' data-incomplete' if i[0] == '★' else ''
                elseidols.append(f'<tr class="else-idol-row{i_incomplete}"><th><img src="../image/idol/{esc(i[2])} {esc(i[3])}.webp" width="60" alt="{esc(i[3])} {esc(i[2])}"></th><th>{esc(i[4])}</th><td><a href="{esc(i[2])} {esc(i[3])}.html" class="idol_link">{esc(i[3])} {esc(i[2])}</a></td></tr>')
        elseidols = ''.join(elseidols)


        incomplete_notice = '<div class="data-incomplete-notice">⚠ このアイドルのデータは未入力の項目があります</div>' if character[0] == '★' else ''

        detail_page_url = f'detail/{character[2]} {character[3]}.html'.replace('\n', '')
        obtain_method = character[23].strip()
        impl_date = character[24].strip()
        detail_description = (
            f'IDOLY PRIDE「{esc(character[3])} {esc(character[2])}」の詳細ページです。'
            + (f'入手方法: {esc(obtain_method)}。' if obtain_method else '')
            + (f'実装日: {esc(impl_date)}。' if impl_date else '')
            + '基本情報、ステータス、ライブスキルなどの情報を掲載しています。'
        )
        detail_title = f'{character[3]} {character[2]} - IDOLY PRIDE データベース M'
        detail_seo_html = seo_meta_html(detail_page_url, detail_title, detail_description)
        detail_breadcrumb_html = breadcrumb_jsonld([
            ('IDOLY PRIDE データベース M', ''),
            ('アイドルリスト', 'content/idol_list.html'),
            (character[2], detail_page_url),
        ])

        detail_content = f'''
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="{detail_description}">
            <meta name="keywords" content="IDOLY PRIDE, アイドル, {character[3]}, {character[2]}, データベース">
            <title>{detail_title}</title>
            {detail_seo_html}
            {FONT_PRECONNECT_HTML}
            <link rel="stylesheet" href="../common.css">
            <link rel="stylesheet" href="detail.css">
            <link rel="shortcut icon" href="../image/icon.ico">
            <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
            <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
            <link rel="mask-icon" href="../image/icon.svg">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
            <meta name="google-adsense-account" content="ca-pub-9647262951514669">
            <script src="detail.js" defer></script>
            {detail_breadcrumb_html}
        </head>
        <body>
            <div class="banner">
                <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - アイドルリスト - {esc(character[3])} {esc(character[2])}</div>
                <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">{esc(character[3])} {esc(character[2])}</div>
                <button class="fav-btn" id="detail-fav-btn" data-key="{esc(character[2])} {esc(character[3])}" aria-label="お気に入りに登録" aria-pressed="false">☆</button>
            </div>
            {incomplete_notice}
            <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span><a href="../content/idol_list.html">アイドルリスト</a><span>›</span>{esc(character[2])}</nav>
            <div class="container">
                <br>
                <div class="left-column">
                    <img src="../image/idol/{esc(character[2])} {esc(character[3])}.webp" class="af_image" alt="{esc(character[3])} {esc(character[2])}" onerror="this.style.display='none';">
                    <img src="../image/idol_bf/{esc(character[2])} {esc(character[3])} bf.webp" onerror="this.style.display='none';" class="bf_image" alt="{esc(character[3])} {esc(character[2])} 覚醒後">
                    <img src="../image/idol_cos/{esc(character[2])} {esc(character[8])}.webp" onerror="this.style.display='none';" class="bf_image" alt="{esc(character[2])} {esc(character[8])}">
                    <div class="personal-details">{personal_details_table}</div>
                    <div class="else-idols"><h2>他アイドル</h2><table>{elseidols}</table></div>
                </div>
                <div class="right-column">
                    <div class="right-container">
                        <h2 class="mokuji"> 基本情報</h2>
                        <table class="basic-info-table">
                            <tr><th>初期レアリティ</th><td>{esc(character[4])}</td></tr>
                            <tr><th>傾向</th><td class="{'t_vocal' if character[5] == 'ボーカル' else 't_dance' if character[5] == 'ダンス' else 't_visual' if character[5] == 'ビジュアル' else ''}">{esc(character[5])}</td></tr>
                            <tr><th>タイプ</th><td>{esc(character[6])}</td></tr>
                            <tr><th>スキル構成</th><td>{esc(character[7])}</td></tr>
                            <tr><th>エール</th><td>{esc(character[22])}</td></tr>
                            <tr><th>衣装・ヘアスタイル</th><td>{esc(character[8])}</td></tr>
                            <tr><th>覚醒衣装</th><td class="awakening">{esc(character[9])}</td></tr>
                            <tr><th>入手方法</th><td>{esc(character[23])}</td></tr>
                            <tr><th>実装日</th><td>{esc(character[24])}</td></tr>
                        </table>
                        <h2 class="mokuji"> ステータス</h2>
                        <table class="status-table">
                            <tr><th><span class="t_vocal">ボーカル</span></th><td>{character[10]}(<b>{vocal_rank}位</b>/{total_idol})</td></tr>
                            <tr><th><span class="t_dance">ダンス</span></th><td>{character[11]}(<b>{dance_rank}位</b>/{total_idol})</td></tr>
                            <tr><th><span class="t_visual">ビジュアル</span></th><td>{character[12]}(<b>{visual_rank}位</b>/{total_idol})</td></tr>
                            <tr><th>スタミナ</th><td>{character[13]}(<b>{stamina_rank}位</b>/{total_idol})</td></tr>
                            <tr><th>パワー</th><td>{power_stat}(<b>{power_rank}位</b>/{total_idol})</td></tr>
                        </table>
                        <div class="table_details"><a href="../content/stats_list.html">ステータスランキング</a> ・ <a href="../content/compare.html?c1={compare_param}">アイドル比較に追加</a></div>
                        <h2 class="mokuji"> ライブスキル</h2>
                        <div class="live-skill-table-container">
                            <table class="live-skill-table">
                                <tr><th>{esc(character[14])}</th></tr>
                                <tr><td class="skill-details">{esc_rich(character[15])}</td></tr>
                                <tr><th>{esc(character[16])}</th></tr>
                                <tr><td class="skill-details">{esc_rich(character[17])}</td></tr>
                                <tr><th>{esc(character[18])}</th></tr>
                                <tr><td class="skill-details">{esc_rich(character[19])}</td></tr>
                                <tr class="awakening"><th>{esc(character[20])}</th></tr>
                                <tr class="awakening"><td class="skill-details">{esc_rich(character[21])}</td></tr>
                                <tr class="table_details-row"><td class="table_details">Lv200/スキルLv最大時の数値です。</td></tr>
                            </table>
                        </div>
                        <div class="else-idols-phone"><h2>他アイドル</h2><table>{elseidols}</table></div>
                        <div class="personal-details-phone">{personal_details_table}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''

        os.makedirs('detail', exist_ok=True)
        filename = f'detail/{character[2]} {character[3]}.html'.replace('\n', '')
        write_page(filename, detail_content)

if __name__ == "__main__":
    generate_html()
    print("HTMLファイルが生成されました: detailページ")
