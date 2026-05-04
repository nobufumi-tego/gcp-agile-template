"""
install_spec のテスト。
プロジェクトルートを一時的に差し替えて、specs/ と docs/ の配置を検証する。
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


def _make_bundle(root: Path, *, name: str = "demo", with_adr: bool = True, with_story: bool = True) -> Path:
    """テスト用のバンドルディレクトリを作る。"""
    bundle = root / "bundle"
    bundle.mkdir()
    (bundle / "spec.toml").write_text(
        textwrap.dedent(
            f"""
            [spec]
            name = "{name}"
            version = "0.1.0"
            description = "test bundle"
            """
        ).strip(),
        encoding="utf-8",
    )
    (bundle / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    docs = bundle / "docs"
    if with_adr:
        adr = docs / "adr"
        adr.mkdir(parents=True)
        (adr / "ADR-099-demo.md").write_text("# ADR-099\nbody\n", encoding="utf-8")
    if with_story:
        story = docs / "sprints" / "sprint-1" / "specs"
        story.mkdir(parents=True)
        (story / "demo-story.md").write_text("# demo story\n", encoding="utf-8")
    return bundle


@pytest.fixture
def tmp_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """install_spec が ROOT を見るので一時 ROOT に差し替える。"""
    import importlib

    import install_spec

    monkeypatch.setattr(install_spec, "ROOT", tmp_path)
    monkeypatch.setattr(install_spec, "SPECS_DIR", tmp_path / "specs")
    monkeypatch.setattr(install_spec, "DOCS_DIR", tmp_path / "docs")
    importlib.reload  # 念のため
    (tmp_path / "specs").mkdir()
    (tmp_path / "docs").mkdir()
    return tmp_path


def test_install_validates_manifest_required(tmp_project: Path, tmp_path: Path) -> None:
    import install_spec

    bundle = tmp_path / "bad-bundle"
    bundle.mkdir()
    # spec.toml なし

    with pytest.raises(ValueError, match="spec.toml"):
        install_spec.install(str(bundle))


def test_install_validates_manifest_has_name(tmp_project: Path, tmp_path: Path) -> None:
    import install_spec

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "spec.toml").write_text('[spec]\nversion = "1"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="\\[spec\\].name"):
        install_spec.install(str(bundle))


def test_install_copies_to_specs_and_docs(tmp_project: Path) -> None:
    import install_spec

    bundle = _make_bundle(tmp_project, name="onboarding")
    result = install_spec.install(str(bundle))

    assert result.name == "onboarding"
    # specs/<name>/ に凍結保存
    assert (tmp_project / "specs" / "onboarding" / "spec.toml").exists()
    assert (tmp_project / "specs" / "onboarding" / "docs" / "adr" / "ADR-099-demo.md").exists()
    # docs/ にもマージ
    assert (tmp_project / "docs" / "adr" / "ADR-099-demo.md").exists()
    assert (
        tmp_project / "docs" / "sprints" / "sprint-1" / "specs" / "demo-story.md"
    ).exists()


def test_install_skips_when_docs_file_exists_with_different_content(
    tmp_project: Path,
) -> None:
    import install_spec

    # 先に docs/adr/ADR-099 を別内容で配置
    existing = tmp_project / "docs" / "adr"
    existing.mkdir(parents=True)
    (existing / "ADR-099-demo.md").write_text("# 既存の別内容\n", encoding="utf-8")

    bundle = _make_bundle(tmp_project, name="onboarding")
    result = install_spec.install(str(bundle))

    # 既存ファイルは保たれる（コンフリクトとして検出）
    assert (existing / "ADR-099-demo.md").read_text(encoding="utf-8") == "# 既存の別内容\n"
    # コンフリクトは result に記録される
    assert any("ADR-099-demo.md" in c for c in result.conflicts)
    # 競合しない方はコピーされる
    assert (
        tmp_project / "docs" / "sprints" / "sprint-1" / "specs" / "demo-story.md"
    ).exists()


def test_install_force_overwrites_existing_docs(tmp_project: Path) -> None:
    import install_spec

    existing = tmp_project / "docs" / "adr"
    existing.mkdir(parents=True)
    (existing / "ADR-099-demo.md").write_text("# old\n", encoding="utf-8")

    bundle = _make_bundle(tmp_project, name="onboarding")
    result = install_spec.install(str(bundle), force=True)

    assert (existing / "ADR-099-demo.md").read_text(encoding="utf-8") == "# ADR-099\nbody\n"
    assert result.conflicts == []


def test_install_idempotent_when_content_identical(tmp_project: Path) -> None:
    import install_spec

    bundle = _make_bundle(tmp_project, name="onboarding")
    install_spec.install(str(bundle))
    # 2 回目のインストール: 同一内容ならコンフリクト無し
    result = install_spec.install(str(bundle))
    assert result.conflicts == []


def test_install_handles_bundle_without_docs(tmp_project: Path, tmp_path: Path) -> None:
    """docs/ が無いバンドルでもクラッシュしない（specs/ 凍結のみ）。"""
    import install_spec

    bundle = _make_bundle(tmp_project, name="manifest-only", with_adr=False, with_story=False)
    result = install_spec.install(str(bundle))

    assert (tmp_project / "specs" / "manifest-only" / "spec.toml").exists()
    assert result.copied == []
