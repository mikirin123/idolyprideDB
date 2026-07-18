import hashlib
import html
import os

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
