import hashlib
import html
import os
from datetime import datetime

WEEKDAYS_JA = ['月', '火', '水', '木', '金', '土', '日']

# キャラプロフィール(data/profiles.json)が未登録のときのフォールバック値。
# generate_detail.py と generate_char_info.py の両方で使うため共通化している。
DEFAULT_PROFILE = ["-", "-", "-", "-", "-", "-", "", "", "", "-", "-", "", "", "-", "", "", "-", "", "", "", "", "-"]


def esc(value):
    """CSV/JSONなど外部データ由来の文字列をHTMLに埋め込む前にエスケープする。"""
    return html.escape(str(value), quote=True)


def esc_rich(value):
    """スキル効果文など、意図的に<br>改行タグだけを含むCSVテキスト用のエスケープ。
    それ以外のHTMLはすべてエスケープしつつ、<br>だけは改行として復元する。"""
    escaped = html.escape(str(value), quote=True)
    return escaped.replace('&lt;br&gt;', '<br>')


def build_char_options_html(characters):
    seen = set()
    options = []
    for c in characters:
        name = c[2]
        if name not in seen:
            seen.add(name)
            options.append(f'<option value="{esc(name)}">{esc(name)}</option>')
    return '\n'.join(options)


def write_if_changed(path, content):
    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    hash_path = f'gitignore/{os.path.basename(path)}.hash'
    os.makedirs('gitignore', exist_ok=True)
    if os.path.exists(path) and os.path.exists(hash_path):
        with open(hash_path, 'r') as f:
            if f.read().strip() == new_hash:
                print(f"変更なし: {path} をスキップ")
                return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    with open(hash_path, 'w') as f:
        f.write(new_hash)
    return True


def _format_footer_date(dt):
    return f"{dt.year}/{dt.month}/{dt.day}({WEEKDAYS_JA[dt.weekday()]}) {dt.strftime('%H:%M')}"


def _get_last_updated(path, content):
    """contentのハッシュが前回記録時から変わっていなければ、前回の最終更新日時を
    そのまま返す。フッター自体の文言はcontentに含めずに判定するため、実質的な
    変更が無い再生成では日時が動かず、write_if_changedの無駄な書き込み抑止とも
    整合する。"""
    meta_path = f'gitignore/{os.path.basename(path)}.updated'
    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    os.makedirs('gitignore', exist_ok=True)
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        if len(lines) == 2 and lines[0] == new_hash:
            return datetime.fromisoformat(lines[1])
    now = datetime.now()
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(f'{new_hash}\n{now.isoformat()}')
    return now


def write_page(path, content):
    """ページ内容が実際に変わった日時を示すフッターを</body>直前に挿入してから書き出す。"""
    last_updated = _get_last_updated(path, content)
    footer = f'<footer class="site-footer">最終更新: {_format_footer_date(last_updated)}</footer>\n'
    if '</body>' in content:
        content = content.replace('</body>', footer + '</body>', 1)
    else:
        content += footer
    return write_if_changed(path, content)
