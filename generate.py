from datetime import datetime
import subprocess
import csv
import io
import re
import urllib.request
import os
from utils import write_if_changed, esc, esc_rich

birthdays = [
    {"name": "長瀬琴乃", "birthday": "12-25"},
    {"name": "伊吹渚", "birthday": "08-03"},
    {"name": "白石沙季", "birthday": "09-26"},
    {"name": "成宮すず", "birthday": "09-13"},
    {"name": "早坂芽衣", "birthday": "07-07"},
    {"name": "川咲さくら", "birthday": "04-03"},
    {"name": "兵藤雫", "birthday": "10-15"},
    {"name": "白石千紗", "birthday": "11-22"},
    {"name": "一ノ瀬怜", "birthday": "03-08"},
    {"name": "佐伯遙子", "birthday": "01-03"},
    {"name": "天動瑠依", "birthday": "11-11"},
    {"name": "鈴村優", "birthday": "02-27"},
    {"name": "奥山すみれ", "birthday": "05-05"},
    {"name": "神崎莉央", "birthday": "08-28"},
    {"name": "井川葵", "birthday": "06-19"},
    {"name": "小美山愛", "birthday": "02-09"},
    {"name": "赤崎こころ", "birthday": "12-06"},
    {"name": "fran", "birthday": "06-11"},
    {"name": "kana", "birthday": "04-10"},
    {"name": "miho", "birthday": "01-25"},
    {"name": "長瀬麻奈", "birthday": "10-09"},
]

today = datetime.today()
today_date = today.date()

closest_person = None
min_diff = None

for person in birthdays:
    month, day = map(int, person["birthday"].split("-"))
    bday_this_year_date = today.replace(month=month, day=day).date()
    if bday_this_year_date < today_date:
        bday_this_year_date = today.replace(year=today.year + 1, month=month, day=day).date()
    diff = bday_this_year_date - today_date
    if min_diff is None or diff < min_diff:
        min_diff = diff
        closest_person = person

month, day = map(int, closest_person["birthday"].split("-"))
birthday_str = f"{month}月{day}日"
days_remaining = min_diff.days
birthday_line = (
    f'<span class="birthday-today">今日は{closest_person["name"]}の誕生日</span>' if days_remaining == 0
    else f'{closest_person["name"]} {birthday_str}<br><span class="birthday-countdown">あと{days_remaining}日</span>'
)

WEEKDAYS_JA = ['月', '火', '水', '木', '金', '土', '日']
UPDATE_INFO_LIMIT = 10
ADMIN_POSTS_LIMIT = 8

# CSVの日付欄は "2025-09-17" と "2025/6/28" が混在しているため両対応する
DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d")


def parse_flexible_date(date_str):
    date_str = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"日付の形式を認識できません: {date_str}")


def parse_flexible_datetime(date_str, time_str):
    date_str = date_str.strip()
    time_str = time_str.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(f"{date_str} {time_str}", f"{fmt} %H:%M")
        except ValueError:
            continue
    raise ValueError(f"日時の形式を認識できません: {date_str} {time_str}")


def format_date_ja(dt):
    """サイト全体で統一する日付表示形式: yyyy/m/d(曜日)"""
    return f"{dt.year}/{dt.month}/{dt.day}({WEEKDAYS_JA[dt.weekday()]})"


def format_date_ja_no_year(dt):
    """開催中のイベント欄用の日付表示形式(年なし): m/d(曜日)"""
    return f"{dt.month}/{dt.day}({WEEKDAYS_JA[dt.weekday()]})"


