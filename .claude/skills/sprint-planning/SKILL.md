---
name: sprint-planning
description: /plan-sprint の承認後に実行。エージェント起動・worktree作成を行う。必ず /plan-sprint → 人間承認 → このスキル の順序を守る。
user-invocable: true
---

# スプリント計画スキル（実装フェーズ開始）

## 前提条件（必ず確認）
- [ ] `/plan-sprint` の計画書が承認済み（`docs/sprints/sprint-N/sprint-plan.md`）
- [ ] 各ストーリーの `/plan-feature` が承認済み（または軽微なため省略承認済み）

## 1. 承認済み計画書の読み込み
`docs/sprints/sprint-N/sprint-plan.md` を読んでWave構成を確認する。

## 2. タスク分解（スマホ・GCP視点で）

```markdown
## Sprint-N 計画

### ゴール
[1文]

### ストーリー分解
| Story | 担当エージェント | 並列可否 | 見積 |
|-------|----------------|---------|------|
| スマホUI実装 | mobile-agent | ↔ backend-agent | M |
| API実装 | backend-agent | ↔ mobile-agent | M |
| GCPリソース構築 | infra-agent | 先行必須 | S |
| テスト | test-agent | API確定後 | S |
```

## 3. エージェント起動（Agent Teams）
```
create an agent team for sprint N:
- mobile-agent: スマホUI実装（story-XXX）
- backend-agent: FastAPI実装（story-XXX）
- infra-agent: Cloud Runデプロイ環境準備
- test-agent: テスト生成（API確定後）
```

## 4. worktree作成（並列実装）
```bash
git worktree add ../frontend-sprint-N feature/sprint-N-frontend
git worktree add ../backend-sprint-N feature/sprint-N-backend
```

## 5. アウトプット
`docs/sprints/sprint-N/plan.md` を作成
