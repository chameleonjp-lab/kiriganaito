# TEST_REPORT

- CLIENT_VERSION: `kiriganaito-2026-06-28-v12-oncoming-speed-control`
- 検証日: 2026-06-28

## 実行結果

- `node tests/progressive-autoplay.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。自然走行最大 1,531m。
- `node tests/release-comprehensive.js`: PASS相当（exit 0、criticalIssues 0、console error/warning 0、Supabase 本番送信なし）。artifact verdict は Playwright 未導入警告により WARN。CLIENT_VERSION v12、0.80km 未満対向障害物なし、2km以内対向障害物あり、`oncoming_unavoidable`/`unavoidableOncomingCount` 0、150km耐久相当の対向障害物数回復を確認。
- `node tests/endurance-150km.js`: PASS（exit 0、console error/warning 0、Supabase 本番送信なし）。150km耐久ハーネス完走、payload version は `kiriganaito-2026-06-28-v12-oncoming-speed-control`。

## v12 追加検査

- 対向障害物は、TTC不足だけを理由に大量却下せず、まず専用速度倍率で低速化し、必要時は安全速度を逆算して再判定する。
- release comprehensive は `oncoming_unavoidable === 0`、`unavoidableOncomingCount === 0`、対向障害物最短TTC 0.50秒以上、早期対向障害物最短TTC 0.80秒以上、150kmで `oncomingSpawnCount >= 300`、`betweenHoleOncomingSpawnCount >= 50`、候補数に対して出現数が極端に少ない状態の禁止を FAIL 条件として検査する。
- 結果画面に対向障害物近すぎ却下数、速度調整数、平均/最小/最大速度倍率、TTC不足による最終却下数、最小反応猶予、平均反応猶予、最短TTC、2km以内最短TTC、避け不能数を表示する。

## 主要数値

- release comprehensive 150km耐久: `oncomingSpawnCount = 978`、`betweenHoleOncomingSpawnCount = 978`、`oncomingCandidateCount = 2031`、`oncomingSpeedAdjustCount = 377`、`oncomingTtcFinalRejectCount = 0`、`unavoidableOncomingCount = 0`、`oncomingMinTtcSec = 0.625秒`、`earlyOncomingMinTtcSec = 1.046秒`。
- endurance-150km.js: `対向障害物出現数 = 973個`、`穴間対向障害物出現数 = 972個`、`対向障害物候補数 = 1745回`、`避け不能対向障害物数 = 0回`、`TTC不足による最終却下数 = 0回`。
- `oncomingCandidateCount` が大量なのに `oncomingSpawnCount` が1桁、または300未満になる状態は release comprehensive で FAIL 扱い。
