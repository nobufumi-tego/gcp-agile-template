"""
modules/*/backend/router.py を動的ロードして FastAPI に include する。

各モジュールは:
- modules/<name>/backend/router.py で APIRouter を `router` 名で公開する
- (任意) modules/<name>/module.toml で `[backend].prefix` を指定可能（既定: /api/v1/<name>）
- 名前が `_` や `.` で始まるディレクトリは無視

1 つのモジュールがロード失敗してもログに残して他のロードは続ける（部分起動を可能にする）。
"""
from __future__ import annotations

import importlib.util
import logging
import sys
import tomllib
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI

logger = logging.getLogger("uvicorn.error")


def _read_manifest(module_dir: Path) -> dict[str, Any]:
    manifest_path = module_dir / "module.toml"
    if not manifest_path.exists():
        return {}
    return tomllib.loads(manifest_path.read_text(encoding="utf-8"))


_NAMESPACE = "_app_modules"


def _ensure_namespace_package() -> None:
    """親名前空間 _app_modules を sys.modules に用意する。"""
    if _NAMESPACE in sys.modules:
        return
    spec = importlib.util.spec_from_loader(_NAMESPACE, loader=None)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    module.__path__ = []  # 名前空間パッケージとして振る舞う
    sys.modules[_NAMESPACE] = module


def _load_router(module_name: str, router_path: Path) -> APIRouter:
    """router.py を動的 import し、`router` 属性を返す。

    `from .models import ...` のような相対 import を機能させるため、
    `_app_modules.<name>` を合成パッケージとして sys.modules に登録してから
    `_app_modules.<name>.router` を読み込む。
    """
    _ensure_namespace_package()

    parent_pkg = f"{_NAMESPACE}.{module_name}"
    backend_dir = router_path.parent

    if parent_pkg not in sys.modules:
        init_py = backend_dir / "__init__.py"
        if init_py.exists():
            parent_spec = importlib.util.spec_from_file_location(
                parent_pkg,
                init_py,
                submodule_search_locations=[str(backend_dir)],
            )
        else:
            parent_spec = importlib.util.spec_from_loader(parent_pkg, loader=None)

        if parent_spec is None:
            raise ImportError(f"could not build parent spec for {module_name}")
        parent_mod = importlib.util.module_from_spec(parent_spec)  # type: ignore[arg-type]
        parent_mod.__path__ = [str(backend_dir)]
        sys.modules[parent_pkg] = parent_mod
        if parent_spec.loader is not None:
            parent_spec.loader.exec_module(parent_mod)

    qualified = f"{parent_pkg}.router"
    spec = importlib.util.spec_from_file_location(qualified, router_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build spec for module {module_name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified] = module
    spec.loader.exec_module(module)

    router = getattr(module, "router", None)
    if router is None:
        raise AttributeError(
            f"module {module_name} の router.py が `router` 属性を公開していません"
        )
    if not isinstance(router, APIRouter):
        raise TypeError(
            f"module {module_name} の `router` は APIRouter ではありません"
        )
    return router


def load_modules(app: FastAPI, modules_dir: Path) -> list[str]:
    """modules_dir 配下のフィーチャーモジュールを app に取り込む。

    Returns: 正常にロードされたモジュール名のリスト（アルファベット順）。
    """
    if not modules_dir.exists():
        return []

    loaded: list[str] = []
    for entry in sorted(modules_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith((".", "_")):
            continue

        router_path = entry / "backend" / "router.py"
        if not router_path.exists():
            continue

        try:
            manifest = _read_manifest(entry)
            prefix = manifest.get("backend", {}).get("prefix", f"/api/v1/{entry.name}")
            router = _load_router(entry.name, router_path)
            app.include_router(router, prefix=prefix)
            loaded.append(entry.name)
            logger.info(f"loaded module: {entry.name} -> {prefix}")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"failed to load module {entry.name}: {exc}")

    return loaded
