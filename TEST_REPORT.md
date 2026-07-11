# TEST_REPORT

- CLIENT_VERSION: `kiriganaito-2026-07-11-v14-world-zones`
- 作業開始時の main 相当 CLIENT_VERSION: `kiriganaito-2026-06-28-v13-hole-fall-density`

## 変更前（v13）基準

- `node tests/progressive-autoplay.js`: exit 0。最大到達距離 1467m、最大補正込みスコア 1616m、console error/warning 0。
- `node tests/release-comprehensive.js`: exit 0。criticalIssues 0、console error/warning 0、Supabase 本番送信なし。Playwright 未導入により artifact verdict は WARN。
- `node tests/endurance-150km.js`: exit 0。150km耐久ハーネス完走、穴 484個、障害物 1623個、対向障害物 623個、加点アイテム 405個、平均穴間隔 0.312km、平均障害物間隔 0.093km、対向障害物最短TTC 0.69秒、最終スコア 150.00km、payload version は v13。

## 変更後（v14）

- `node tests/progressive-autoplay.js`: exit 0。最大到達距離 1467m、最大補正込みスコア 1616m、console error/warning 0。
- `node tests/release-comprehensive.js`: exit 0。criticalIssues 0、console error/warning 0、Supabase 本番送信なし。worldMetadataCheck は全項目 true。Playwright 未導入により artifact verdict は WARN。
- `node tests/endurance-150km.js`: exit 0。150km耐久ハーネス完走、穴 484個、障害物 1623個、対向障害物 623個、加点アイテム 405個、平均穴間隔 0.312km、平均障害物間隔 0.093km、対向障害物最短TTC 0.69秒、最終スコア 150.00km、payload version は v14。

## 主要出現数・間隔の差分

- 固定 seed の 150km 耐久では、v13 と v14 で穴 484個、障害物 1623個、対向障害物 623個、加点アイテム 405個、平均穴間隔 0.312km、平均障害物間隔 0.093km、対向障害物最短TTC 0.69秒、最終スコア 150.00km が一致しました。
- `Math.random()` の静的出現数は変更前後とも 40 で、新しい乱数呼び出しは追加していません。
- 実機未確認。Playwright は package 未導入で npx playwright が npm E403 のため利用不可です。
