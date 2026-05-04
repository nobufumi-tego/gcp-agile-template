---
name: sprint-review
description: スプリント終了時に実行。DoD確認・デプロイ・CLAUDE.md更新・レトロ記録を行う。
user-invocable: true
---

# スプリントレビュースキル

## 1. DoD 最終確認
```
[ ] pytest 全件グリーン
[ ] /mobile-check 通過（375px・LCP・CLS・PWA）
[ ] review-agent 承認済み
[ ] /deploy-gcp 実行・本番確認
[ ] 受入条件すべて満たす
[ ] CLAUDE.md 更新済み
```

## 2. 本番動作確認
```bash
# スマホエミュレーションで本番確認
npx lighthouse https://[本番URL] \
  --form-factor=mobile \
  --output=json | python -c "
import json,sys; r=json.load(sys.stdin)
print('Performance:', r['categories']['performance']['score']*100)
print('LCP:', r['audits']['largest-contentful-paint']['displayValue'])
"
```

## 3. CLAUDE.md への知見反映
以下カテゴリで追記：
- GCP設定で発見したこと（リージョン・スケール設定など）
- スマホ対応で発見したパターン
- コスト最適化の知見
- やらかしと対処法

## 4. レトロスペクティブ記録
`docs/sprints/sprint-N/retro.md` に記録：

```markdown
## Keep
## Problem
## Try
## エージェント構成の改善点
## コスト実績（前回比）
```

## 5. 次スプリント準備
- 未完了ストーリーを backlog.md に戻す
- 新しい技術的負債を backlog.md に追加