def load_setting(key):
    with open('gitignore/setting.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith(f'{key}='):
                val = line.split('=', 1)[1].strip()
                return val if val else None
    return None


def fetch_csv_with_cache(url, cache_path):
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8-sig')
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        # newline='' がないと、セル内改行を含む行が書き込み→読み込みの
        # 往復で二重変換されて空行が混入する(Windows特有の既知の罠)
        with open(cache_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        return content
    except Exception as e:
        print(f"警告: URLからの取得に失敗しました ({e})。キャッシュを使用します。")
        with open(cache_path, 'r', encoding='utf-8', newline='') as f:
            return f.read()


def load_update_rows():
    url = load_setting('UPDATE_INFO_CSV_URL')
    if not url:
        raise ValueError("UPDATE_INFO_CSV_URL が gitignore/setting.txt に見つかりません")
    content = fetch_csv_with_cache(url, 'gitignore/cache_update_info.csv')
    return sorted(csv.DictReader(io.StringIO(content)), key=lambda r: r['日付'], reverse=True)


def row_to_update_html(row):
    dt = parse_flexible_date(row['日付'])
    date_ja = format_date_ja(dt)
    description = esc(row['説明'])
    links_str = row['リンクリスト'].strip()

    html = f'<li>{date_ja}</li>\n'
    if links_str:
        link_parts = []
        for item in links_str.split(';'):
            parts = item.strip().split('|', 1)
            if len(parts) == 2:
                text, entry_url = parts
                link_parts.append(f'・<a href="{esc(entry_url.strip())}">{esc(text.strip())}</a>')
        html += f'<p>{description}<br>{"<br>".join(link_parts)}</p>\n'
    else:
        html += f'<p>{description}</p>\n'
    html += '<hr>\n'
    return html


def generate_update_html(rows, section_id):
    visible = rows[:UPDATE_INFO_LIMIT]
    hidden = rows[UPDATE_INFO_LIMIT:]

    html = ''.join(row_to_update_html(r) for r in visible)
    if hidden:
        html += f'<div id="updates-more-{section_id}" style="display:none">\n'
        html += ''.join(row_to_update_html(r) for r in hidden)
        html += '</div>\n'
        html += (
            f'<button class="show-more-btn" '
            f'onclick="document.getElementById(\'updates-more-{section_id}\').style.display=\'block\';'
            f'this.style.display=\'none\'">もっと見る</button>\n'
        )
    return html


def load_admin_posts():
    url = load_setting('ADMIN_POSTS_CSV_URL')
    if not url:
        return []
    try:
        content = fetch_csv_with_cache(url, 'gitignore/cache_admin_posts.csv')
        return sorted(csv.DictReader(io.StringIO(content)), key=lambda r: r.get('日付', ''), reverse=True)
    except Exception:
        return []


EVENT_CATEGORY_CLASS = {
    '定期': 'regular',
    'ガチャ': 'gacha',
    'イベント': 'event',
    'ミッション': 'mission',
    'お仕事キャンペーン': 'job',
    'その他': 'other',
}

# 開催中イベント一覧の並び順: このリストの並び順を優先度とし、区分が同じ場合は日付順にする
EVENT_CATEGORY_PRIORITY = [
    'イベント',
    'ガチャ',
    'お仕事キャンペーン',
    'ミッション',
    'その他',
    'ログインボーナス',
    '定期',
]
EVENT_CATEGORY_ORDER = {name: i for i, name in enumerate(EVENT_CATEGORY_PRIORITY)}

# イベント名の一部をリンクにできるよう「[表示文言](URL)」の記法を許可する
EVENT_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def load_events_rows():
    """開催中のイベント一覧を読み込み、現在時刻を含む期間の行だけをイベント区分優先度順(区分が同じ場合は終了が近い順)で返す。"""
    url = load_setting('EVENTS_CSV_URL')
    if not url:
        return []
    try:
        content = fetch_csv_with_cache(url, 'gitignore/cache_events.csv')
    except Exception:
        return []

    now = datetime.now()
    ongoing = []
    for row in csv.DictReader(io.StringIO(content)):
        try:
            start_dt = parse_flexible_datetime(row['開始日付'], row['開始時間'])
            end_dt = parse_flexible_datetime(row['終了日付'], row['終了時間'])
        except (ValueError, KeyError):
            continue
        if start_dt <= now <= end_dt:
            ongoing.append((row, start_dt, end_dt))
    ongoing.sort(key=lambda t: (
        EVENT_CATEGORY_ORDER.get(t[0].get('イベント区分', '').strip(), len(EVENT_CATEGORY_PRIORITY)),
        t[2],
    ))
    return ongoing


def format_event_rich_text(raw):
    """CSVセル内の実改行に加えて、文字列「<br>」を書いても改行になるようにする。"""
    normalized = raw.replace('\r\n', '\n').replace('\r', '\n')
    escaped = esc_rich(normalized).replace('\n', '<br>')

    def repl(m):
        text, entry_url = m.group(1), m.group(2)
        return f'<a href="{entry_url}" target="_blank" rel="noopener noreferrer">{text}</a>'

    return EVENT_LINK_RE.sub(repl, escaped)


def format_event_period(start_dt, end_dt):
    def fmt(dt):
        return f"{format_date_ja_no_year(dt)} {dt.strftime('%H:%M')}"
    return f"{fmt(start_dt)} ～ {fmt(end_dt)}"


def generate_events_html(ongoing):
    if not ongoing:
        return '<li class="event-empty event-li">現在開催中のイベントはありません</li>\n'

    html = ''
    for row, start_dt, end_dt in ongoing:
        category = row.get('イベント区分', '').strip()
        css_class = EVENT_CATEGORY_CLASS.get(category, 'other')
        description = row.get('説明', '').strip()
        event_desc_html = (
            f'<div class="event-desc">{format_event_rich_text(description)}</div>'
            if description else ''
        )
        html += (
            '<li class="event-item event-li">'
            '<div class="event-item-header">'
            f'<span class="event-badge event-badge-{css_class}">{esc(category)}</span>'
            f'<span class="event-period">{format_event_period(start_dt, end_dt)}</span>'
            '</div>'
            f'<div class="event-name">{format_event_rich_text(row.get("イベント名", ""))}</div>'
            f'{event_desc_html}'
            '</li>\n'
        )
    return html


TWEET_URL_RE = re.compile(r"(?:twitter\.com|x\.com)/[^/]+/status/(\d+)")


def _admin_post_html(row):
    try:
        date_str = format_date_ja(parse_flexible_date(row['日付']))
    except Exception:
        date_str = row.get('日付', '')
    tweet_url = row.get('URL', '').strip()
    if not tweet_url:
        return ''
    header = (
        f'<div class="admin-post-header">'
        f'<span class="admin-post-date">{esc(date_str)}</span>'
        f'<a href="{esc(tweet_url)}" target="_blank" rel="noopener noreferrer" class="admin-post-link">'
        f'<i class="fab fa-twitter"></i> Twitterで見る</a>'
        f'</div>'
    )
    match = TWEET_URL_RE.search(tweet_url)
    if match:
        return (
            f'<li class="admin-post-item admin-post-tweet">'
            f'{header}'
            f'<div class="tweet-lazy-embed" data-tweet-id="{match.group(1)}"></div>'
            f'</li>\n'
        )
    return f'<li class="admin-post-item">{header}</li>\n'


def generate_admin_posts_html(rows):
    if not rows:
        return ''
    visible = rows[:ADMIN_POSTS_LIMIT]
    hidden = rows[ADMIN_POSTS_LIMIT:]
    html = ''.join(filter(None, (_admin_post_html(r) for r in visible)))
    if hidden:
        html += '<div id="admin-posts-more" style="display:none">\n'
        html += ''.join(filter(None, (_admin_post_html(r) for r in hidden)))
        html += '</div>\n'
        html += (
            '<button class="show-more-btn" '
            'onclick="document.getElementById(\'admin-posts-more\').style.display=\'block\';'
            'this.style.display=\'none\'">もっと見る</button>\n'
        )
    return html


def generate_rss(rows):
    site_url = load_setting('SITE_URL') or ''
    items = ''
    for row in rows[:20]:
        dt = datetime.strptime(row['日付'], "%Y-%m-%d")
        weekday = WEEKDAYS_JA[dt.weekday()]
        date_ja = f"{dt.year}年{dt.month}月{dt.day}日({weekday})"
        pub_date = dt.strftime('%a, %d %b %Y 00:00:00 +0900')
        description = row['説明']
        links_str = row['リンクリスト'].strip()
        if links_str:
            link_texts = [item.split('|')[0].strip() for item in links_str.split(';') if '|' in item]
            description += '：' + '、'.join(link_texts)
        items += f'''    <item>
      <title>{esc(date_ja)} の更新</title>
      <description>{esc(description)}</description>
      <pubDate>{pub_date}</pubDate>
      <link>{esc(site_url)}</link>
    </item>
'''
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>IDOLY PRIDE データベース M 更新情報</title>
    <link>{site_url}</link>
    <description>IDOLY PRIDE データベース M の更新情報</description>
    <language>ja</language>
{items}  </channel>
</rss>'''
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss)


NAV_SECTIONS = [
    ("コンテンツ", [
        ("idol_list", "content/idol_list.html", "fa-solid fa-list", "アイドルリスト"),
        ("stats_list", "content/stats_list.html", "fa-solid fa-chart-simple", "ステータスランキング"),
        ("idol_sep_list", "content/idol_sep_list.html", "fa-solid fa-filter", "キャラ別リスト"),
        ("yell_sep_list", "content/yell_sep_list.html", "fa-solid fa-filter", "エール別リスト"),
        ("exp_calculator", "content/exp_calculator.html", "fa-solid fa-calculator", "レスピ計算機"),
        ("skill_list", "content/skill_list.html", "fa-solid fa-wand-magic-sparkles", "スキル一覧"),
        ("compare", "content/compare.html", "fa-solid fa-code-compare", "アイドル比較"),
        ("timeline", "content/timeline.html", "fa-solid fa-timeline", "リリース履歴"),
    ]),
    ("データ", [
        ("exphoto_list", "content/exphoto_list.html", "fa-solid fa-camera", "専用フォト"),
        ("colors", "content/colors.html", "fa-solid fa-palette", "メンバーカラー"),
        ("birthdays", "content/birthdays.html", "fa-solid fa-cake-candles", "キャラ誕生日"),
        ("interact-present", "content/interact-present.html", "fa-solid fa-gift", "プレゼント交流Pt上昇量"),
        ("chara_list", "content/chara_list.html", "fa-solid fa-id-card", "キャラ情報"),
        ("group_list", "content/group_list.html", "fa-solid fa-people-group", "グループ情報"),
        ("music_list", "content/music_list.html", "fa-solid fa-music", "楽曲情報"),
        ("cd_list", "content/cd_list.html", "fa-solid fa-compact-disc", "CD情報"),
    ]),
]

OFFICIAL_NAV_SECTION = ("公式コンテンツ", [
    (None, "https://idolypride.jp/", "fa-solid fa-house", "公式サイト"),
    (None, "https://qualiarts.store/collections/idoly-pride", "fa-solid fa-bag-shopping", "qualiarts store"),
    (None, "https://x.com/idolypride", "fab fa-twitter", "Twitter"),
    (None, "https://www.youtube.com/c/IDOLYPRIDE", "fab fa-youtube", "YouTube"),
])

EVENT_NAV_SECTIONS = [
    ("はちはじ'25", [
        ("circle-list", "event/はちはじ25/circle-list.html", "fa-solid fa-table-list", "サークル一覧"),
        ("oshinagaki", "event/はちはじ25/oshinagaki.html", "fa-solid fa-globe", "おしながき・告知ツイート一覧"),
    ]),
]


def load_page_visibility():
    visibility = {}
    try:
        with open('page_visibility.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, val = line.split('=', 1)
                visibility[key.strip()] = val.strip().lower() != 'hide'
    except FileNotFoundError:
        pass
    return visibility


def build_nav_section(title, items, visibility):
    visible_items = [item for item in items if visibility.get(item[0], True)]
    if not visible_items:
        return ''
    rows = ''.join(
        f'                        <div class="item"><a href="{href}" class="menuu-item"><i class="{icon}"></i> {label}</a></div>\n'
        for _, href, icon, label in visible_items
    )
    return (
        f'                    <h2 class="menuu-head">{title}</h2>\n'
        f'                    <div class="menuu-grid">\n{rows}'
        f'                    </div>'
    )


def build_nav_html(all_sections, visibility):
    sections = [build_nav_section(title, items, visibility) for title, items in all_sections]
    return '\n                    <br>\n'.join(s for s in sections if s)


def generate_html(update_rows, admin_posts, events_rows):
    visibility = load_page_visibility()
    nav_html = build_nav_html(NAV_SECTIONS + [OFFICIAL_NAV_SECTION] + EVENT_NAV_SECTIONS, visibility)

    latest_date_ja = ''
    if update_rows:
        dt = datetime.strptime(update_rows[0]['日付'], "%Y-%m-%d")
        latest_date_ja = f"{dt.year}年{dt.month}月{dt.day}日"

    events_html = generate_events_html(events_rows)
    update_html = generate_update_html(update_rows, 'main')
    admin_posts_html = generate_admin_posts_html(admin_posts)
    admin_posts_display = '' if admin_posts_html else ' style="display:none"'
    has_tweet_embed = 'tweet-lazy-embed' in admin_posts_html
    tweet_widgets_script = (
        '\n    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
        if has_tweet_embed else ''
    )
    tweet_lazyload_script = (
        '\n<script src="tweet_lazyload.js"></script>' if has_tweet_embed else ''
    )

    description = (
        f"スマホゲーム「IDOLYPRIDE」(アイプラ)のデータをまとめるサイトです。"
        f"最終更新: {latest_date_ja}。"
        f"アイドルの誕生日や専用フォト、エール別リストなど、様々な情報を提供しています。"
    )

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="keywords" content="IDOLYPRIDE,アイプラ,データベース,アイドル,誕生日,専用フォト,エール別リスト,ステータスランキング,レスピ計算機">
    <title>IDOLY PRIDE データベース M</title>
    <link rel="stylesheet" href="style.css">
    <link rel="shortcut icon" href="image/icon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="image/icon.png">
    <link rel="mask-icon" href="image/icon.svg">
    <link rel="alternate" type="application/rss+xml" title="更新情報" href="feed.xml">{tweet_widgets_script}
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9647262951514669" crossorigin="anonymous"></script>
    <meta name="google-adsense-account" content="ca-pub-9647262951514669">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
<body>
    <div class="banner">
        <div class="banner_title">IDOLY PRIDE データベース M</div>
        <button class="menu">︙</button>
        <div class="menu-content">
            <a><i class="fa-solid fa-circle-question"></i> このサイトについて</a>
        </div>
    </div>
    <div class="popup-overlay"></div>
    <div class="popup">
        <div class="popup-header"></div>
        <div class="popup-content"></div>
        <button class="popup-close">閉じる</button>
    </div>
    <div class="menuu-container">
        <section class="menuu">
{nav_html}
        </section>
        <aside class="sidebar">
            <div class="news">
                <h2 class="news-head">次の誕生日</h2>
                <span class="birthday"><img src="image/circle_icon/{closest_person["name"]}.webp" class="circle_icon" alt="{closest_person["name"]}"> {birthday_line}</span>
            </div>
            <div class="news events-news">
                <h2 class="news-head">開催中のイベント</h2>
                <ul>
{events_html}</ul>
            </div>
            <div class="news">
                <h2 class="news-head">更新情報</h2>
                <ul>
{update_html}</ul>
            </div>
            <div class="news admin-posts-news"{admin_posts_display}>
                <h2 class="news-head">管理者の投稿</h2>
                <ul>
{admin_posts_html}</ul>
            </div>
        </aside>
    </div>
    <button id="scrollToTopBtn" onclick="scrollToTop()">ページ上部へ</button>
</body>
<script src="script.js"></script>{tweet_lazyload_script}
</html>
'''
    write_if_changed('index.html', html_content)


if __name__ == "__main__":
    update_rows = load_update_rows()
    admin_posts = load_admin_posts()
    events_rows = load_events_rows()
    generate_html(update_rows, admin_posts, events_rows)
    generate_rss(update_rows)
    print("HTMLファイルが生成されました: index.html")
    print("RSSフィードが生成されました: feed.xml")
    scripts = [
        "generate_detail.py",
        "generate_yell_sep_list.py",
        "generate_idol_sep_list.py",
        "generate_stats_list.py",
        "generate_idol_list.py",
        "generate_exphoto_list.py",
        "generate_skill_list.py",
        "generate_compare.py",
        "generate_timeline.py",
        "generate_char_info.py",
        "generate_group_info.py",
        "generate_music_list.py",
        "generate_cd_list.py",
        "generate_sitemap.py",
    ]

    # 各スクリプトが個別にキャラCSVをネットワーク取得すると13回分の無駄な
    # 通信が発生するため、ここで一度だけ取得・キャッシュしてから
    # サブプロセスにキャッシュ利用を指示する
    from db import load_characters
    load_characters()
    child_env = os.environ.copy()
    child_env['IPDB_CHARACTERS_PREFETCHED'] = '1'

    for script in scripts:
        result = subprocess.run(["python", script], env=child_env)
        if result.returncode != 0:
            print(f"警告: {script} が失敗しました (終了コード: {result.returncode})")
