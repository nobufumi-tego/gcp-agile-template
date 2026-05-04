#!/usr/bin/env python
"""
scripts/install_spec.py

外部から仕様書バンドルを取り込むためのCLI。3 つのソースに対応:
  - ローカルパス        : python scripts/install_spec.py /path/to/bundle
  - .zip                : python scripts/install_spec.py /path/to/bundle.zip
  - Git URL             : python scripts/install_spec.py https://github.com/po/specs.git
                          オプション: --subdir <path/inside/repo>
                                    --ref <branch-or-tag>

バンドルは spec.toml を含むディレクトリで、`docs/` サブツリーに配置したい仕様書を持つ。

  bundle/
    spec.toml             # [spec].name は必須
    README.md
    docs/
      adr/ADR-NNN-*.md
      sprints/sprint-N/specs/<story>.md
      sprints/sprint-N/plans/<story>-plan.md
      ...

実行内容:
  1. ソース → 一時領域にステージング
  2. spec.toml 検証
  3. specs/<name>/ に**バンドル全体を凍結**コピー（再取り込みは --force なしでも上書き）
  4. <bundle>/docs/** を プロジェクトの docs/** にマージ
     - 既存ファイルと内容が違うとコンフリクト → スキップ＋警告
     - --force で上書き
     - 内容同一ならスキップ（idempotent）
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _source import DEFAULT_IGNORE, stage_from_source  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = ROOT / "specs"
DOCS_DIR = ROOT / "docs"


@dataclass
class InstallResult:
    name: str
    copied: list[str] = field(default_factory=list)
    skipped_same: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


def _err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def _validate_manifest(bundle_root: Path) -> dict:
    manifest_path = bundle_root / "spec.toml"
    if not manifest_path.exists():
        raise ValueError(
            f"{manifest_path} が見つかりません。spec.toml を含むディレクトリを指定してください"
        )
    data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    if "spec" not in data or "name" not in data["spec"]:
        raise ValueError("spec.toml に [spec].name がありません")
    return data


def _merge_docs(
    bundle_docs: Path, dest_docs: Path, *, force: bool, result: InstallResult
) -> None:
    """bundle_docs 配下のファイルを dest_docs にマージ。"""
    if not bundle_docs.exists():
        return

    for src_file in bundle_docs.rglob("*"):
        if src_file.is_dir():
            continue
        rel = src_file.relative_to(bundle_docs)
        dest_file = dest_docs / rel
        rel_display = str(rel).replace("\\", "/")

        if dest_file.exists():
            same_content = (
                dest_file.read_bytes() == src_file.read_bytes()
            )
            if same_content:
                result.skipped_same.append(rel_display)
                continue
            if not force:
                result.conflicts.append(rel_display)
                continue
            # force: 上書き
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        result.copied.append(rel_display)


def install(
    source: str,
    *,
    subdir: str | None = None,
    ref: str | None = None,
    force: bool = False,
) -> InstallResult:
    SPECS_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="install-spec-") as tmp:
        stage = Path(tmp)
        bundle_root = stage_from_source(source, subdir=subdir, ref=ref, stage=stage)

        manifest = _validate_manifest(bundle_root)
        name = manifest["spec"]["name"]
        result = InstallResult(name=name)

        # specs/<name>/ に凍結コピー（既存があれば消して再配置）
        frozen_dest = SPECS_DIR / name
        if frozen_dest.exists():
            shutil.rmtree(frozen_dest)
        shutil.copytree(bundle_root, frozen_dest, ignore=DEFAULT_IGNORE)

        # docs/ にマージ
        _merge_docs(
            frozen_dest / "docs", DOCS_DIR, force=force, result=result
        )

        return result


def main() -> int:
    p = argparse.ArgumentParser(description="仕様書バンドルを specs/ と docs/ に取り込む")
    p.add_argument("source", help="ローカルパス・.zip・Git URL のいずれか")
    p.add_argument("--subdir", help="ソース内の相対パス（モノレポ対応）")
    p.add_argument("--ref", help="Git の branch/tag（Git URL のときのみ有効）")
    p.add_argument("--force", action="store_true", help="既存 docs/ ファイルを上書き")
    args = p.parse_args()

    try:
        result = install(args.source, subdir=args.subdir, ref=args.ref, force=args.force)
    except (ValueError, subprocess.CalledProcessError) as e:
        _err(str(e))
        return 1

    print(f"\n[OK] installed spec bundle: {result.name} -> specs/{result.name}/")
    if result.copied:
        print(f"\n  copied to docs/ ({len(result.copied)}):")
        for f in result.copied:
            print(f"    + docs/{f}")
    if result.skipped_same:
        print(f"\n  skipped (same content) ({len(result.skipped_same)}):")
        for f in result.skipped_same:
            print(f"    = docs/{f}")
    if result.conflicts:
        print(f"\n  CONFLICTS ({len(result.conflicts)}) - 既存ファイルと内容が異なります:")
        for f in result.conflicts:
            print(f"    ! docs/{f}")
        print("\n  --> 確認のうえ --force で上書きするか、手動でマージしてください")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
