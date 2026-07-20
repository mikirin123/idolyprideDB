import csv
from utils import write_page, esc, seo_meta_html, breadcrumb_jsonld, FONT_PRECONNECT_HTML


def load_songs():
    songs = []
    with open('data/music.csv', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get('曲名') or '').strip()
            if not title:
                continue
            songs.append(row)
    return songs


def load_cds():
    cds = []
    with open('data/cd.csv', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('CD名') or '').strip()
            if not name:
                continue
            cds.append(row)
    return cds


def generate_html():
    songs = load_songs()
    cds = load_cds()

    song_id_by_title = {}
    for i, song in enumerate(songs):
        title = (song.get('曲名') or '').strip()
        song_id = (song.get('id') or '').strip() or str(i)
        song_id_by_title.setdefault(title, song_id)

    cards_html = ''
    for cd in cds:
        name = cd.get('CD名', '')
        cd_type = cd.get('種類', '')
        image = (cd.get('画像') or '').strip()
        comment = cd.get('一言', '')
        tracks = [t.strip() for t in (cd.get('収録楽曲') or '').split(';') if t.strip()]

        tracks_html = ''.join(
            f'<li><a href="../content/music_list.html#song-{esc(song_id_by_title.get(track, ""))}">{esc(track)}</a></li>'
            for track in tracks
        ) if tracks else '<li>-</li>'

        image_html = (
            f'<img src="{esc(image)}" class="cd-cover" alt="{esc(name)}" loading="lazy" onerror="this.style.display=\'none\'">'
            if image else ''
        )
        type_badge = f'<span class="cd-type-badge cd-type-{esc(cd_type)}">{esc(cd_type)}</span>' if cd_type else ''

        cards_html += f'''            <div class="cd-card" id="cd-{esc(name)}">
                {image_html}
                <div class="cd-body">
                    <h3 class="cd-name">{esc(name)} {type_badge}</h3>
                    <p class="cd-comment">{esc(comment)}</p>
                    <ul class="cd-tracklist">{tracks_html}</ul>
                </div>
            </div>\n'''

    page_description = "IDOLY PRIDEのCD情報一覧です。収録楽曲やジャケット画像を確認できます。"
    page_title = "CD情報 - IDOLY PRIDE データベース M"
    seo_html = seo_meta_html('content/cd_list.html', page_title, page_description)
    breadcrumb_html = breadcrumb_jsonld([
        ('IDOLY PRIDE データベース M', ''),
        ('CD情報', 'content/cd_list.html'),
    ])

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="IDOLY PRIDE, CD情報, ディスコグラフィー, データベース">
    <title>{page_title}</title>
    {seo_html}
    {FONT_PRECONNECT_HTML}
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="cd_list.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    {breadcrumb_html}
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - CD情報</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">CD情報</div>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>CD情報</nav>
    <div class="container">
        <div class="cd-grid">
{cards_html}        </div>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script src="cd_list.js"></script>
</body>
</html>'''

    write_page('content/cd_list.html', html_content)


if __name__ == '__main__':
    generate_html()
    print('HTMLファイルが生成されました: CD情報')
