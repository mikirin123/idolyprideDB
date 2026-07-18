import csv
import io
import os
import urllib.request
from datetime import datetime

CACHE_PATH = 'gitignore/cache_characters.csv'


def _load_setting(key):
    try:
        with open('gitignore/setting.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith(f'{key}='):
                    val = line.split('=', 1)[1].strip()
                    return val if val else None
    except FileNotFoundError:
        pass
    return None


def load_characters():
    # generate.py がビルド開始時に一度だけ取得・キャッシュ済みの場合、
    # 13個のサブプロセスそれぞれが同じCSVを再取得しに行く無駄を避ける
    if os.environ.get('IPDB_CHARACTERS_PREFETCHED') == '1' and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r', encoding='utf-8', newline='') as f:
            content = f.read()
        return _parse_characters(content)

    url = _load_setting('CHARACTERS_CSV_URL')
    if not url:
        raise ValueError("CHARACTERS_CSV_URL が gitignore/setting.txt に見つかりません")
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8-sig')
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        # newline='' を指定しないと、セル内改行(\r)を含む行がWindowsの
        # 改行コード変換で書き込み→読み込みの往復時に二重変換され、
        # 空行が挿入されてCSVが壊れる
        with open(CACHE_PATH, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
    except Exception as e:
        print(f"警告: URLからの取得に失敗しました ({e})。キャッシュを使用します。")
        with open(CACHE_PATH, 'r', encoding='utf-8', newline='') as f:
            content = f.read()
    return _parse_characters(content)


def _parse_characters(content):
    reader = csv.reader(io.StringIO(content))
    next(reader)  # ヘッダー行をスキップ

    date_limit = None
    date_limit_str = _load_setting('IMPL_DATE_LIMIT')
    if date_limit_str:
        for fmt in ('%Y/%m/%d', '%Y-%m-%d'):
            try:
                date_limit = datetime.strptime(date_limit_str, fmt)
                break
            except ValueError:
                continue
        if date_limit:
            print(f"[dev] IMPL_DATE_LIMIT={date_limit_str} : 実装日フィルタを適用します")
        else:
            print(f"警告: IMPL_DATE_LIMIT の形式が不正です ({date_limit_str})。YYYY/MM/DD または YYYY-MM-DD 形式で指定してください。")

    rows = []
    for row in reader:
        try:
            int(row[1])
        except (ValueError, IndexError):
            # スプレッドシート中の空行・区切り行はスキップするだけにする。
            # break だと、その行より後ろの全アイドルが黙って消えてしまう。
            continue
        if any(cell.startswith('#') for cell in row):
            # '#' 始まりのセルは「ここで読み込みを終了する」という
            # 意図的な終端マーカーなので break のままにする。
            break
        if len(row) > 3 and not row[3].strip():
            # カード名が空 = まだ未入力の行なので、それ以降は続きがないとみなして終了する。
            break
        if date_limit and len(row) > 24 and row[24]:
            for fmt in ('%Y/%m/%d', '%Y-%m-%d'):
                try:
                    if datetime.strptime(row[24], fmt) > date_limit:
                        row = None
                    break
                except ValueError:
                    continue
            if row is None:
                continue
        rows.append(tuple(row))
    return rows
