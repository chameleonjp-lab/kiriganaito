# kiriganaito P5 逃走・無敵専用構成契約

- 対象段階: `COMPLETION_PLAN_v1.md` P5
- 基準: P4 `kiriganaito-2026-07-20-v20-air-obstacle`
- 現行候補版: `kiriganaito-2026-07-20-v22-device-feedback-ui`
- 作業ブランチ: `ai/kiriganaito-v21-chase-invincible`
- Draft Pull Request: `#41`

## 1. 目的

事故後15秒の逃走をゲームの山場として成立させ、👯‍♀️取得による4秒無敵を「実際に障害物を突破できる状態」として明確に伝えます。

P5ではスコア、ランキング、通常時のP2密度、P3判断パターン、P4空中障害物の基本契約を変更しません。

## 2. 維持する中心ルール

- 事故後の逃走時間は15秒
- 逃走中の速度倍率は既存の2倍
- 警戒度3で終了
- 👯‍♀️無敵は実プレイ時間8秒
- 無敵対象は障害物事故だけ
- 穴は無敵中でも即終了
- 1段ジャンプのみ
- 対向障害物のTTC最低条件を緩和しない

## 3. 逃走セッション

事故ごとに新しい逃走セッションを開始します。

同一逃走中に再事故が発生した場合は、旧セッションの未解決P5 requestを破棄し、新しい15秒セッションとして再開始します。警戒度3へ到達した場合は従来どおり終了します。

記録項目:

```text
chaseSessionId
chaseSessionCount
chaseCompletedSessionCount
chaseElapsedSec
chasePhase
chaseSessionGroundCount
chaseSessionHoleCount
chaseSessionScoreItemCount
chaseSessionOncomingCount
chaseSessionMaxDecisionBlankSec
chaseLastSessionSummary
```

## 4. 15秒フェーズ

| 逃走経過 | フェーズ | 内容 |
| --- | --- | --- |
| 0〜1秒 | grace | 新しい強い危険を生成しない理解時間 |
| 1〜6秒 | ground_reward | 地上障害物と高所報酬を中心に提示 |
| 6〜12秒 | mixed | 小穴、必須地上障害物、報酬、対向を混在 |
| 12〜15秒 | finale | 小穴と報酬による短い最終判断 |

通常時の予定は逃走中に消費しません。逃走終了後にP2通常予定を安全側へ再開します。

## 5. 検証済み専用イベント計画

### 5-1. 1〜6秒

```text
1.05 score_high
1.25 ground
3.20 ground
4.00 score_high
5.15 ground
```

### 5-2. 6〜12秒

```text
6.00 score_high
6.85 small_hole
7.80 score_high
9.50 score_high
10.15 ground
10.95 oncoming_if_2km
11.80 score_high
```

### 5-3. 12〜15秒

```text
13.40 small_hole
14.10 score_high
```

穴後の必須障害物は既存契約を維持し、逃走中は地上方向へ固定します。

専用地上4個と小穴後の必須地上2個から、実効出現は地上5個に収束します。2個目の必須地上は15秒終了境界付近となるため、固定seedでの正式保証値は5個です。

## 6. 高所報酬の扱い

P5報酬は次の契約で提示します。

```text
lane: high
challenge: false
placed: true
speedMult: 0.70
```

危険物と同じ操作を強要せず、低速で画面に残すことで判断空白を埋めます。

報酬はP5専用requestに限り、安全に重ねられる高所報酬として配置します。P4 AIR HAZARDは逃走中に生成しません。

## 7. 1回の逃走での保証

正常終了した15秒セッションの検証済み値:

### 2km以降

```text
地上障害物: 5
穴: 2
加点アイテム: 7
対向障害物: 1
👯‍♀️追加生成: 0
最大判断空白: 0.20秒
最大同時危険数: 1
```

### 2km未満

```text
地上障害物: 5
穴: 2
加点アイテム: 7
対向障害物: 0
👯‍♀️追加生成: 0
最大判断空白: 0.284秒以下
```

一般許容範囲は次を維持します。

```text
地上障害物: 5〜8
穴: 2〜4
加点アイテム: 4〜7
2km以降の対向障害物: 1〜3
2km未満の対向障害物: 0〜3
👯‍♀️追加生成: 0
```

## 8. 逃走中の安全契約

- 0〜1秒はP5専用危険0
- 穴は`SMALL`のみ
- 穴後の必須障害物を省略しない
- 対向障害物は既存TTC判定を通過させる
- P3 patternを開始しない
- P4 AIR HAZARDを新規生成しない
- 逃走中の👯‍♀️を新規生成しない
- 同時に相反する操作を要求しない
- `unavoidableOncomingCount = 0`
- `consecutiveHoleViolationCount = 0`
- 15秒終了後にP5 requestを残さない

## 9. 無敵8秒

