"""GitHubにpushするために必要なファイルだけを別フォルダにまとめるスクリプト。

A_DB(DBバックアップ)や Y_*.py(個人用の管理・画像加工ツール)、
gitignore/ 内のキャッシュ・ハッシュファイルなど、サイトの生成・公開に
不要なものは除外してコピーする。
"""

import os
import shutil
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = Path(r"C:\Users\oya02\Documents\GitHub\idolyprideDB")

# トップレベルで丸ごと除外するディレクトリ(個人用ツール・キャッシュ・バックアップ)
EXCLUDE_DIRS = {
    '.git', '.claude', '__pycache__', 'A_DB', 'A_ページ作成', 'backup',
}

# 除外するファイル名(個人用の管理ツールやローカル専用の設定)
EXCLUDE_FILES = {
    'Y_アイドル管理.py',
    'Y_画像加工.py',
    'Y_IPDB.code-workspace',
    'Z_不足イラスト.txt',
    'Z_不足能力詳細.txt',
    'config.ini',
    'game_data.db',
}

# 除外する拡張子(作業用コピー・ビルドキャッシュ)
EXCLUDE_SUFFIXES = {'.xlsx', '.hash'}


def should_skip_dir(rel_dir):
    return rel_dir.parts and rel_dir.parts[0] in EXCLUDE_DIRS


def should_skip_file(rel_file):
    if rel_file.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    if rel_file.name in EXCLUDE_FILES:
        return True
    if rel_file.parts[0] == 'gitignore':
        # gitignore/ 配下は全てローカル専用(キャッシュ・ハッシュに加え、
        # setting.txt はCSV取得元URLを含むためGitHub側にはコピーしない。
        # Actions側では secrets から実行時に生成する)
        return True
    return False


def collect(output_dir):
    """必要なファイルを出力先へ上書きコピーする(削除は行わない)。

    OneDrive等の同期フォルダでは、フォルダを事前削除する方式は
    同期ロックで PermissionError になることがあるため、
    既存ファイルは上書きするだけにとどめ、ソース側から消えた
    ファイルは stale_files として報告するだけにする。
    """
    output_dir = output_dir.resolve()
    if output_dir == SOURCE_ROOT or SOURCE_ROOT in output_dir.parents:
        raise ValueError(f"出力先はプロジェクトフォルダの外を指定してください: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    wanted_files = set()
    copied = 0
    for dirpath, dirnames, filenames in os.walk(SOURCE_ROOT):
        rel_dir = Path(dirpath).relative_to(SOURCE_ROOT)
        if should_skip_dir(rel_dir):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d != '__pycache__']

        for name in filenames:
            rel_file = rel_dir / name
            if should_skip_file(rel_file):
                continue
            wanted_files.add(rel_file)
            src = Path(dirpath) / name
            dst = output_dir / rel_file
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1

    # 出力先のうち、今回コピー対象になっているトップレベルの
    # ディレクトリ/ファイルの範囲内で、ソースにもう存在しないものを報告する
    managed_tops = {rel.parts[0] for rel in wanted_files}
    stale_files = []
    for dirpath, dirnames, filenames in os.walk(output_dir):
        rel_dir = Path(dirpath).relative_to(output_dir)
        if rel_dir.parts and rel_dir.parts[0] not in managed_tops:
            dirnames[:] = []
            continue
        for name in filenames:
            rel_file = rel_dir / name
            if rel_file.parts[0] in managed_tops and rel_file not in wanted_files:
                stale_files.append(rel_file)

    return output_dir, copied, stale_files


if __name__ == "__main__":
    result_dir, count, stale = collect(OUTPUT_DIR)
    print(f"{count}個のファイルを {result_dir} にコピーしました(既存ファイルは上書きのみ、削除は行っていません)")
    if stale:
        print(f"ソース側に無くなった古いファイルが{len(stale)}件あります(手動で確認・削除してください):")
        for f in stale:
            print(f"  {f}")
