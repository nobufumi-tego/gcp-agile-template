# specs/ — 取り込み済み仕様書バンドル置き場

外部から取り込んだ仕様書（ユーザーストーリー・受入条件・ADR・スプリント計画書）の
**凍結アーカイブ**を置くディレクトリ。

## 役割の分担

```
specs/<name>/        ← 取り込み時のスナップショット（編集しない）
docs/                ← 実際に使う作業領域（ここを編集する）
```

`scripts/install_spec.py` がスペックバンドルを取り込むと、両方に配置する：
- `specs/<name>/`  : 元バンドル全体を凍結保存（再取り込み・差分比較用）
- `docs/...`       : `specs/<name>/docs/**` をプロジェクトの `docs/**` にマージ（ここから編集）

## バンドル構造

```
specs/<name>/
├── spec.toml             # マニフェスト（必須）
├── README.md             # バンドルの説明
└── docs/                 # プロジェクトの docs/ にミラーされる構造
    ├── adr/
    │   └── ADR-NNN-*.md
    ├── sprints/
    │   ├── backlog.md
    │   └── sprint-N/
    │       ├── specs/
    │       │   └── <story>.md
    │       └── plans/
    │           └── <story>-plan.md
    └── ...
```

## マニフェスト形式

`spec.toml`:
```toml
[spec]
name = "user-onboarding-mvp"
version = "0.1.0"
description = "新規ユーザーの初回ログイン〜プロフィール編集までの仕様一式"
author = "PO チーム / external"

[target]
# どの sprint の specs/plans に入るか（任意・人間向けドキュメント）
sprint = 1
```

## 取り込みコマンド

```bash
# ローカルパス
python scripts/install_spec.py /path/to/bundle

# Git URL（branch・モノレポ subdir 指定可）
python scripts/install_spec.py https://github.com/po-team/specs.git --ref main --subdir bundles/onboarding

# .zip
python scripts/install_spec.py ./onboarding-spec.zip

# 既存の docs/ ファイルを上書き
python scripts/install_spec.py <source> --force
```

## コンフリクト方針

- `docs/<path>` がすでに存在し、内容が異なる場合 → 既定で **スキップして警告**
- `--force` で上書き
- 同一内容なら静かにスキップ
- `specs/<name>/` 自体は `--force` なしでも上書き（凍結アーカイブのため）
