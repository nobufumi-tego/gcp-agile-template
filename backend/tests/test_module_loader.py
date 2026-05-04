"""
module_loader のテスト。
fixture で一時ディレクトリにダミーモジュールを作り、ロードできることを検証する。
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def tmp_modules_dir(tmp_path: Path) -> Path:
    """空の modules/ 風ディレクトリを返す。"""
    d = tmp_path / "modules"
    d.mkdir()
    return d


def _write_module(
    root: Path,
    name: str,
    *,
    router_code: str,
    manifest: str | None = None,
) -> Path:
    """テスト用にダミーモジュールを書き出すヘルパー。"""
    mod = root / name
    backend = mod / "backend"
    backend.mkdir(parents=True)
    (backend / "__init__.py").write_text("", encoding="utf-8")
    (backend / "router.py").write_text(textwrap.dedent(router_code), encoding="utf-8")
    if manifest is not None:
        (mod / "module.toml").write_text(textwrap.dedent(manifest), encoding="utf-8")
    return mod


def test_load_modules_returns_empty_when_dir_does_not_exist(tmp_path: Path) -> None:
    from module_loader import load_modules

    app = FastAPI()
    loaded = load_modules(app, tmp_path / "non-existent")
    assert loaded == []


def test_load_modules_skips_when_dir_is_empty(tmp_modules_dir: Path) -> None:
    from module_loader import load_modules

    app = FastAPI()
    loaded = load_modules(app, tmp_modules_dir)
    assert loaded == []


def test_load_modules_loads_router_with_default_prefix(tmp_modules_dir: Path) -> None:
    from module_loader import load_modules

    _write_module(
        tmp_modules_dir,
        "hello",
        router_code="""
            from fastapi import APIRouter
            router = APIRouter()

            @router.get("/ping")
            def ping():
                return {"ok": True}
        """,
    )

    app = FastAPI()
    loaded = load_modules(app, tmp_modules_dir)
    assert loaded == ["hello"]

    client = TestClient(app)
    res = client.get("/api/v1/hello/ping")
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_load_modules_uses_manifest_prefix(tmp_modules_dir: Path) -> None:
    from module_loader import load_modules

    _write_module(
        tmp_modules_dir,
        "billing",
        router_code="""
            from fastapi import APIRouter
            router = APIRouter()

            @router.get("/usage")
            def usage():
                return {"used": 0}
        """,
        manifest="""
            [module]
            name = "billing"
            version = "0.1.0"

            [backend]
            prefix = "/api/v2/billing"
        """,
    )

    app = FastAPI()
    loaded = load_modules(app, tmp_modules_dir)
    assert loaded == ["billing"]

    client = TestClient(app)
    res = client.get("/api/v2/billing/usage")
    assert res.status_code == 200


def test_load_modules_skips_module_without_router(tmp_modules_dir: Path) -> None:
    """frontend-only のモジュール（backend/router.py が無い）はスキップされる。"""
    from module_loader import load_modules

    mod = tmp_modules_dir / "frontend-only"
    (mod / "frontend").mkdir(parents=True)

    app = FastAPI()
    loaded = load_modules(app, tmp_modules_dir)
    assert loaded == []


def test_load_modules_skips_underscore_dirs(tmp_modules_dir: Path) -> None:
    """_template や _wip などのプレフィックス付きディレクトリは無視。"""
    from module_loader import load_modules

    _write_module(
        tmp_modules_dir,
        "_wip",
        router_code="""
            from fastapi import APIRouter
            router = APIRouter()
        """,
    )

    app = FastAPI()
    loaded = load_modules(app, tmp_modules_dir)
    assert loaded == []


def test_load_modules_loads_multiple_in_alphabetical_order(
    tmp_modules_dir: Path,
) -> None:
    from module_loader import load_modules

    _write_module(
        tmp_modules_dir,
        "zeta",
        router_code="from fastapi import APIRouter\nrouter = APIRouter()",
    )
    _write_module(
        tmp_modules_dir,
        "alpha",
        router_code="from fastapi import APIRouter\nrouter = APIRouter()",
    )

    app = FastAPI()
    loaded = load_modules(app, tmp_modules_dir)
    assert loaded == ["alpha", "zeta"]


def test_load_modules_logs_and_continues_on_failure(
    tmp_modules_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """1 つのモジュールが壊れても他のモジュールはロードされる。"""
    from module_loader import load_modules

    _write_module(
        tmp_modules_dir,
        "broken",
        router_code="raise RuntimeError('boom')",
    )
    _write_module(
        tmp_modules_dir,
        "good",
        router_code="from fastapi import APIRouter\nrouter = APIRouter()",
    )

    app = FastAPI()
    loaded = load_modules(app, tmp_modules_dir)
    assert loaded == ["good"]
