---
name: plan-architecture
description: 新機能追加やリファクタリング前にアーキテクチャレベルの計画を立てる。GCP構成変更・DB設計変更・認証フロー変更など大きな判断が必要な場合に使う。ADRとして記録する。
user-invocable: true
---

# アーキテクチャ計画スキル（/plan フェーズ）

## 位置づけ
```
新機能要件 or 大規模変更
  → /plan-architecture（ADR作成・承認）  ← ここ
    → /plan-sprint
      → /plan-feature × N
        → 実装
```

## 実行内容（コードは書かない）

### 1. 変更の文脈整理
```
何が変わるか:    [GCP構成 / DB設計 / 認証 / API設計 / フロント構成]
なぜ変えるか:    [ビジネス要件 / 技術的負債 / スケール要件]
変えないものは:  [継続して使う既存の仕組み]
```

### 2. 選択肢の列挙と比較

```markdown
## 選択肢A: [名前]
### 構成
[図または説明]
### メリット
- GCPファースト観点:
- スマホファースト観点:
- コスト観点:
- 開発速度:
### デメリット
- [デメリット]
### Claude Code実装難易度: [Easy/Medium/Hard]

## 選択肢B: [名前]
（同様）

## 推奨: 選択肢[X]
理由: [1-2文で]
```

### 3. GCP構成図（テキスト表現）
```
[スマホ/ブラウザ]
  ↓ HTTPS
[Firebase Hosting] → [SvelteKit SSR on Cloud Run] (任意)
  ↓ Firebase Auth IDトークン
[Cloud Run: FastAPI]
  ↓                    ↓              ↓
[Firestore]      [Cloud Storage]  [Pub/Sub]
                                      ↓
                               [Cloud Run: Worker]
                                      ↓
                               [Vertex AI / MediaPipe]
                                      ↓
                               [BigQuery]
```

### 4. 移行計画（既存データ・認証の継続性）
```
現状: [現在の構成]
移行手順:
  Step 1: [並行運用フェーズ]
  Step 2: [切り替えフェーズ]
  Step 3: [旧構成の廃止]
ロールバック: [問題発生時の戻し方]
ダウンタイム: [あり/なし/最小化策]
```

### 5. コスト影響試算
```
現状月額: 約 ¥[X]
変更後月額: 約 ¥[Y]
差分: [増減理由]
無料枠への影響: [あり/なし]
```

### 6. ADR（Architecture Decision Record）として保存
`docs/adr/ADR-[NNN]-[title].md` に記録。

承認後に `docs/adr/` に `状態: 承認済み` で保存。

## 承認プロセス
アーキテクチャ変更は **必ず人間（のぶさん）が承認してから** 次フェーズへ。
特にGCPリソースの追加・削除・認証フローの変更は慎重に。

## アウトプット
- `docs/adr/ADR-NNN-[title].md`（ADR）
- `docs/sprints/sprint-N/arch-plan.md`（スプリントへの接続）
