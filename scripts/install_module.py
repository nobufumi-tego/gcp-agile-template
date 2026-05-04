#!/usr/bin/env python
"""
scripts/install_module.py

外部からモジュールを取り込むためのCLI。3 つのソースに対応:
  - ローカルパス        : python scripts/install_module.py /path/to/module-dir
  - .zip                : python scripts/install_module.py /path/to/module.zip
  - Git URL             : python scripts/install_module.py https://github.com/user/repo.git
                          オプション: --subdir <path/inside/repo>
                                    --ref <branch-or-tag>

ソース直下に module.toml が必要。なければエラー。
取り込み先: <project-root>/modules/<name>/   （name は module.toml から取得）
既存モジュールがあると --force が無いと失敗する。

実行手順:
  1. 一時ディレクトリにソースを配置（git clone / zip 展開 / コピー）
  2. module.toml を検証（[module].name 必須）
  3. modules/<name>/ にコピー
  4. 必要なら hint を表示（npm run modules:sync を実行など）
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

# scripts/ を sys.path に追加（_source 共通モジュールを import するため）
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _source import DEFAULT_IGNORE, stage_from_source  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT / "modules"


def _err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def _validate_manifest(module_root: Path) -> dict:
    manifest_path = module_root / "module.toml"
    if not manifest_path.exists():
        raise ValueError(
            f"{manifest_path} が見つかりません。module.toml を含むディレクトリを指定してください"
        )
    data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    if "module" not in data or "name" not in data["module"]:
        raise ValueError("module.toml に [module].name がありません")
    return data


def install(source: str, *, subdir: str | None = None, ref: str | None = None, force: bool = False) -> str:
    MODULES_DIR.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="install-module-") as tmp:
        stage = Path(tmp)
        module_root = stage_from_source(source, subdir=subdir, ref=ref, stage=stage)

        manifest = _validate_manifest(module_root)
        name = manifest["module"]["name"]
        dest = MODULES_DIR / name

        if dest.exists():
            if not force:
                raise FileExistsError(
                    f"{dest} は既に存在します。--force で上書きしてください"
                )
            shutil.rmtree(dest)

        shutil.copytree(module_root, dest, ignore=DEFAULT_IGNORE)
        return name


def main() -> int:
    p = argparse.ArgumentParser(description="モジュールを modules/ に取り込む")
    p.add_argument("source", help="ローカルパス・.zip・Git URL のいずれか")
    p.add_argument("--subdir", help="ソース内の相対パス（モノレポ対応）")
    p.add_argument("--ref", help="Git の branch/tag（Git URL のときのみ有効）")
    p.add_argument("--force", action="store_true", help="既存モジュールを上書き")
    args = p.parse_args()

    try:
        name = install(args.source, subdir=args.subdir, ref=args.ref, force=args.force)
    except (ValueError, FileExistsError, subprocess.CalledProcessError) as e:
        _err(str(e))
        return 1

    print(f"\n[OK] installed module: {name} -> modules/{name}/")
    print("\nnext steps:")
    print("  1. backend は再起動で自動 include される")
    print(f"  2. modules/{name}/frontend/ がある場合は: cd frontend && npm run modules:sync")
    print(f"  3. テスト: backend/.venv/Scripts/pytest.exe modules/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
