"""
scripts 共通: 外部ソース（ローカルパス・.zip・Git URL）の取得。

install_module.py / install_spec.py が共有する。
"""
from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path


def is_url(source: str) -> bool:
    return source.startswith(("http://", "https://", "git@", "git+"))


def clone_git(url: str, ref: str | None, dest: Path) -> None:
    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [url, str(dest)]
    subprocess.run(cmd, check=True)


def stage_from_source(
    source: str,
    *,
    subdir: str | None,
    ref: str | None,
    stage: Path,
) -> Path:
    """
    source を一時領域 stage に展開し、本体ディレクトリを返す。

    - ローカルディレクトリ → そのまま参照（コピーしない、呼び出し側でコピー）
    - .zip                  → stage/_zip に展開
    - Git URL              → stage/_clone に clone

    subdir 指定時はその相対パスへ降りる。
    """
    src = Path(source)

    if is_url(source):
        clone_dest = stage / "_clone"
        clone_git(source, ref, clone_dest)
        candidate = clone_dest
    elif src.is_file() and src.suffix == ".zip":
        zip_dest = stage / "_zip"
        zip_dest.mkdir(parents=True)
        with zipfile.ZipFile(src) as z:
            z.extractall(zip_dest)
        # 単一トップレベルディレクトリの場合はそこへ降りる（よくある zip 構造）
        children = [c for c in zip_dest.iterdir() if not c.name.startswith(".")]
        if len(children) == 1 and children[0].is_dir():
            candidate = children[0]
        else:
            candidate = zip_dest
    elif src.is_dir():
        candidate = src
    else:
        raise ValueError(f"unsupported source: {source}")

    if subdir:
        candidate = candidate / subdir
        if not candidate.exists():
            raise ValueError(f"subdir {subdir} がソース内に存在しません")

    return candidate


# .git や Python キャッシュなど、コピーしたくないファイル/ディレクトリのデフォルト除外
DEFAULT_IGNORE = shutil.ignore_patterns(
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "node_modules",
    ".svelte-kit",
    "build",
)
