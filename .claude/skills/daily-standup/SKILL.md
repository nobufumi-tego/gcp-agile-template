---
name: daily-standup
description: 毎日の進捗確認。スマホ品質・GCPコスト・ブロッカーを集約する。
user-invocable: true
---

# デイリースタンドアップスキル

## 確認項目

### 進捗
```bash
git log --oneline --since="1 day ago" --all
```

### スマホ品質（毎日確認）
```bash
# ステージング環境でLighthouse
npx lighthouse https://[staging-url] --form-factor=mobile \
  --output=json | python -c "
import json,sys; r=json.load(sys.stdin)
score = r['categories']['performance']['score']*100
status = '✓' if score >= 70 else '✗'
print(f'{status} モバイルスコア: {score:.0f}')
"
```

### GCPコスト確認
```bash
gcloud billing budgets list --format="table(displayName,amount,thresholdRules)"
```

### コンテキスト確認
- /context で使用率を確認
- 70%超 → /compact 実行
- 90%超 → 新セッション推奨

### ブロッカー
- API契約の未確定 → spec-agent に依頼
- GCPリソースの不足 → infra-agent に委譲
- テスト失敗継続 → review-agent に相談

## アウトプット
`docs/sprints/sprint-N/standup-YYYYMMDD.md` に記録
