# kiriganaito v9 counter-fix test report

## 対象バージョン
- CLIENT_VERSION: `kiriganaito-2026-06-28-v9-counter-fix`

## 変更概要
- 穴間必須障害物カウンターの 未定義表示を修正。
- `resultSnapshot` に穴間カウンターを格納。
- 結果表示側で `safeInt` による未定義防御を追加。
- 結果画面と artifact に 未定義表示 / 非数値表示 が出ないことを確認。
- `consecutiveHoleViolationCount === 0` を確認。
- Supabase/RPC仕様は変更なし。

## 実行結果
- `node tests/progressive-autoplay.js`: PASS（exit 0、console error/warning 0、Supabase本番送信なし）。自然走行最大到達 1526m、150km自然到達は不可。
- `node tests/release-comprehensive.js`: PASS/WARN（exit 0、finalVerdict=WARN、criticalIssues 0、console error/warning 0、Supabase本番送信なし）。WARN は Playwright 未導入によるスクリーンショット未取得。
- `node tests/endurance-150km.js`: PASS（exit 0、console error/warning 0、Supabase本番送信なし）。150km耐久ハーネス完走、payload version は `kiriganaito-2026-06-28-v9-counter-fix`。

## v9 追加確認
- 結果画面に「穴間必須障害物出現数」「穴間通常障害物出現数」「穴間対向障害物出現数」「穴間障害物生成失敗再試行数」「穴だけ連続した回数」が数値で表示されることを確認。
- `resultSnapshot.betweenHoleObstacleSpawnCount`、`betweenHoleNormalObstacleSpawnCount`、`betweenHoleOncomingSpawnCount`、`betweenHoleObstacleRetryCount`、`consecutiveHoleViolationCount` がすべて `number` であることを確認。
- 結果内訳文字列と artifact に 未定義個、未定義回、未定義表示、非数値表示 が含まれないことを確認。
- 通常プレイ/150km耐久ハーネスで `consecutiveHoleViolationCount === 0` を確認。

## 変更していない仕様
- `GAME_SLUG`、`PUBLIC_URL`、Supabase URL、Publishable key、RPCパス、RPC引数、pending queueキー、旧キー移行処理、ランキング送信仕様は変更なし。
- 穴即終了、警戒度3終了、2段ジャンプなし、外部ライブラリなし、`index.html` 1ファイル構成は維持。
