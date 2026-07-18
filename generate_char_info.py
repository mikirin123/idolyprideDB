import csv
import json
import os
from utils import write_if_changed, esc, DEFAULT_PROFILE
from db import load_characters

PROFILE_FIELDS = [
    'CV', '誕生日', '星座', '年齢', '身長', '体重',
    'スリーサイズB', 'スリーサイズW', 'スリーサイズH', '学校',
    '好き1', '好き2', '好き3', '嫌い1', '嫌い2', '嫌い3',
    '趣味1', '趣味2', '趣味3', '趣味4', '趣味5', 'その他',
]


def load_profiles():
    with open('data/profiles.json', 'r', encoding='utf-8') as f:
        return json.load(f)


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


def build_char_groups(groups):
    """キャラ名 -> 所属グループ名リスト"""
    char_groups = {}
    for group_name, members in groups:
        for member in members:
            char_groups.setdefault(member, []).append(group_name)
    return char_groups


def build_char_songs(songs):
    """キャラ名 -> 歌唱曲リスト（曲名, 曲ID）"""
    char_songs = {}
    for i, song in enumerate(songs):
        song_id = (song.get('id') or '').strip() or str(i)
        singers = [s.strip() for s in (song.get('歌唱メンバー') or '').split(';') if s.strip()]
        for singer in singers:
            char_songs.setdefault(singer, []).append((song['曲名'], song_id))
    return char_songs


