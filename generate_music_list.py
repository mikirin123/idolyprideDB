import csv
from utils import write_page, esc


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


def generate_html():
    songs = load_songs()

    group_names = sorted({(s.get('グループ') or '').strip() for s in songs if s.get('グループ', '').strip()})
    member_names = sorted({
        m.strip()
        for s in songs
        for m in (s.get('歌唱メンバー') or '').split(';')
        if m.strip()
    })

    group_options = '\n'.join(f'                    <option value="{esc(g)}">{esc(g)}</option>' for g in group_names)
    member_options = '\n'.join(f'                    <option value="{esc(m)}">{esc(m)}</option>' for m in member_names)

    rows_html = ''
    for i, song in enumerate(songs):
        song_id = (song.get('id') or '').strip() or str(i)
        title = song.get('曲名', '')
        members = [m.strip() for m in (song.get('歌唱メンバー') or '').split(';') if m.strip()]
        group_name = song.get('グループ', '')
        lyricist = song.get('作詞', '')
        composer = song.get('作曲', '')
        arranger = song.get('編曲', '')
        release_date = song.get('リリース日', '')
        cd_name = song.get('収録CD', '')
        youtube_url = song.get('YouTube(MV)', '').strip()
        cover = song.get('表紙', '').strip()

        members_html = '、'.join(f'<a href="../character/{esc(m)}.html">{esc(m)}</a>' for m in members)
        group_html = f'<a href="../group/{esc(group_name)}.html">{esc(group_name)}</a>' if group_name else ''
        cd_html = f'<a href="../content/cd_list.html#cd-{esc(cd_name)}">{esc(cd_name)}</a>' if cd_name else ''
        youtube_html = f'<a href="{esc(youtube_url)}" target="_blank" rel="noopener noreferrer" class="mv-link"><i class="fa-brands fa-youtube"></i> MV</a>' if youtube_url else ''
        cover_html = f'<img src="{esc(cover)}" class="song-cover" alt="{esc(title)}" loading="lazy" onerror="this.style.display=\'none\'">' if cover else ''
        members_data = '|'.join(members)

        rows_html += f'''            <tr id="song-{esc(song_id)}" data-group="{esc(group_name)}" data-members="{esc(members_data)}">
                <td class="cover-cell">{cover_html}</td>
                <td class="song-name-cell">{esc(title)}</td>
                <td class="group-cell">{group_html}</td>
                <td class="members-cell">{members_html}</td>
                <td>{esc(lyricist)}</td>
                <td>{esc(composer)}</td>
                <td>{esc(arranger)}</td>
                <td class="date-cell">{esc(release_date)}</td>
                <td class="cd-cell">{cd_html}</td>
                <td class="mv-cell">{youtube_html}</td>
            </tr>\n'''

    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="IDOLY PRIDEの楽曲一覧です。グループや歌唱メンバー、作詞作曲編曲でキーワード検索できます。">
    <meta name="keywords" content="IDOLY PRIDE, 楽曲情報, 曲一覧, データベース">
    <title>楽曲情報 - IDOLY PRIDE データベース M</title>
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="music_list.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - 楽曲情報</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">楽曲情報</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>楽曲情報</nav>
    <div class="search-bar-container">
        <div class="search-row">
            <input type="text" id="search-bar" class="search-bar" placeholder="曲名・作詞・作曲・編曲でキーワード検索">
        </div>
        <div id="result-count" class="result-count"></div>
    </div>
    <div class="container">
        <div class="filters">
            <h2>フィルタ</h2>
            <div class="filter-section">
                <h3>グループ</h3>
                <select id="filter-group">
                    <option value="">すべて</option>
{group_options}
                </select>
            </div>
            <div class="filter-section">
                <h3>歌唱メンバー</h3>
                <select id="filter-member">
                    <option value="">すべて</option>
{member_options}
                </select>
            </div>
            <button type="button" class="reset" onclick="resetFilters()">リセット</button>
        </div>
        <div class="table-container">
            <table id="music-table">
                <thead>
                    <tr>
                        <th>表紙</th>
                        <th>曲名</th>
                        <th>グループ</th>
                        <th>歌唱メンバー</th>
                        <th>作詞</th>
                        <th>作曲</th>
                        <th>編曲</th>
                        <th>リリース日</th>
                        <th>収録CD</th>
                        <th>MV</th>
                    </tr>
                </thead>
                <tbody>
{rows_html}                </tbody>
            </table>
        </div>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script src="music_list.js"></script>
</body>
</html>'''

    write_page('content/music_list.html', html_content)


if __name__ == '__main__':
    generate_html()
    print('HTMLファイルが生成されました: 楽曲情報')
