# kiriganaito P5 逃走・無敵専用構成契約

- 対象段階: `COMPLETION_PLAN_v1.md` P5
- 基準: P4 `kiriganaito-2026-07-20-v20-air-obstacle`
- 予定版: `kiriganaito-2026-07-20-v21-chase-invincible`
- 作業ブランチ: `ai/kiriganaito-v21-chase-invincible`

## 1. 目的

事故後15秒の逃走をゲームの山場として成立させ、👯‍♀️取得による4秒無敵を「実際に障害物を突破できる状態」として明確に伝えます。

P5ではスコア、ランキング、通常時のP2密度、P3パターン、P4空中障害物の基本契約を変更しません。

## 2. 変更しない中心ルール

- 事故後の逃走時間は15秒
- 逃走中の速度倍率は既存の2倍
- 警戒度3で終了
- 👯‍♀️無敵は4秒
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
chaseElapsedSec
chasePhase
chaseSessionGroundCount
chaseSessionHoleCount
chaseSessionScoreItemCount
chaseSessionOncomingCount
chaseSessionMaxDecisionBlankSec
chaseCompletedSessionCount
```

## 4. 15秒フェーズ

| 逃走経過 | フェーズ | 内容 |
| --- | --- | --- |
| 0〜1秒 | grace | 新しい強い危険を生成しない理解時間 |
| 1〜6秒 | ground_reward | 地上障害物と加点報酬を交互に提示 |
| 6〜12秒 | mixed | 小穴、必須地上障害物、報酬、対向を混在 |
| 12〜15秒 | finale | 小穴、報酬、対向による短い最終判断 |

通常時の予定は逃走中に消費しません。逃走終了後にP2の通常予定を安全側へ再開します。

## 5. 専用イベント計画

### 5-1. 1〜6秒

```text
1.05 score
1.65 ground
2.30 score
2.95 ground
3.60 score
4.25 ground
4.90 score
5.55 ground
```

### 5-2. 6〜12秒

```text
6.20 small_hole
6.85 score
7.50 oncoming_if_2km
8.20 small_hole
8.90 score
9.60 small_hole
10.30 oncoming_if_2km
```

### 5-3. 12〜15秒

```text
12.15 small_hole
12.80 score
13.70 oncoming_if_2km
```

穴後の必須障害物は既存契約を維持し、逃走中は地上方向へ固定します。

## 6. 1回の逃走での保証

正常終了した15秒セッションでは次を目標範囲とします。

```text
地上障害物: 5〜8
穴: 2〜4
加点アイテム: 4〜7
2km以降の対向障害物: 1〜3
👯‍♀️追加生成: 0
```

P5専用地上4個と、小穴後の必須地上障害物を合わせて最大8個に収めます。

2kmへ到達していないセッションでは、対向障害物0個を許容します。2km到達後は最低1個を保証します。

## 7. 逃走中の安全契約

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

## 8. 無敵4秒

無敵残時間は`performance.now()`の期限ではなく、PLAYING中の固定タイムステップ`dt`だけで減算します。

```text
取得直後: 4.000秒
PLAYING update 240回: 0秒
バックグラウンド中: 減算0
速度倍率: 無関係
```

### 8-1. 障害物提示

無敵セッションごとに目標数を2個または3個へ固定します。

- 通常予定で提示された障害物も目標数へ含める
- 不足分だけ`spawnSource=invincible`で補う
- 逃走中はP5逃走構成を優先し、追加のINVINCIBLE requestを増やさない

### 8-2. 終了直後

無敵終了時に大穴抑制区間を設定します。

```text
無敵終了後0.14km以内: LARGE hole禁止
SMALL / MEDIUM: 既存安全判定を満たせば可
```

### 8-3. 突破表示

無敵で障害物事故を防いだ場合は次を表示します。

```text
無敵で突破!
```

カウンター`invinciblePreventedAccidents`を1回だけ増加します。

## 9. 計測

resultSnapshotと自動artifactへ最低限次を格納します。

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
invincibleSessionCount
invinciblePresentedObstacleCount
invinciblePreventedAccidents
invincibleBackgroundDecayViolationCount
invincibleLargeHoleViolationCount
```

通常結果画面には内部診断値を追加しません。

## 10. 自動合格条件

### 逃走

```text
15秒が速度倍率に影響されない
0〜1秒のP5専用危険0
地上5〜8
穴2〜4
加点4〜7
2km以降の対向1〜3
👯‍♀️追加0
最大判断空白 <= 0.70秒を目標
避け不能配置0
TTC最低条件維持
穴だけ連続0
```

### 無敵

```text
固定step 240回で4秒終了
performance clockだけを進めても残時間不変
速度倍率に影響されない
障害物提示2〜3
穴落ち有効
終了直後LARGE hole 0
防止事故表示とカウンター一致
```

### 回帰

```text
progressive autoplay PASS
150km endurance PASS
release comprehensive criticalIssues 0
P1 PASS
P2 PASS
P3 PASS
P4 PASS
console error / warning 0
Supabase本番送信0
```

## 11. 変更禁止

- 通常時のP2密度目標
- P3パターン定義
- P4吊り下げバーの高さ、速度、出現条件
- ジャンプ力、重力、固定タイムステップ
- 穴幅、穴落ち判定
- 対向TTC最低条件
- スコア式、アイテム点数、ペナルティ
- 通常UI、結果UI
- ランキング、Supabase、RPC、pending key

## 12. 実機確認

- 事故直後1秒が状況理解に使える
- 1〜6秒で逃走開始を理解できる
- 6〜12秒で山場として密度が上がる
- 12〜15秒が短い最終判断として認識できる
- 赤演出が危険物を隠さない
- 無敵残時間がバックグラウンド復帰後も維持される
- 「無敵で突破!」が接触位置付近で読める

実機確認が終わるまでPRはDraftのまま維持します。