def load_profile_ids():
    ids = {}
    try:
        with open('data/profiles.csv', encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                name = row.get('キャラ名')
                id_str = row.get('id')
                if name and id_str:
                    ids[name] = int(id_str)
    except FileNotFoundError:
        pass
    return ids


def write_profiles_csv(char_names, profiles, char_groups, profile_ids):
    os.makedirs('data', exist_ok=True)
    with open('data/profiles.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'キャラ名'] + PROFILE_FIELDS + ['所属グループ'])
        for name in char_names:
            profile = profiles.get(name, DEFAULT_PROFILE)
            groups = ';'.join(char_groups.get(name, []))
            writer.writerow([profile_ids[name], name] + list(profile) + [groups])


def generate_html():
    characters = load_characters()
    profiles = load_profiles()
    groups = load_groups()
    songs = load_songs()
    char_groups = build_char_groups(groups)
    char_songs = build_char_songs(songs)

    char_names = []
    seen = set()
    char_cards = {}
    for c in characters:
        name = c[2]
        if name not in seen:
            seen.add(name)
            char_names.append(name)
        char_cards.setdefault(name, []).append(c)

    # プロフィールのみ登録されていてアイドルカードを持たないキャラ（ゲスト出演等）も含める
    profile_only_names = [name for name in profiles if name not in seen]

    # 表示順はdata/profiles.csvのidを正とする。新規キャラは末尾に追加する
    profile_ids = load_profile_ids()
    next_id = max(profile_ids.values(), default=0)
    for name in char_names + profile_only_names:
        if name not in profile_ids:
            next_id += 1
            profile_ids[name] = next_id
    char_names.sort(key=lambda name: profile_ids[name])

    write_profiles_csv(
        sorted(char_names + profile_only_names, key=lambda name: profile_ids[name]),
        profiles, char_groups, profile_ids,
    )

    toc_html = ''
    for name in char_names:
        toc_html += f'''
    <a class="toc-btn-wrap" href="../character/{esc(name)}.html">
        <img src="../image/circle_icon/{esc(name)}.webp" alt="{esc(name)}" class="toc-icon">
        <div class="toc-label">{esc(name)}</div>
    </a>
    '''

    list_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="IDOLY PRIDEのキャラクター情報一覧です。プロフィール、所属グループ、歌唱曲を確認できます。">
    <meta name="keywords" content="IDOLY PRIDE, キャラ情報, プロフィール, グループ, データベース">
    <title>キャラ情報 - IDOLY PRIDE データベース M</title>
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="chara_list.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - キャラ情報</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">キャラ情報</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span>キャラ情報</nav>
    <div class="container">
        <nav class="toc"><div class="toc-buttons">{toc_html}</div></nav>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script src="chara_list.js"></script>
</body>
</html>'''
    write_if_changed('content/chara_list.html', list_html)

    os.makedirs('character', exist_ok=True)
    for name in char_names:
        profile = profiles.get(name, DEFAULT_PROFILE)
        likes = ' '.join(x for x in profile[10:13] if x)
        dislikes = ' '.join(x for x in profile[13:16] if x)
        hobbies = ' '.join(x for x in profile[16:21] if x)
        three_size = '-'.join(x for x in profile[6:9] if x) or '-'

        my_groups = char_groups.get(name, [])
        groups_html = '、'.join(
            f'<a href="../group/{esc(g)}.html">{esc(g)}</a>' for g in my_groups
        ) if my_groups else '-'

        cards_html = ''.join(
            f'''<a href="../detail/{esc(c[2])} {esc(c[3])}.html" class="idol-item{' data-incomplete' if c[0] == '★' else ''}">
                <img src="../image/idol/{esc(c[2])} {esc(c[3])}.webp" alt="{esc(c[3])} {esc(c[2])}" onerror="this.style.display='none'">
                <span>{esc(c[3])}</span>
            </a>''' for c in char_cards.get(name, [])
        )

        my_songs = char_songs.get(name, [])
        songs_html = ''.join(
            f'<li><a href="../content/music_list.html#song-{esc(i)}">{esc(title)}</a></li>'
            for title, i in my_songs
        ) if my_songs else '<li>-</li>'

        char_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="IDOLY PRIDE {esc(name)}のキャラクター情報ページです。プロフィール、所属グループ、アイドル一覧、歌唱曲を掲載しています。">
    <meta name="keywords" content="IDOLY PRIDE, キャラ情報, {esc(name)}, データベース">
    <title>{esc(name)} - IDOLY PRIDE データベース M</title>
    <link rel="stylesheet" href="../common.css">
    <link rel="stylesheet" href="character.css">
    <link rel="shortcut icon" href="../image/icon.ico">
    <link rel="icon" type="image/png" sizes="192x192" href="../image/icon.png">
    <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="../image/icon.png">
    <link rel="mask-icon" href="../image/icon.svg">
</head>
<body>
    <div class="banner">
        <div class="banner_title" onclick="location.href='../index.html'" style="cursor:pointer">IDOLY PRIDE データベース M - キャラ情報 - {esc(name)}</div>
        <div class="banner_title_phone" onclick="location.href='../index.html'" style="cursor:pointer">{esc(name)}</div>
        <a href="javascript:history.back()" class="back-button">戻る</a>
    </div>
    <nav class="breadcrumb"><a href="../index.html">トップ</a><span>›</span><a href="../content/chara_list.html">キャラ情報</a><span>›</span>{esc(name)}</nav>
    <div class="container">
        <div class="char-profile-card">
            <img src="../image/circle_icon/{esc(name)}.webp" class="char-icon" alt="{esc(name)}" onerror="this.style.display='none'">
            <h2 class="char-name">{esc(name)}</h2>
            <table class="profile-table">
                <tr><th>CV</th><td>{esc(profile[0])}</td></tr>
                <tr><th>誕生日</th><td>{esc(profile[1])}</td></tr>
                <tr><th>星座</th><td>{esc(profile[2])}</td></tr>
                <tr><th>年齢</th><td>{esc(profile[3])}</td></tr>
                <tr><th>身長</th><td>{esc(profile[4])}</td></tr>
                <tr><th>体重</th><td>{esc(profile[5])}</td></tr>
                <tr><th>スリーサイズ</th><td>{esc(three_size)}</td></tr>
                <tr><th>学校</th><td>{esc(profile[9])}</td></tr>
                <tr><th>好き</th><td>{esc(likes)}</td></tr>
                <tr><th>嫌い</th><td>{esc(dislikes)}</td></tr>
                <tr><th>趣味</th><td>{esc(hobbies)}</td></tr>
                <tr><th>その他</th><td>{esc(profile[21])}</td></tr>
                <tr><th>所属グループ</th><td>{groups_html}</td></tr>
            </table>
        </div>
        <div class="char-section">
            <h2 class="mokuji">アイドル一覧</h2>
            <div class="idol-list">{cards_html}</div>
        </div>
        <div class="char-section">
            <h2 class="mokuji">歌唱曲</h2>
            <ul class="song-list">{songs_html}</ul>
        </div>
    </div>
    <button id="scrollToTopBtn">ページ上部へ</button>
    <script src="character.js"></script>
</body>
</html>'''
        write_if_changed(f'character/{name}.html', char_html)


if __name__ == '__main__':
    generate_html()
    print('HTMLファイルが生成されました: キャラ情報')
