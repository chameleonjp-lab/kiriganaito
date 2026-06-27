# kiriganaito v7 emergency test report

## Summary
- Updated CLIENT_VERSION, HTML meta, home display, and result display to `kiriganaito-2026-06-28-v7-result-dom-density`.
- Fixed result DOM rendering by caching `resultComment` and splitting result processing into snapshot/header/breakdown/version/submission stages.
- Increased hole density with short retry scheduling and recorded max/average hole gaps.
- Increased oncoming obstacle retry/spawn behavior after 3km and recorded candidate/spawn/retry counts.
- Supabase/RPC behavior remains mocked in tests; production submission is not performed by the test harness.

## v7 緊急修正テスト結果
- `node tests/progressive-autoplay.js`: PASS（console error/warning 0、Supabase 本番送信なし）。自然走行は最大 780m、密度増加により早期穴落ち傾向のため実機確認対象。
- `node tests/release-comprehensive.js`: PASS/WARN（finalVerdict=WARN、console error 0、resultComment DOM キャッシュ、finishGame 完走、非0結果スコア、内訳、ランキング送信モック到達、CLIENT_VERSION v7 を確認）。WARN は Playwright 未導入によるスクリーンショット未取得。
- `node tests/endurance-150km.js`: PASS（console error/warning 0、Supabase 本番送信なし）。密度調整後の自然走行は 19.05km で終了し、結果画面と送信 payload は非0で v7。

## Manual device checks recommended
- 実機で結果画面の大きな記録、内訳、ランキング送信状態が初回表示から更新されること。
- 実機で 0.5km 以降に小穴が十分見えること、穴同士が接触しないこと。
- 実機で 3km 以降の対向障害物が左から右へ向かう障害物として見えること。