無敵残時間は`performance.now()`の期限ではなく、PLAYING中の固定タイムステップ`dt`だけで減算します。

```text
取得直後: 8.000秒
PLAYING update 120回後: 約6.000秒
PLAYING update 240回後: 約4.000秒
PLAYING update 480回後: 0秒
performance clockだけを30秒進めた場合: 8.000秒のまま
速度倍率: 無関係
```

浮動小数残差は`1e-9`以下で0へクランプし、終了処理を必ず1回実行します。

### 9-1. 障害物提示

無敵セッションごとの補完request数を2個または3個へ固定し、通常予定を含む8秒間の実効提示総数を4〜6個とします。

- 通常予定やP4 AIRを含む、同一無敵セッション中に実際に画面へ入った障害物を数える
- 不足分だけ`spawnSource=invincible`で補う
- 補充分は`x=-18`から提示し、8秒以内に認識可能状態へ入れる
- 逃走中はP5逃走構成を優先し、追加INVINCIBLE requestを増やさない
- 生成時ではなく18px認識可能位置への進入時に提示数を加算する

固定seed検証値:

```text
計画数: 3
実効提示数: 3
未解決request: 0
```

### 9-2. 終了直後

無敵終了時に大穴抑制区間を設定します。

```text
無敵終了後0.14km以内: LARGE holeをMEDIUMへ格下げ
0.14km通過後: LARGE holeを再許可
SMALL / MEDIUM: 既存安全判定を満たせば可
```

### 9-3. 突破表示

無敵で障害物事故を防いだ場合は次を表示します。

```text
無敵で突破!
```

- `invinciblePreventedAccidents`を1回増加
- 障害物を無効化
- 警戒度を増加させない
- `invincibleBreakthroughFlash`を0.85秒設定

### 9-4. 穴

無敵中でも穴落ちは有効です。

```text
終了理由: 穴に落ちました
無敵残時間: 消費せず終了
```

## 10. 計測

resultSnapshotと自動artifactへ次を格納します。

```text
chaseSessionCount
chaseCompletedSessionCount
chaseGroundPresentedCount
chaseHolePresentedCount
chaseScoreItemPresentedCount
chaseOncomingPresentedCount
chaseMaxDecisionBlankSec
chaseGraceHazardViolationCount
chaseCountRangeViolationCount
chaseLastSessionSummary
invincibleSessionCount
invinciblePresentedObstacleCount
invinciblePreventedAccidents
invincibleBackgroundDecayViolationCount
invincibleLargeHoleViolationCount
```

通常結果画面には内部診断値を追加しません。

## 11. 自動検証結果

### 逃走

seed `21001`〜`21005`、各2.5km開始:

```text
逃走時間: 15.000秒
地上: 各5
穴: 各2
加点: 各7
対向: 各1
👯‍♀️追加: 各0
最大判断空白: 各0.20秒
grace hazard violation: 0
count range violation: 0
避け不能対向: 0
穴だけ連続: 0
孤立P5 request: 0
console error / warning: 0
```

2km未満seed `21999`:

```text
地上5 / 穴2 / 加点7 / 対向0 / 👯‍♀️追加0
最大判断空白0.284秒以下
```

### 無敵

```text
wall-clock 30秒経過による減算: 0
固定step 240回で終了: PASS
速度倍率変更後も4秒: PASS
障害物実効提示3: PASS
終了後0.14km LARGE抑制: PASS
抑制後LARGE再許可: PASS
突破表示1回: PASS
警戒度増加0: PASS
穴落ち有効: PASS
console error / warning: 0
```

### 回帰

同一適用ワークフローRun `29706911275`で次をすべて通過しています。

```text
progressive autoplay PASS
150km endurance PASS
release comprehensive PASS
P1 effective presentation PASS
P2 density PASS
P3 pattern PASS
P4 airborne obstacle PASS
P5 chase and invincible PASS
検証済みcommit / push PASS
一時ファイル削除 PASS
```

## 12. 変更していないもの

- 通常時のP2密度目標
- P3パターン定義
- P4吊り下げバーの高さ、速度、通常出現条件
- ジャンプ力、重力、固定タイムステップ
- 穴幅、穴落ち判定
- 対向TTC最低条件
- スコア式、アイテム点数、ペナルティ
- 通常UI、結果UI
- ランキング、Supabase、RPC、pending key

## 13. 実機確認

- 事故直後1秒が状況理解に使える
- 1〜6秒で逃走開始を理解できる
- 6〜12秒で山場として密度が上がる
- 12〜15秒が短い最終判断として認識できる
- 高所報酬が危険物を隠さない
- 赤演出が危険物を隠さない
- 無敵残時間がバックグラウンド復帰後も維持される
- 「無敵で突破!」が接触位置付近で読める

実機確認が終わるまでPR #41はDraftのまま維持します。Ready化、マージ、公開は行いません。
