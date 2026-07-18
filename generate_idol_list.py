from utils import write_page, build_char_options_html, esc
import os
import json
import pickle
from datetime import datetime, timedelta
from db import load_characters

def generate_html():
    characters = load_characters()
    char_options = build_char_options_html(characters)

    html_content = '''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="IDOLY PRIDEアイドルリストページです。アイドルの詳細情報を検索・フィルタリングできます。">
        <meta name="keywords" content="IDOLY PRIDE, アイドルリスト, ゲームデータベース">
        <title>アイドルリスト - IDOLY PRIDE データベース M</title>
        <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="idol_list.css">
        <link rel="shortcut icon" href="../image/icon.ico">
        <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
        <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
        <link rel="mask-icon" href="../image/icon.svg">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
        <meta name="google-adsense-account" content="ca-pub-9647262951514669">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    </head>
    <body>
        <div class="banner">
            <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - アイドルリスト</div>
            <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">アイドルリスト</div>
            <a href="javascript:history.back()" class="back-button">戻る</a>
        </div>
        <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>アイドルリスト</nav>
        <div id="filter-status" class="filter-status" style="display:none">
            <i class="fa-solid fa-filter"></i> <span id="filter-status-text">フィルタ中</span>
            <button type="button" class="filter-status-reset" onclick="resetFilters()">リセット</button>
        </div>
        <div class="search-bar-container">
            <div class="search-bar-wrapper">
                <input type="text" id="search-bar" class="search-bar" placeholder="アイドル名、衣装・髪型、スキル名・効果で検索">
                <div class="search-mode">
                    <label><input type="radio" name="search-mode" value="and" checked> AND検索</label>
                    <label><input type="radio" name="search-mode" value="or"> OR検索</label>
                </div>
                <button id="search-button" onclick="performSearchAndFilter()">適用</button>
            </div>
        </div>
        <div class="container">
            <div class="filters">
                <div class="filter-header" onclick="toggleFilter()">
                    フィルタ・並び替え<span id="filter-toggle-icon">▲</span>
                </div>
                <div id="filter-body">
                <form id="filter-form">
                    <div>
                        <h3>お気に入り</h3>
                        <label><input type="checkbox" id="fav-only"> お気に入りのみ表示</label>
                    </div>
                    <div>
                        <h3 id="no_br">キャラ</h3>
                        <div class="hint-icon">?</div>
                        <div class="hint-popup">コラボキャラは入手方法からフィルタできます</div>
                        <br>
                        <select name="character">
                            <option value="">すべて</option>
                            __CHAR_OPTIONS__
                        </select>
                    </div>
        
                    <div>
                        <h3>初期レアリティ</h3>
                        <label><input type="checkbox" name="rarity" value="★1">★1</label>
                        <label><input type="checkbox" name="rarity" value="★2">★2</label>
                        <label><input type="checkbox" name="rarity" value="★3">★3</label>
                        <label><input type="checkbox" name="rarity" value="★4">★4</label>
                        <label><input type="checkbox" name="rarity" value="★5">★5</label>
                        <label><input type="checkbox" name="rarity" value="★5覚醒">★5覚醒</label>
                    </div>
                    
                    <div>
                        <h3>入手方法</h3>
                        <select name="obtain">
                            <option value="">すべて</option>
                            <option value="恒常">恒常</option>
                            <option value="限定">限定</option>
                            <option value="フェス">フェス</option>
                            <option value="誕生日">誕生日</option>
                            <option value="プレミアム">プレミアム</option>
                            <option value="コラボ">コラボ</option>
                            <option value="イベント">イベント</option>
                            <option value="その他">その他</option>
                        </select>
                    </div>
                    
                    <div>
                        <h3>傾向</h3>
                        <label><input type="checkbox" name="trend" value="ボーカル"><font color="#FF469D">ボーカル</font></label>
                        <label><input type="checkbox" name="trend" value="ダンス"><font color="#3ABAFF">ダンス</font></label>
                        <label><input type="checkbox" name="trend" value="ビジュアル"><font color="#FFA900">ビジュアル</font></label>
                    </div>
                    
                    <div>
                        <h3>タイプ</h3>
                        <label><input type="checkbox" name="type" value="スコアラー">スコアラー</label>
                        <label><input type="checkbox" name="type" value="バッファー">バッファー</label>
                        <label><input type="checkbox" name="type" value="サポーター">サポーター</label>
                    </div>
                    
                    <div>
                        <h3>スキル構成</h3>
                        <label><input type="checkbox" name="skill" value="SP所持">SP所持</label>
                        <label><input type="checkbox" name="skill" value="SP未所持">SP未所持</label>
                        <label><input type="checkbox" name="skill" value="AA">AA</label>
                    </div>
                    
                    <div>
                        <h3>エール</h3>
                        <select name="support">
                            <option value="">すべて</option>
                            <option value="なし">なし</option>
                            <option value="ボーカルアップ">ボーカルアップ</option>
                            <option value="ダンスアップ">ダンスアップ</option>
                            <option value="ビジュアルアップ">ビジュアルアップ</option>
                            <option value="スタミナアップ">スタミナアップ</option>
                            <option value="メンタルアップ">メンタルアップ</option>
                            <option value="クリティカルアップ">クリティカルアップ</option>
                            <option value="ビートスコアアップ">ビートスコアアップ</option>
                            <option value="Aスキルスコアアップ">Aスキルスコアアップ</option>
                            <option value="SPスキルスコアアップ">SPスキルスコアアップ</option>
                            <option value="クリティカルスコアアップ">クリティカルスコアアップ</option>
                            <option value="MEXPアップ【自主トレ】">MEXPアップ【自主トレ】</option>
                            <option value="コインアップ【自主トレ】">コインアップ【自主トレ】</option>
                            <option value="レッスンピースアップ【自主トレ】">レッスンピースアップ【自主トレ】</option>
                            <option value="MEXPアップ【ファンイベント】">MEXPアップ【ファンイベント】</option>
                            <option value="MEXPアップ【プロモーション】">MEXPアップ【プロモーション】</option>
                            <option value="コインアップ【プロモーション】">コインアップ【プロモーション】</option>
                            <option value="アクセサリアップ">アクセサリアップ</option>
                            <option value="元気回復アップ">元気回復アップ</option>
                        </select>
                    </div>
                    <div>
                        <h3>並び替え</h3>
                        <label><input type="radio" name="sort" value="id" id="sort-id" checked>実装順</label>
                        <br>
                        <label><input type="radio" name="sort" value="ボーカル" ><font color="#FF469D">ボーカル</font></label>
                        <label><input type="radio" name="sort" value="ダンス"><font color="#3ABAFF">ダンス</font></label>
                        <label><input type="radio" name="sort" value="ビジュアル"><font color="#FFA900">ビジュアル</font></label>
                        <br>
                        <label><input type="radio" name="sort" value="スタミナ">スタミナ</label>
                        <div class="sort-order">
                            <label><input type="radio" name="sort-order" value="asc">昇順</label>
                            <label><input type="radio" name="sort-order" value="desc" checked>降順</label>
                        </div>
                    </div>
                    <button type="button" class="reset" onclick="resetFilters()">全てリセット</button>
                </form>
                </div>
            </div>
            <div class="table-container">
                <table id="character-table">
                    <tr>
                        <th class="fav-header">★</th>
                        <th class="hidden">入力チェック</th>
                        <th class="hidden">ID</th>
                        <th class="hidden">キャラ</th>
                        <th>アイドル名</th>
                        <th class="hidden">初期レアリティ</th>
                        <th>傾向</th>
                        <th>タイプ</th>
                        <th>構成</th>
                        <th class="hidden">衣装・ヘアスタイル</th>
                        <th class="hidden">覚醒衣装</th>
                        <th class="hidden">ボーカル</th>
                        <th class="hidden">ダンス</th>
                        <th class="hidden">ビジュアル</th>
                        <th class="hidden">スタミナ</th>
                        <th class="hidden">ライブスキル1名前</th>
                        <th class="hidden">ライブスキル1効果</th>
                        <th class="hidden">ライブスキル2名前</th>
                        <th class="hidden">ライブスキル2効果</th>
                        <th class="hidden">ライブスキル3名前</th>
                        <th class="hidden">ライブスキル3効果</th>
                        <th class="hidden">覚醒スキル名前</th>
                        <th class="hidden">覚醒スキル効果</th>
                        <th>エール</th>
                        <th class="hidden">入手方法</th>
                        <th class="hidden">実装日</th>
                    </tr>
    '''

    html_content = html_content.replace('__CHAR_OPTIONS__', char_options, 1)

    for character in characters:
        row_data = [
            f'<td><img src="../image/idol/{esc(character[2])} {esc(item)}.webp" class="idol_image" alt="{esc(item)} {esc(character[2])}" loading="lazy"><br><a href="../detail/{esc(character[2])} {esc(item)}.html" class="idol_link">{esc(item)} {esc(character[2])}</a></td>' if i == 3 else
            f'<td class="hidden">{esc(item)}</td>' if i in [0, 1, 2, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24] else
            f'<td class="trend-vocal" value="{esc(item)}"><span class="text">{esc(item)}</span><img src="../image/tr_{esc(item)}.webp" class="icon" alt=""></td>' if i == 5 and item == 'ボーカル' else
            f'<td class="trend-dance" value="{esc(item)}"><span class="text">{esc(item)}</span><img src="../image/tr_{esc(item)}.webp" class="icon" alt=""></td>' if i == 5 and item == 'ダンス' else
            f'<td class="trend-visual" value="{esc(item)}"><span class="text">{esc(item)}</span><img src="../image/tr_{esc(item)}.webp" class="icon" alt=""></td>' if i == 5 and item == 'ビジュアル' else
            f'<td class="type-scorer" value="{esc(item)}"><span class="text">{esc(item)}</span><img src="../image/ty_{esc(item)}.webp" class="icon" alt=""></td>' if i == 6 and item == 'スコアラー' else
            f'<td class="type-buffer" value="{esc(item)}"><span class="text">{esc(item)}</span><img src="../image/ty_{esc(item)}.webp" class="icon" alt=""></td>' if i == 6 and item == 'バッファー' else
            f'<td class="type-supporter" value="{esc(item)}"><span class="text">{esc(item)}</span><img src="../image/ty_{esc(item)}.webp" class="icon" alt=""></td>' if i == 6 and item == 'サポーター' else
            f'<td value="{esc(item)}"><img src="../image/yell/{esc(item)}.webp" class="yell_icon" alt="{esc(item)}"></td>' if i == 22 else
            f'<td>{esc(item)}</td>'
            for i, item in enumerate(character)
        ]
        card_key = f'{character[2]} {character[3]}'
        fav_cell = f'<td class="fav-cell"><button class="fav-btn" data-key="{esc(card_key)}">☆</button></td>'
        row_class = ' class="data-incomplete"' if character[0] == '★' else ''
        html_content += f'<tr data-cardkey="{esc(card_key)}" data-char="{esc(character[2])}" data-card="{esc(character[3])}" data-trend="{esc(character[5])}" data-type="{esc(character[6])}"{row_class}>' + fav_cell + ''.join(row_data) + '</tr>'

    html_content += '''
                </table>
            </div>
        </div>
        <button id="scrollToTopBtn">ページ上部へ</button>
    </body>
    <script src="idol_list.js"></script>
    </html>
    '''

    write_page('content/idol_list.html', html_content)

if __name__ == "__main__":
    generate_html()
    print("HTMLファイルが生成されました: アイドルリスト")