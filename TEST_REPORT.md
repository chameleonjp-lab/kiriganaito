# kiriganaito v8 hole-obstacle-link test report

## 対象バージョン
- CLIENT_VERSION: `kiriganaito-2026-06-28-v8-hole-obstacle-link`

## 変更概要
- 穴生成後、次の穴までに通常障害物または対向障害物を必ず1つ以上生成する `spawn.needObstacleBeforeNextHole` 制御を追加。
- 3.00km未満は通常障害物のみ、3.00km以降は通常/対向障害物を距離・逃走状態に応じて混在。
- 対向障害物が安全距離不足で出せない場合は通常障害物へフォールバック。
- 結果画面に穴間必須障害物カウンターと穴だけ連続した回数を追加。
- Supabase URL、publishable key、RPCパス、RPC引数、pending queueキー、旧キー移行処理、ランキング送信仕様は変更なし。

## 実行結果
- `node tests/progressive-autoplay.js`: PASS（exit 0、console error/warning 0、Supabase本番送信なし）。自然走行最大到達 1526m、150km自然到達は不可。
- `node tests/release-comprehensive.js`: PASS/WARN（exit 0、finalVerdict=WARN、console error/warning 0、Supabase本番送信なし）。WARN は Playwright 未導入によるスクリーンショット未取得。
- `node tests/endurance-150km.js`: PASS（exit 0、console error/warning 0、Supabase本番送信なし）。150km耐久ハーネス完走、payload version は v8。

## v8 追加観点
- CLIENT_VERSION が `kiriganaito-2026-06-28-v8-hole-obstacle-link` であることを確認。
- 結果画面に「穴間必須障害物出現数」「穴間通常障害物出現数」「穴間対向障害物出現数」「穴間障害物生成失敗再試行数」「穴だけ連続した回数」が表示されることを確認。
- `consecutiveHoleViolationCount` は通常 0 になる設計。テストハーネスで静的/動的に監視。
- 3km未満は穴間対向障害物を禁止し、3km以降は対向障害物も候補に含める。
- 大穴直後の対向障害物、対向障害物直後の大穴、穴直後/障害物直後の即配置を安全距離で抑止。
