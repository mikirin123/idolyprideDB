from utils import write_if_changed, build_char_options_html, esc
import os
from db import load_characters
from collections import defaultdict

RARITY_OPTIONS = ['★1', '★2', '★3', '★4', '★5', '★5覚醒']
OBTAIN_OPTIONS = ['恒常', '限定', 'フェス', '誕生日', 'プレミアム', 'コラボ', 'イベント', 'その他']
SUPPORT_OPTIONS = [
    'なし', 'ボーカルアップ', 'ダンスアップ', 'ビジュアルアップ', 'スタミナアップ', 'メンタルアップ',
    'クリティカルアップ', 'ビートスコアアップ', 'Aスキルスコアアップ', 'SPスキルスコアアップ',
    'クリティカルスコアアップ', 'MEXPアップ【自主トレ】', 'コインアップ【自主トレ】',
    'レッスンピースアップ【自主トレ】', 'MEXPアップ【ファンイベント】', 'MEXPアップ【プロモーション】',
    'コインアップ【プロモーション】', 'アクセサリアップ', '元気回復アップ',
]


def _date_key(date_str):
    parts = date_str.split('/')
    if len(parts) != 3:
        return None
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return None


def generate_html():
    characters = load_characters()
    char_options = build_char_options_html(characters)
    obtain_options_html = '\n'.join(f'<option value="{o}">{o}</option>' for o in OBTAIN_OPTIONS)
    support_options_html = '\n'.join(f'<option value="{o}">{o}</option>' for o in SUPPORT_OPTIONS)
    rarity_checks_html = '\n'.join(
        f'<label><input type="checkbox" class="tl-rarity-filter" value="{r}">{r}</label>' for r in RARITY_OPTIONS
    )

    # 実装日でグループ化（日付なし・不正な形式は末尾に）
    dated = []
    undated = []
    for c in characters:
        release_date = c[24] if len(c) > 24 else ''
        if release_date and _date_key(release_date) is not None:
            dated.append(c)
        else:
            undated.append(c)

    dated.sort(key=lambda c: _date_key(c[24]), reverse=True)

    groups = defaultdict(list)
    for c in dated:
        groups[c[24]].append(c)

    def card_html(c):
        char, card = c[2], c[3]
        rarity = c[4]
        trend = c[5]
        char_type = c[6]
        skill = c[7]
        support = c[22]
        obtain = c[23]
        trend_class = 'trend-vocal' if trend == 'ボーカル' else 'trend-dance' if trend == 'ダンス' else 'trend-visual' if trend == 'ビジュアル' else ''
        obtain_class = 'obtain-' + obtain if obtain in ('限定', 'フェス', '誕生日', 'プレミアム') else ''
        incomplete_class = ' data-incomplete' if c[0] == '★' else ''
        cardkey = f'{char} {card}'
        return f'''<a href="../detail/{esc(char)} {esc(card)}.html" class="tl-card {obtain_class}{incomplete_class}"
            data-char="{esc(char)}" data-card="{esc(card)}" data-cardkey="{esc(cardkey)}"
            data-rarity="{esc(rarity)}" data-trend="{esc(trend)}" data-type="{esc(char_type)}"
            data-skill="{esc(skill)}" data-support="{esc(support)}" data-obtain="{esc(obtain)}">
            <img src="../image/idol/{esc(char)} {esc(card)}.webp" alt="{esc(card)} {esc(char)}" loading="lazy" onerror="this.style.opacity=0.2">
            <div class="tl-card-name {trend_class}">{esc(card)}</div>
            <div class="tl-card-char">{esc(char)}</div>
            <div class="tl-card-obtain">{esc(obtain)}</div>
        </a>'''

    timeline_html = ''
    for date in sorted(groups.keys(), key=_date_key, reverse=True):
        # 日付をYYYY/MM/DD形式に変換
        try:
            parts = date.split('/')
            if len(parts) == 3:
                date_str = f'{int(parts[0])}年{int(parts[1])}月{int(parts[2])}日'
            else:
                date_str = date
        except Exception:
            date_str = date

        count = len(groups[date])
        timeline_html += f'''<div class="tl-group">
            <div class="tl-date"><span class="tl-date-text">{esc(date_str)}</span><span class="tl-date-count">{count}件</span></div>
            <div class="tl-cards">{''.join(card_html(c) for c in groups[date])}</div>
        </div>'''

    if undated:
        timeline_html += f'''<div class="tl-group">
            <div class="tl-date"><span class="tl-date-text">日付未登録</span><span class="tl-date-count">{len(undated)}件</span></div>
            <div class="tl-cards">{''.join(card_html(c) for c in undated)}</div>
        </div>'''

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="IDOLY PRIDEのカードリリース履歴です。実装日ごとにカードを確認できます。">
    <meta name="keywords" content="IDOLY PRIDE, リリース履歴, 実装日, データベース">
    <title>リリース履歴 - IDOLY PRIDE データベース M</title>
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="timeline.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - リリース履歴</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">リリース履歴</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>リリース履歴</nav>
    <div id="filter-status" class="filter-status" style="display:none">
        <span id="filter-status-text">🔍 フィルタ中</span>
        <button type="button" class="filter-status-reset" onclick="resetTlFilters()">リセット</button>
    </div>
    <div class="tl-toolbar">
        <div class="tl-search-row">
            <input type="text" id="tl-search-bar" class="tl-search-bar" placeholder="アイドル名・カード名で検索（スペース区切りで複数可）">
            <div class="tl-search-mode">
                <label><input type="radio" name="tl-search-mode" value="and" checked> AND</label>
                <label><input type="radio" name="tl-search-mode" value="or"> OR</label>
            </div>
            <button type="button" id="tl-screenshot-btn">📷 画像として保存</button>
        </div>
        <div class="tl-filter-header" onclick="toggleTlFilter()">
            フィルタ・並び替え<span id="tl-filter-toggle-icon">▲</span>
        </div>
        <div id="tl-filter-body">
            <div class="tl-filter-row">
                <label><input type="checkbox" id="tl-fav-only"> お気に入りのみ表示</label>
            </div>
            <div class="tl-filter-row">
                <label class="tl-filter-select">キャラ：
                    <select id="tl-char-filter">
                        <option value="">すべて</option>
                        {char_options}
                    </select>
                </label>
                <label class="tl-filter-select">入手方法：
                    <select id="tl-obtain-filter">
                        <option value="">すべて</option>
                        {obtain_options_html}
                    </select>
                </label>
                <label class="tl-filter-select">エール：
                    <select id="tl-support-filter">
                        <option value="">すべて</option>
                        {support_options_html}
                    </select>
                </label>
            </div>
            <div class="tl-filter-row">
                <span class="tl-filter-label">初期レアリティ：</span>
                {rarity_checks_html}
            </div>
            <div class="tl-filter-row">
                <span class="tl-filter-label">傾向：</span>
                <label><input type="checkbox" class="tl-trend-filter" value="ボーカル"><span class="trend-vocal">ボーカル</span></label>
                <label><input type="checkbox" class="tl-trend-filter" value="ダンス"><span class="trend-dance">ダンス</span></label>
                <label><input type="checkbox" class="tl-trend-filter" value="ビジュアル"><span class="trend-visual">ビジュアル</span></label>
            </div>
            <div class="tl-filter-row">
                <span class="tl-filter-label">タイプ：</span>
                <label><input type="checkbox" class="tl-type-filter" value="スコアラー">スコアラー</label>
                <label><input type="checkbox" class="tl-type-filter" value="バッファー">バッファー</label>
                <label><input type="checkbox" class="tl-type-filter" value="サポーター">サポーター</label>
            </div>
            <div class="tl-filter-row">
                <span class="tl-filter-label">スキル構成：</span>
                <label><input type="checkbox" class="tl-skill-filter" value="SP所持">SP所持</label>
                <label><input type="checkbox" class="tl-skill-filter" value="SP未所持">SP未所持</label>
                <label><input type="checkbox" class="tl-skill-filter" value="AA">AA</label>
            </div>
            <button type="button" class="tl-reset" onclick="resetTlFilters()">リセット</button>
        </div>
        <span id="tl-count" class="tl-count"></span>
    </div>
    <div class="tl-container" id="tl-container">
        {timeline_html}
    </div>
    <button id="scrollToTopBtn" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">ページ上部へ</button>
    <script src="timeline.js"></script>
</body>
</html>'''

    os.makedirs('content', exist_ok=True)
    write_if_changed('content/timeline.html', html_content)
    print('HTMLファイルが生成されました: リリース履歴')

if __name__ == '__main__':
    generate_html()
