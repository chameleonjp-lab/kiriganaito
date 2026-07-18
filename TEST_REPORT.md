# kiriganaito TEST_REPORT

- 現行 CLIENT_VERSION: `kiriganaito-2026-07-18-v18-effective-density`
- 現行段階: `P2 穴・障害物・アイテム密度の再調整`
- 基準main: `7b85b1a49c8005c4597cd5d054f0af2f416fa766`
- 作業ブランチ: `ai/kiriganaito-v18-effective-density`
- Draft Pull Request: `#37`

---

## v16 SpawnDirector正確性修正の履歴

### v15で確認された問題

- `spawnItemPattern()` が成功時に `undefined` を返し、同一SCORE_ITEM requestを再試行できる状態だった。
- `collectDueSpawnRequests()` が重複key確認前にpayload用乱数を消費していた。
- 穴間対向障害物などで、安全条件待機が試行数加算より前に抜ける経路があった。
- 低レベル生成関数とSpawnDirectorで再試行管理が二重化していた。
- 穴間障害物、対向、追跡、無敵などの成功数を二重計上し得た。
- 成功後の次回予定更新がrequest解決と低レベル関数へ分散していた。

### v16で実施した修正

- 低レベル生成関数の戻り値を成功`true`、失敗`false`へ統一。
- 重複key確認後にpayloadを作る`enqueueSpawnRequestIfNew()`を追加。
- requestへ`fallbackStage`、`attemptsInStage`、`totalAttempts`、`timeoutRecorded`を追加。
- Director経由では低レベル関数のretry副作用を停止。
- `recordSpawnSuccess()`へ成功カウンターを一元化。
- `advanceScheduleAfterResolution()`へ成功後schedule更新を集約。
- `buildResultSnapshot()`へSpawnDirector診断値と整合フラグを追加。

### v14 / v15 / v16固定seed比較

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

---

## P1 実効出現計測の基準

P1では、生成数ではなく、対象がCanvasへ最大18px入った時点を実効出現として測定した。

初回15km基準:

| 分類 | 実効出現数 | 最大間隔 |
| --- | ---: | ---: |
| 穴 | 16 | 1.312km / 33.02秒 |
| 通常地上障害物 | 153 | 0.232km / 5.32秒 |
| 対向障害物 | 54 | 0.483km / 11.92秒 |
| 加点アイテム | 119 | 1.332km / 30.95秒 |
| 👯‍♀️ | 8 | 1.628km / 37.22秒 |

生成物は認識可能位置まで到達しており、穴不足の主因は生成後消失ではなく、予定の競合と生成間隔だった。

---

## v18 P2 実効出現密度再調整

### 目的

SpawnDirectorの安全条件を緩めず、穴、対向障害物、加点アイテムの予約競合を解消する。

### 実装

- 穴予定が期限へ到達した場合、通常地上障害物を一時保留して穴用安全区間を作る。
- 穴生成後は`between_holes`必須障害物を優先する。
- 1〜2kmでは穴6個を優先保証し、早期対向障害物は維持する。
- 通常対向障害物が大幅に遅れた場合、穴予約を一時的に譲る。
- 通常対向障害物は失敗時も対向障害物のまま低速🚶へ縮退する。
- 加点アイテムは前回成功地点を基準に最低間隔を持ち、連続生成と長時間欠落の両方を抑制する。
- 穴requestの再試行間隔だけを短縮し、安全判定そのものは変更しない。
- 穴間必須障害物の再試行間隔は従来値を維持し、必須障害物のスキップ加速を防止する。

### 変更していないもの

- 穴幅
- 障害物速度
- 対向障害物TTC最低条件
- ジャンプ、重力、固定タイムステップ
- 当たり判定
- アイテム点数とスコア式
- UI
- ランキング、Supabase、RPC、pending key

---

## P2 30固定seedゲート

- seed: `18001`〜`18030`
- 各5km
- 合計150km
- 判定: **PASS**
- failures: `0`

| 指標 | 30seed結果 | 合格条件 |
| --- | ---: | --- |
| 0〜1kmの穴 | 全seed 6個 | 4〜6個 |
| 1〜2kmの穴 | 全seed 6個 | 6〜9個 |
| 2km以降平均穴間隔 | 0.1696〜0.1786km | 0.10〜0.18km |
| 2km以降最大穴間隔 | 0.2322km | 0.30km未満 |
| 加点アイテム | 7.0〜7.4個/km | 6〜10個/km |
| 取り逃がし対象 | 0〜0.8個/km | 0〜2個/km |
| 最大判断空白 | 0.717秒 | 1.2秒未満 |
| 最大同時危険数 | 2 | 2以下 |

整合条件:

```text
同一entity二重計数 0
不正spawnSource 0
presented > generated 0
SpawnDirector整合式 成立
console error 0
console warning 0
Supabase本番送信 0
```

---

## 150km耐久結果

| 項目 | v18結果 |
| --- | ---: |
| 穴 | 849個 |
| 障害物 | 1151個 |
| 対向障害物 | 301個 |
| 加点アイテム | 1150個 |
| 最大穴間隔 | 0.230km |
| 平均穴間隔 | 0.180km |
| 対向障害物最短TTC | 1.01秒 |
| 2km以内対向障害物最短TTC | 1.38秒 |
| 回避不能対向障害物 | 0 |
| 穴間必須障害物 | 穴849個に対して849個 |
| 穴だけ連続 | 0 |

---

## 回帰テスト

次はすべてexit 0。

```bash
node tests/effective-presentation-metrics.js
node tests/p2-density-regression.js
node tests/progressive-autoplay.js
node tests/release-comprehensive.js
node tests/endurance-150km.js
```

結果:

```text
P1実効出現計測 PASS
P2 30seedゲート PASS
release criticalIssues 0
console error 0
console warning 0
Supabase本番送信 0
unavoidableOncomingCount 0
consecutiveHoleViolationCount 0
```

`release-comprehensive`の最終判定は、Playwright未導入に関する既存warningだけを理由に`WARN`。

---

## 未確認

- iPhone SE実機での3プレイ体感
- iPhone 17 Pro実機での3プレイ体感
- 18px実効出現閾値の実機妥当性
- Playwright/WebKit自動試験
- Codeberg Pages公開版

P2の自動合格条件は満たしているが、実機3プレイの確認が終わるまでPRはDraftのままとする。


## v19 P3 判断パターン

- 既存オブジェクトだけを使う8種類の短い判断パターンを導入。
- 0〜1kmは学習用4種類だけ、1km以降に複合パターンを段階解禁。
- 10,000回選択の分布、3連続禁止、定義安全性を `tests/p3-pattern-regression.js` で検査。
- P1実効出現、P2 30seed、progressive autoplay、release comprehensive、150km耐久を同時回帰検査する。
- 実機、Playwright/WebKit、Codeberg Pagesは未確認。
