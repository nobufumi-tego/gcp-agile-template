---
name: plan-feature
description: 機能実装前に /plan モードで計画を立てる。コードを書く前に必ずこのスキルを実行し、人間の承認を得てから実装に移る。spec-agentの仕様書が確定した後に使う。
user-invocable: true
---

# 機能計画スキル（/plan フェーズ）

## 位置づけ
```
spec-agent（仕様確定）
  → /plan-feature（計画・承認）  ← ここ
    → 実装エージェント（コード作成）
```

## 実行方法
Claude Code で `/plan` を入力するか、このスキルを呼ぶ。
**コードは一切書かない。計画だけを出力する。**

## 計画書のフォーマット（TDD ファースト）

### 1. 対象ストーリーの確認
```
Story: [story名]
仕様書: docs/sprints/sprint-N/specs/[story].md
スプリントゴールとの関係: [一言]
```

### 2. テスト計画（最優先・実装より先に書く）

このプロジェクトは TDD が必須。実装ファイル一覧の前に、書くべきテストを列挙する。

```
バックエンドテスト（backend/tests/）:
  test_[name].py::test_[behavior]  → 検証内容: [...]
  test_[name].py::test_[edge case] → 検証内容: [...]

フロントエンドテスト（同居 *.test.ts）:
  src/lib/[path]/[name].test.ts::it('...')  → 検証内容: [...]

E2E（Playwright）:
  [シナリオ]: [操作 → 期待結果]

/mobile-check 確認ポイント:
  - 375px レイアウト
  - LCP / CLS
  - タッチターゲット 44px
  - PWA manifest

このテスト群が **書ける = 実装の契約が確定している** という意味。書けない箇所は仕様の曖昧さなので spec-agent に差し戻し。
```

### 3. 影響範囲の分析
```
変更するファイル:
  frontend/src/routes/[path]/+page.svelte  → [変更内容]
  backend/routers/[name].py               → [変更内容]
  backend/models/[name].py                → [変更内容]

新規作成するファイル:
  [ファイルパス] → [目的]

変更しないファイル:
  [理由と根拠]
```

### 4. API契約（フロント↔バック合意点）
```
エンドポイント: POST /api/v1/[resource]
リクエスト: { field: type }
レスポンス: { field: type }
エラーケース:
  400: [条件]
  401: 未認証
  404: [条件]
```
※ この契約がそのままセクション 2 のテストの assertion になる。

### 5. Firestore データ設計
```
コレクション: [name]
ドキュメント構造:
  {
    uid: string,
    [field]: type,
    created_at: Timestamp,
    updated_at: Timestamp
  }
セキュリティルール変更: 要 / 不要
```

### 6. スマホ対応計画
```
レイアウト: [375px でのUI方針]
タッチ操作: [必要なジェスチャー]
オフライン: [対応方針]
パフォーマンス懸念: [LCP・CLSへの影響]
```

### 7. 実装順序（TDD ベース）
```
Step 0: テストファイル作成（セクション 2 の内容）   ← Red を先に作る
Step 1: infra-agent → [GCPリソース準備]
Step 2: backend-agent → 失敗テスト確認 → 最小実装 → Green
Step 3: mobile-agent → 失敗テスト確認 → 最小実装 → Green（Step2 と並列可能）
Step 4: 全エージェント → リファクタ（テスト緑のまま）
Step 5: review-agent → レビュー（コミット履歴で TDD 順序を確認）
```

### 8. リスクと対策
```
リスク: [発生しうる問題]
対策:   [回避・軽減策]
代替案: [計画が崩れた場合の選択肢]
```

### 9. 見積もり
```
infra-agent:   [時間]
backend-agent: [時間]（うちテスト記述: [時間]）
mobile-agent:  [時間]（うちテスト記述: [時間]）
合計:          [時間]
コストトークン見積もり: [Small/Medium/Large]
```

## 承認プロセス
計画書を出力後、**人間（PO/のぶさん）の承認を待つ**。
承認なしに実装エージェントを起動しない。

承認コメント例:
- 「計画承認。実装開始」→ orchestratorがエージェントを起動
- 「Step 3を先に」→ 順序を修正して再提出
- 「Firestore設計を変更」→ データ設計を修正して再提出

## アウトプット
`docs/sprints/sprint-N/plans/[story]-plan.md` に保存
