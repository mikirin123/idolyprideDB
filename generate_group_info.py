import csv
import os
from utils import (
    write_page, esc,
    seo_meta_html, breadcrumb_jsonld, FONT_PRECONNECT_HTML, IN_ARTICLE_AD_HTML,
)


def load_groups():
    groups = []
    with open('data/group.csv', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('グループ名') or '').strip()
            if not name:
                continue
            members = [m.strip() for m in (row.get('メンバー') or '').split(';') if m.strip()]
            groups.append((name, members))
    return groups


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


def build_group_songs(songs):
    """グループ名 -> 楽曲リスト（曲名, 曲ID）"""
    group_songs = {}
    for i, song in enumerate(songs):
        song_id = (song.get('id') or '').strip() or str(i)
        group_name = (song.get('グループ') or '').strip()
        if group_name:
            group_songs.setdefault(group_name, []).append((song['曲名'], song_id))
    return group_songs


def generate_html():
    groups = load_groups()
    songs = load_songs()
    group_songs = build_group_songs(songs)

    toc_html = ''
    for name, _ in groups:
        toc_html += f'''
    <a class="toc-btn-wrap" href="../group/{esc(name)}.html">
        <div class="toc-label">{esc(name)}</div>
    </a>
    '''

    grouplist_description = 'IDOLY PRIDEのグループ情報一覧です。メンバーと歌唱曲を確認できます。'
    grouplist_title = 'グループ情報 - IDOLY PRIDE データベース M'
    grouplist_seo_html = seo_meta_html('content/group_list.html', grouplist_title, grouplist_description)
    grouplist_breadcrumb_html = breadcrumb_jsonld([
        ('IDOLY PRIDE データベース M', ''),
        ('グループ情報', 'content/group_list.html'),
    ])

    list_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{grouplist_description}">
    <meta name="keywords" content="IDOLY PRIDE, グループ情報, データベース">
    <title>{grouplist_title}</title>
    {grouplist_seo_html}
    {FONT_PRECONNECT_HTML}
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="group_list.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    {grouplist_breadcrumb_html}
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - グループ情報</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">グループ情報</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>グループ情報</nav>
    <div class="container">
        <nav class="toc"><div class="toc-buttons group-toc-buttons">{toc_html}</div></nav>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script src="group_list.js"></script>
</body>
</html>'''
    write_page('content/group_list.html', list_html)

    os.makedirs('group', exist_ok=True)
    for name, members in groups:
        members_html = ''.join(
            f'''<a href="../character/{esc(m)}.html" class="idol-item">
                <img src="../image/circle_icon/{esc(m)}.webp" alt="{esc(m)}" onerror="this.style.display='none'">
                <span>{esc(m)}</span>
            </a>''' for m in members
        )

        my_songs = group_songs.get(name, [])
        songs_html = ''.join(
            f'<li><a href="../content/music_list.html#song-{esc(i)}">{esc(title)}</a></li>'
            for title, i in my_songs
        ) if my_songs else '<li>-</li>'

        group_page_url = f'group/{name}.html'
        group_description = f'IDOLY PRIDE {esc(name)}のグループ情報ページです。メンバーと歌唱曲を掲載しています。'
        group_title = f'{esc(name)} - IDOLY PRIDE データベース M'
        group_seo_html = seo_meta_html(group_page_url, group_title, group_description)
        group_breadcrumb_html = breadcrumb_jsonld([
            ('IDOLY PRIDE データベース M', ''),
            ('グループ情報', 'content/group_list.html'),
            (name, group_page_url),
        ])

        group_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{group_description}">
    <meta name="keywords" content="IDOLY PRIDE, グループ情報, {esc(name)}, データベース">
    <title>{group_title}</title>
    {group_seo_html}
    {FONT_PRECONNECT_HTML}
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="group.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    {group_breadcrumb_html}
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - グループ情報 - {esc(name)}</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">{esc(name)}</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span><a href="../content/group_list.html">グループ情報</a><span>›</span>{esc(name)}</nav>
    <div class="container">
        <h2 class="group-name">{esc(name)}</h2>
        <div class="char-section">
            <h2 class="mokuji">メンバー</h2>
            <div class="idol-list">{members_html}</div>
        </div>
        {IN_ARTICLE_AD_HTML}
        <div class="char-section">
            <h2 class="mokuji">楽曲</h2>
            <ul class="song-list">{songs_html}</ul>
        </div>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script src="group.js"></script>
</body>
</html>'''
        write_page(f'group/{name}.html', group_html)


if __name__ == '__main__':
    generate_html()
    print('HTMLファイルが生成されました: グループ情報')
