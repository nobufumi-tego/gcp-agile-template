---
name: plan-sprint
description: スプリント全体の計画を /plan モードで立てる。sprint-planningの前段階。バックログを読んで全ストーリーの実装計画・並列化・コスト見積もりを一覧化する。
user-invocable: true
---

# スプリント全体計画スキル（/plan フェーズ）

## 位置づけ
```
バックログ確定
  → /plan-sprint（スプリント全体計画）  ← ここ
    → /sprint-planning（エージェント起動・worktree作成）
      → 各機能の /plan-feature
        → 実装
```

## 実行内容（コードは書かない）

### 1. バックログ読み込み
`docs/sprints/backlog.md` を読んで今スプリントのストーリーを把握する。

### 2. スプリント計画書の生成

```markdown
# Sprint-N 計画書

## ゴール
[1文で]

## ストーリー一覧と担当エージェント

| # | Story | 担当 | 依存 | 見積 | 並列可 |
|---|-------|------|------|------|--------|
| 1 | [name] | mobile+backend | なし | M | ✓ |
| 2 | [name] | infra | なし | S | ✓ |
| 3 | [name] | backend | Story-2完了後 | M | - |

## 実行ウェーブ（並列化計画）

Wave 1（並列）:
  - infra-agent: GCPリソース準備
  - spec-agent:  仕様書作成（全ストーリー）

Wave 2（並列）:
  - mobile-agent:  Story-1 UI実装
  - backend-agent: Story-1,3 API実装

Wave 3（順次）:
  - test-agent:    全ストーリーテスト
  - review-agent:  レビュー

Wave 4:
  - infra-agent:   /deploy-gcp

## worktree構成
  ../feature-sprint-N-frontend  ← mobile-agent
  ../feature-sprint-N-backend   ← backend-agent
  ../feature-sprint-N-infra     ← infra-agent

## トークンコスト見積もり
  Wave1: Small（仕様・設計中心）
  Wave2: Large（実装・並列）
  Wave3: Medium（テスト・レビュー）
  合計目安: Max プラン [N] タスク分

## リスク
  [リスク1]: [対策]
  [リスク2]: [対策]

## 前スプリントからの改善点（レトロより）
  [改善点1]
  [改善点2]
```

### 3. 承認待ち
計画書提出後、**人間の承認を得てから `/sprint-planning` を実行**。

変更可能な項目:
- ストーリーの優先順位変更
- Wave の順序変更
- 特定ストーリーの次スプリント送り

### 4. アウトプット
`docs/sprints/sprint-N/sprint-plan.md` に保存
