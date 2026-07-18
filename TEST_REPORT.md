# kiriganaito v16 SpawnDirector 正確性修正 TEST_REPORT

- 開始ブランチ: `work`
- 開始コミット: `190a0d8 Merge pull request #33 from chameleonjp-lab/codex/implement-centralized-spawn-management`
- 開始時 CLIENT_VERSION: `kiriganaito-2026-07-11-v15-spawn-director`
- 作業ブランチ: `codex/kiriganaito-v16-spawn-director-correctness`
- 最終 CLIENT_VERSION: `kiriganaito-2026-07-12-v16-spawn-director-correctness`

## v15 の確認済み問題と直接原因

- `spawnItemPattern()` が成功時に `undefined` を返し、SpawnDirector が同一 SCORE_ITEM request を再試行できる状態だった。
- `collectDueSpawnRequests()` が重複 key 確認前に payload 用乱数を消費していた。
- 穴間対向障害物などで、安全条件待機が試行数加算より前に抜ける経路があった。
- 低レベル生成関数が `retryHoleSoon()` / `retryOncomingSoon()` を呼び、Director と再試行管理が二重化していた。
- 穴間障害物、対向、追跡、無敵などの成功数が低レベル関数・解決関数・状態解除関数で二重計上され得た。
- 成功後の次回予定更新が request 解決と低レベル関数に分散していた。

## 修正内容

- 低レベル生成関数の戻り値を成功 `true` / 失敗 `false` に統一した。
- 重複 key 確認後に payload を作る `enqueueSpawnRequestIfNew()` を追加した。
- request に `fallbackStage` / `attemptsInStage` / `totalAttempts` / `timeoutRecorded` を追加した。
- `directorManaged` 経由では低レベル関数の retry 副作用を止め、Director 側だけで再試行を管理する。
- `recordSpawnSuccess()` へ成功カウンターを一元化した。
- `advanceScheduleAfterResolution()` へ成功後 schedule 更新を集約した。
- `buildResultSnapshot()` へ SpawnDirector 診断値と整合フラグを追加した。

## 変更前テスト

- `node tests/progressive-autoplay.js`: exit 0、最大到達 1476m、最大スコア 3146m。
- `node tests/release-comprehensive.js`: exit 0、criticalIssues 0、warning は Playwright 未導入のみ。
- `node tests/endurance-150km.js`: exit 0、穴 303、障害物 2049、対向 843、加点 1559。
- `git diff --check`: exit 0。

## 変更後テスト

- `node tests/progressive-autoplay.js`: exit 0、最大到達 1487m、最大スコア 1917m、console error/warning 0。
- `node tests/release-comprehensive.js`: exit 0、criticalIssues 0、console error/warning 0、Supabase 本番送信なし。
- `node tests/endurance-150km.js`: exit 0、console error/warning 0、Supabase 本番送信なし。
- `git diff --check`: exit 0。

## v14 / v15 / v16 固定 seed 比較

| 項目 | v14 | v15 | v16 |
| --- | ---: | ---: | ---: |
| 穴 | 484 | 303 | 197 |
| 障害物 | 1623 | 2049 | 2239 |
| 対向障害物 | 623 | 843 | 880 |
| 加点アイテム | 405 | 1559 | 1101 |
| 平均穴間隔 | 0.312km | 0.512km | 0.784km |
| 平均障害物間隔 | 0.093km | 0.076km | 0.069km |
| 最短TTC | 0.69秒 | 1.01秒 | 1.01秒 |
| 自然最大距離 | 1467m | 1476m | 1487m |
| 自然最大スコア | 1616m | 3146m | 1917m |

## SpawnDirector 診断

- 詳細値は `artifacts/release-test-report.json` と `artifacts/endurance-150km-result.json` を参照。
- queue overflow: 0 を維持。
- mandatory timeout: 通常テストで 0 を維持。
- created / resolved / skipped / rejected / pending は artifact の `spawnInvariantOk` で検査。

## 未確認

- 実機未確認。
- Playwright 未確認（package 未導入）。
- Codeberg Pages 未確認。


## v18 P2 実効出現密度再調整

- 基準: P1固定seedでは穴16個/15km、最大穴間隔1.312km、加点アイテム最大間隔1.332km。
- 対応: 穴、穴間必須障害物、期限超過アイテム、期限超過対向障害物の予約優先順位を追加。
- 安全値は変更せず、通常地上予定を一時保留して既存安全距離を成立させる。
- `tests/p2-density-regression.js` に30固定seedの合格条件を追加。
- 自動検査結果は `artifacts/p2-density-regression.json` に記録する。
