---
name: mobile-check
description: フロントエンド実装後に必ず実行。スマホファースト基準を自動チェックする。
user-invocable: true
---

# モバイルチェックスキル

## 実行タイミング
フロントエンドの実装・修正のたびに必ず実行する。

## チェック項目

### 1. レイアウト確認
```bash
# Playwright でスマホエミュレーション
npx playwright test --project=mobile-chrome
```
確認ポイント：
- 375px（iPhone SE）で崩れなし
- 390px（iPhone 15）で崩れなし
- 横スクロール発生なし

### 2. タッチターゲット確認
```bash
# axe-core でアクセシビリティ含むタッチ確認
npx axe http://localhost:5173 --tags mobile
```
- インタラクティブ要素が44×44px以上

### 3. パフォーマンス確認
```bash
# Lighthouse CLI（モバイル設定）
npx lighthouse http://localhost:5173 \
  --form-factor=mobile \
  --throttling-method=simulate \
  --output=json \
  --output-path=./lighthouse-report.json

# スコア確認
cat lighthouse-report.json | python -c "
import json, sys
r = json.load(sys.stdin)
cats = r['categories']
print(f'Performance: {cats[\"performance\"][\"score\"]*100:.0f}')
print(f'LCP: {r[\"audits\"][\"largest-contentful-paint\"][\"displayValue\"]}')
print(f'CLS: {r[\"audits\"][\"cumulative-layout-shift\"][\"displayValue\"]}')
"
```
合格基準：
- Performance スコア 70以上
- LCP 2.5秒以内
- CLS 0.1以下

### 4. PWA確認
```bash
cat frontend/static/manifest.json | python -c "
import json, sys
m = json.load(sys.stdin)
checks = ['name', 'short_name', 'icons', 'start_url', 'display']
for c in checks:
    status = '✓' if c in m else '✗'
    print(f'{status} {c}')
"
```

## 合否判定
すべて通過 → DoD の mobile-check 項目にチェック
不合格あり → mobile-agent に差し戻し・修正依頼
