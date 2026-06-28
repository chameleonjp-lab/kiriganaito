# TEST_REPORT

- CLIENT_VERSION: `kiriganaito-2026-06-28-v11-oncoming-avoidability`
- 検証日: 2026-06-28

## 実行結果

- `node tests/progressive-autoplay.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。0.80km未満対向障害物なし、自然走行最大 1,464m。
- `node tests/release-comprehensive.js`: PASS相当（exit 0、criticalIssues 0、console error/warning 0、Supabase 本番送信なし）。artifact verdict は Playwright 未導入警告により WARN。CLIENT_VERSION v11、0.80km 未満対向障害物なし、2km以内対向障害物1回、`oncoming_unavoidable`/`unavoidableOncomingCount` 0、早期最短TTC 1.07秒を確認。
- `node tests/endurance-150km.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。150km耐久ハーネス完走、payload version は `kiriganaito-2026-06-28-v11-oncoming-avoidability`。

## v11 追加検査

- 対向障害物は、画面上で認識可能になる位置から接触までのTTCを `updateThings()` と同じ相対速度で推定し、最低反応猶予未満なら生成却下・0.02〜0.04km後に再試行する。
- release comprehensive は `oncoming_unavoidable === 0`、`unavoidableOncomingCount === 0`、対向障害物最短TTC 0.50秒以上、早期対向障害物最短TTC 0.80秒以上、大穴/穴直後の危険複合なしを FAIL 条件として検査する。
- 結果画面に対向障害物近すぎ却下数、最小反応猶予、平均反応猶予、最短TTC、2km以内最短TTC、避け不能数を表示する。

## 主要数値

- release comprehensive: `earlyOncomingSpawnCount = 1`、`earlyOncomingMinTtcSec = 1.073秒`、`unavoidableOncomingCount = 0`、`oncomingTooCloseRejectCount = 2`。
- 150km耐久結果: `earlyOncomingSpawnCount = 1`、`betweenHoleOncomingSpawnCount = 1`、`oncomingCandidateCount = 73980`、`oncomingSpawnCount = 1`、`unavoidableOncomingCount = 0`、`earlyOncomingMinTtcSec = 1.08秒`。
- `oncomingCandidateCount > 0` かつ `oncomingSpawnCount === 0` の状態は release comprehensive で FAIL 扱い。
