# TEST_REPORT

- CLIENT_VERSION: `kiriganaito-2026-06-28-v13-hole-fall-density`
- 検証日: 2026-06-30

## 実行結果

- `node tests/progressive-autoplay.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。自然走行最大 1,468m。
- `node tests/release-comprehensive.js`: PASS相当（exit 0、criticalIssues 0、console error/warning 0、Supabase 本番送信なし）。artifact verdict は Playwright 未導入警告により WARN。穴落ち専用テスト、v13 CLIENT_VERSION、2km以内対向障害物、`unavoidableOncomingCount` 0 を確認。
- `node tests/endurance-150km.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。150km耐久ハーネス完走、payload version は `kiriganaito-2026-06-28-v13-hole-fall-density`。

## v13 追加検査

- 足元支持点が穴の水平範囲に入った地上走行・穴中央・穴端・着地・無敵中・障害物事故後無敵中・高速 swept ケースで、すべて `RESULT` かつ `resultSnapshot.reason` が穴になることを検査。
- 十分な高さでジャンプ中に穴上を越えた場合は `PLAYING` のままになることを検査。
- 穴には `prevX` を保持し、1フレームで足元を跨ぐ場合も `didHoleSweepAcrossFoot()` で検出する。
- 結果画面は通常表示と詳細診断を分け、runMeters / resultSnapshot / TTC 系などの開発値は「詳細診断を表示」ボタンで折りたたむ。

## 主要数値

- release comprehensive 150km耐久: `oncomingSpawnCount` は300以上、`betweenHoleOncomingSpawnCount` は50以上、`unavoidableOncomingCount = 0`、`oncomingMinTtcSec = 0.6248秒`、`earlyOncomingMinTtcSec = 1.1839秒`。
- endurance-150km.js: `穴出現数 = 484個`、`平均穴間隔 = 0.312km`、`障害物出現数` は継続的に生成、`対向障害物最短TTC = 0.69秒`、`2km以内対向障害物最短TTC = 1.38秒`、`避け不能対向障害物数 = 0回`。
- Supabase/RPC は既存 `submit_score` / `get_best_score_ranking` と publishable key のみを使用し、テストでは本番送信していない。
