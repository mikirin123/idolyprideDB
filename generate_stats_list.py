from utils import write_page, build_char_options_html, esc
import os
from db import load_characters

def calculate_power(vo, da, vi, st):
    """PWR.値を計算する関数（少数切り捨て）"""
    return int(vo * 0.5) + int(da * 0.5) + int(vi * 0.5) + int(st * 0.8) + 500

STAT_CLASS = {'Vo.': 'stat-vo', 'Da.': 'stat-da', 'Vi.': 'stat-vi'}

def generate_html():
    try:
        characters = load_characters()
        char_options = build_char_options_html(characters)

        # ランキングデータの準備
        stats_indices = {'Vo.': 10, 'Da.': 11, 'Vi.': 12, 'St.': 13}
        ranks = {key: sorted([int(x[idx]) for x in characters], reverse=True) for key, idx in stats_indices.items()}
        ranks['PWR.'] = sorted(
            [calculate_power(int(x[10]), int(x[11]), int(x[12]), int(x[13])) for x in characters],
            reverse=True
        )

        # HTML生成
        html_content = '''
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="IDOLY PRIDEのステータスランキングを確認できます。各アイドルのVo., Da., Vi., St., PWR.を比較して表示します。">
            <meta name="keywords" content="IDOLY PRIDE, ステータスランキング, Vo., Da., Vi., St., PWR.">
            <title>ステータスランキング - IDOLY PRIDE データベース M</title>
            <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="stats_list.css">
            <script src="stats_list.js"></script>
            <link rel="shortcut icon" href="../image/icon.ico">
            <link rel="icon" type="image/png" sizes="180x180" href="../image/icon.png">
            <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
            <link rel="mask-icon" href="../image/icon.svg">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
            <meta name="google-adsense-account" content="ca-pub-9647262951514669">
        </head>
        <body>
            <div class="banner">
                <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - ステータスランキング</div>
                <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">ステータスランキング</div>
                <a href="javascript:history.back()" class="back-button">戻る</a>
            </div>
            <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>ステータスランキング</nav>
            <div id="filter-status" class="filter-status" style="display:none">
                <span id="filter-status-text">🔍 フィルタ中</span>
                <button type="button" class="filter-status-reset" onclick="resetStatsFilter()">リセット</button>
            </div>
            <div class="stats-toolbar">
                <div class="stats-filter">
                    <label>キャラ <select id="f-char"><option value="">すべて</option>
                        __CHAR_OPTIONS__
                    </select></label>
                    <label>傾向 <select id="f-trend"><option value="">すべて</option>
                        <option value="ボーカル">ボーカル</option><option value="ダンス">ダンス</option><option value="ビジュアル">ビジュアル</option>
                    </select></label>
                    <label>タイプ <select id="f-type"><option value="">すべて</option>
                        <option value="スコアラー">スコアラー</option><option value="バッファー">バッファー</option><option value="サポーター">サポーター</option>
                    </select></label>
                    <label>入手 <select id="f-obtain"><option value="">すべて</option>
                        <option value="恒常">恒常</option><option value="限定">限定</option><option value="フェス">フェス</option>
                        <option value="誕生日">誕生日</option><option value="プレミアム">プレミアム</option>
                        <option value="コラボ">コラボ</option><option value="イベント">イベント</option><option value="その他">その他</option>
                    </select></label>
                    <span id="stats-filter-count" class="stats-filter-count"></span>
                    <button onclick="resetStatsFilter()" class="stats-filter-reset">リセット</button>
                </div>
            </div>
            <div class="stats_list-sidebar-container">
                <div class="stats_list-sidebar">
        '''

        html_content = html_content.replace('__CHAR_OPTIONS__', char_options, 1)

        # カテゴリごとのランキングを生成
        categories = ['スコアラー', 'バッファー', 'サポーター']
        stats = ['Vo.', 'Da.', 'Vi.']
        for stat in stats:
            html_content += f'<div class="stats-stat-group {STAT_CLASS[stat]}">'
            for category in categories:
                html_content += f'<div class="stats-card"><h3>{stat} {category} TOP5</h3><ul>'
                top_characters = sorted(
                    [x for x in characters if x[6] == category],
                    key=lambda x: int(x[stats_indices[stat]]),
                    reverse=True
                )[:5]
                for rank, idol in enumerate(top_characters, start=1):
                    rank_class = ' data-incomplete' if idol[0] == '★' else ''
                    html_content += f'''
                    <li class="rank-item{rank_class}">
                        <span class="rank-badge">{rank}</span>
                        <img src="../image/idol/{esc(idol[2])} {esc(idol[3])}.webp" alt="{esc(idol[3])} {esc(idol[2])}">
                        <a href="../detail/{esc(idol[2])} {esc(idol[3])}.html">
                            <span class="rank-value">{int(idol[stats_indices[stat]])}</span>
                            <span class="rank-name">{esc(idol[3])} {esc(idol[2])}</span>
                        </a>
                    </li>
                    '''
                html_content += '</ul></div>'
            html_content += '</div>'

        html_content += '''
                </div>
                <div class="stats_list-container">
                    <div class="stats_list-table-card">
                    <table class="stats_list-table">
                        <tr>
                            <th>アイドル名</th>
                            <th class="hidden">傾向・タイプ</th>
                            <th class="sortable">Vo.</th>
                            <th class="sortable">Da.</th>
                            <th class="sortable">Vi.</th>
                            <th class="sortable">St.</th>
                            <th class="sortable pwr">PWR.</th>
                        </tr>
        '''

        # テーブルデータを生成
        for character in characters:
            power_stat = calculate_power(int(character[10]), int(character[11]), int(character[12]), int(character[13]))
            row_class = ' class="data-incomplete"' if character[0] == '★' else ''
            html_content += f'''
            <tr{row_class} data-char="{esc(character[2])}" data-trend="{esc(character[5])}" data-type="{esc(character[6])}" data-rarity="{esc(character[4])}" data-obtain="{esc(character[23])}">
                <td class="idol_names">
                    <img src="../image/idol/{esc(character[2])} {esc(character[3])}.webp" alt="{esc(character[3])} {esc(character[2])}">
                    <a href="../detail/{esc(character[2])} {esc(character[3])}.html" class="idol_link">
                        {esc(character[3])} {esc(character[2])}
                    </a>
                </td>
                <td class="hidden">
                    <img src="../image/tr_{esc(character[5])}.webp" class="idol_type" alt="{esc(character[5])}">
                    <img src="../image/ty_{esc(character[6])}.webp" class="idol_type" alt="{esc(character[6])}">
                </td>
                <td class="status">{int(character[10])}</td>
                <td class="status">{int(character[11])}</td>
                <td class="status">{int(character[12])}</td>
                <td class="status">{int(character[13])}</td>
                <td class="status pwr">{power_stat}</td>
            </tr>
            '''

        html_content += '''
                    </table>
                    </div>
                </div>
            </div>
            <button id="scrollToTopBtn">ページ上部へ</button>
        </body>
        </html>
        '''

        # ファイル書き込み
        os.makedirs('content', exist_ok=True)
        write_page('content/stats_list.html', html_content)
        print("HTMLファイルが生成されました: ステータスランキング")

    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    generate_html()
