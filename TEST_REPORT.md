# kiriganaito v15 TEST_REPORT

- 開始ブランチ: `work`
- 開始コミット: `b8862d1589b77cd84c4faaa2a6ed06ab0d0758eb`
- 開始時 CLIENT_VERSION: `kiriganaito-2026-07-11-v14-world-zones`
- 作業ブランチ: `codex/kiriganaito-v15-spawn-director`
- 現行 CLIENT_VERSION: `kiriganaito-2026-07-11-v15-spawn-director`

## 変更前テスト

- `node tests/progressive-autoplay.js`: exit 0 / 最大到達距離 1467m / 最大補正込みスコア 1616m
- `node tests/release-comprehensive.js`: exit 0 / criticalIssues 0 / console error 0 / console warning 0
- `node tests/endurance-150km.js`: exit 0 / 穴 484 / 障害物 1623 / 対向 623 / 加点 405 / 平均穴間隔 0.312km / 平均障害物間隔 0.093km / 最短TTC 0.69秒 / 最終スコア 150.00km
- `git diff --check`: exit 0

## 変更後テスト

- `node tests/progressive-autoplay.js`: exit 0 / 最大到達距離 1476m / 最大補正込みスコア 3146m
- `node tests/release-comprehensive.js`: exit 0 / finalVerdict WARN / criticalIssues 0 / console error 0 / console warning 0 / Supabase本番送信なし
- `node tests/endurance-150km.js`: exit 0 / 穴 303 / 障害物 2049 / 対向 843 / 加点 1559 / 平均穴間隔 0.512km / 平均障害物間隔 0.076km / 最短TTC 1.01秒 / 最終スコア 150.00km
- `git diff --check`: exit 0

## SpawnDirector 構造

- キュー上限: ground 6 / air 3 / hole 2
- 1固定更新の処理上限: ground 2 / air 1 / hole 1 / total 4
- 再試行上限: 通常3回、失敗後 `nextAttemptKm` まで待機
- mandatory timeout: 通常テストで 0 を目標
- queue overflow: 通常テストで 0 を目標
- カウンター整合性: `spawnSource` と metadata を正本として二重計上を避ける設計

## 代替ルール

- 穴: LARGE → MEDIUM → SMALL → スキップ
- 穴間障害物: 対向 → 通常 → 🚶
- 早期対向障害物: 対向維持、低速🚶候補で待機
- 無敵中障害物: 通常方向🚶へ代替
- 加点アイテム: LOW の 💰 へ代替
- 👯‍♀️: 別アイテムへ置換せず延期/スキップ
- 逃走中イベント: 対向/穴は通常障害物、高い加点は低い💰へ代替

## 未確認事項

- 実機確認: 未実施
- Playwright: package 未導入のため未実施
- Codeberg Pages公開版: 未確認、公開操作なし

## 固定seed差分

v15 は再試行制御により固定seedの密度が変動している。今回はバランス定数は変更していないため、次回候補は SpawnDirector を使った実測密度調整。
