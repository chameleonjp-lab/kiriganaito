# TEST_REPORT

- CLIENT_VERSION: `kiriganaito-2026-06-28-v10-early-oncoming`
- 目的: 対向障害物を 0.80km 以降へ前倒しし、2.00km 以内の実出現保証と穴間必須障害物への対向混入を検証。

## 実行結果

- `node tests/progressive-autoplay.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。最大到達距離 1441m、自然走行ハーネスで 1km 到達を確認。
- `node tests/release-comprehensive.js`: PASS（exit 0、criticalIssues 0、console error/warning 0、Supabase 本番送信なし）。CLIENT_VERSION v10、0.80km 未満の対向障害物なし、2km 以内対向障害物保証、結果画面カウンター、穴間対向障害物カウンターを確認。
- `node tests/endurance-150km.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。150km 耐久ハーネス完走、payload version は `kiriganaito-2026-06-28-v10-early-oncoming`。

## 主要カウンター

- 150km 耐久結果: `earlyOncomingSpawnCount = 3`、`betweenHoleOncomingSpawnCount = 1`、`oncomingCandidateCount = 44195`、`oncomingSpawnCount = 953`。
- `oncomingCandidateCount > 0` かつ `oncomingSpawnCount === 0` の状態は release comprehensive で FAIL 扱い。
- `betweenHoleOncomingSpawnCount` が長距離プレイで 0 のままなら FAIL 扱い。

## 生成物

- `artifacts/progressive-autoplay-report.json`
- `artifacts/progressive-autoplay-summary.txt`
- `artifacts/release-test-report.json`
- `artifacts/release-test-summary.txt`
- `artifacts/endurance-150km-report.json`
