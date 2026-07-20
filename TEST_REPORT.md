# kiriganaito TEST_REPORT

- 現行 CLIENT_VERSION: `kiriganaito-2026-07-20-v22-device-feedback-ui`
- 現行段階: `P5実機フィードバックUI修正`
- 基準main: `343f576d375bdf526221f36556d61308e695af4d`
- 作業ブランチ: `ai/kiriganaito-v22-device-feedback-ui`
- Draft Pull Request: `#42`
- 検証済み実装コミット: `ffa0f11cd4f8d26121889a7ff81ae064257a0635`
- 状態: 自動ゲート合格、実機再確認待ち、Draft・未マージ

---

## 1. 既存基盤

### v16 SpawnDirector正確性

- 1 requestが最大1 entityだけを生成する契約を固定。
- 重複key確認後にpayloadを生成。
- 再試行時のpayloadと乱数結果を固定。
- `fallbackStage / attemptsInStage / totalAttempts`で有限再試行化。
- 成功カウンターを`recordSpawnSuccess()`へ一元化。
- 成功後のschedule更新を一元化。

### P1 実効出現計測

対象がCanvasへ最大18px入った時点を実効出現として測定する。

P4では分類へ`airObstacle`を追加し、AIRを従来の地上障害物数へ混入させない。

### P2 実効出現密度

- 0〜1km、1〜2kmの穴数を安定化。
- 2km以降の穴間隔を固定seedで制御。
- 対向障害物TTCと2km以内保証を維持。
- 加点アイテム密度と最大判断空白を制御。

### P3 判断パターン

既存の地上障害物、穴、対向障害物、空中報酬、👯‍♀️だけを使う短い判断シーケンスを導入済み。

P4 AIR HAZARDはP3の地上`G`として採用しない。

---

## 2. P4実装内容

追加した空中障害物は1種類だけです。

```text
名称: 吊り下げバー
描画: Canvas図形
zone: air
movementType: world_scroll
objectRole: hazard
heightBand: mid
spawnSource: normal
airKind: hanging_bar
```

SpawnDirectorのAIR queueへ`AIR_OBSTACLE` requestとして登録します。

### 表示

- 2本の支持線
- 暗色の横棒
- 黄色の警告帯
- 地上との隙間を示す影

外部画像と既存作品の素材は使用していません。

---

## 3. 当たり判定

### 地上

```text
最低契約: 12px以上
固定seed検査値: 29px
地上状態での接触: 0
```

### ジャンプ

通常ジャンプ中は吊り下げバーへ接触します。

```text
直接ジャンプ接触検査: PASS
接触時 airObstacleContactCount: 1
```

接触処理は既存障害物事故を再利用します。

- 通常時: ペナルティ、警戒度+1、15秒逃走
- 👯‍♀️無敵時: 障害物事故を無効化
- 穴判定: 変更なし

---

## 4. 正式な出現方式

### スケジュール

```text
2km未満: 出現0
初回due: 2.35km
成功後の次回due: 1.10km後
同時に有効な空中障害物: 最大1個
```

### 実生成条件

初回dueへ到達しても即時生成しません。

既存安全判定を通過した通常の地上障害物が生成された直後だけ、吊り下げバーを後方へ追加します。

```text
初期X: -190px
スクロール速度: 190px/s × 既存速度倍率
地上障害物成功からの許容遅延: 0.003km以内
```

先行する地上危険より低速で追従するため、水平距離は縮まりません。

### 生成禁止

```text
逃走中
👯‍♀️無敵中
P3 pattern進行中
穴間必須障害物待ち
既存AIR HAZARDが有効
初期X帯に穴または地上障害物が存在
```

### P2/P3との分離

P4成功時に次を変更しません。

- `nextHoleAt`
- `nextObstacleAt`
- `nextOncomingAt`
- P2の穴・障害物・アイテム予定
- P3 pattern状態

AIRは従来の地上混雑数から除外し、上下封鎖はP4専用ゲートで検査します。

---

## 5. P4直接検査

| 指標 | 結果 |
| --- | --- |
| metadata生成 | PASS |
| metadata error | 0 |
| 地上クリアランス | 29px |
| 地上安全 | PASS |
| 通常ジャンプ接触 | PASS |
| 2km未満生成拒否 | PASS |
| 逃走中生成拒否 | PASS |
| 無敵中生成拒否 | PASS |
| 1000 geometry placements failure | 0 |
| 穴との初期X競合拒否 | PASS |
| 地上障害物との初期X競合拒否 | PASS |
| console error / warning | 0 / 0 |

判定: **PASS**

---

## 6. P4自然走行ゲート

seed `20001`〜`20005`、各7km。

| seed | 出現数 | 実効出現数 | 初回km | 2km未満 | 逃走中 | 水平重複 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20001 | 4 | 4 | 2.379 | 0 | 0 | 0 |
| 20002 | 4 | 4 | 2.387 | 0 | 0 | 0 |
| 20003 | 4 | 4 | 2.385 | 0 | 0 | 0 |
| 20004 | 4 | 4 | 2.380 | 0 | 0 | 0 |
| 20005 | 4 | 4 | 2.379 | 0 | 0 | 0 |

共通結果:

```text
生成数と実効出現数: 一致
airObstacleFullBlockViolationCount: 0
firstOverlap: null
mandatory timeout: 0
unavoidableOncomingCount: 0
consecutiveHoleViolationCount: 0
patternAbortedCount: 0
console error / warning: 0 / 0
```

判定: **PASS**

P4自然走行で観測されるSpawnDirector全体のqueue overflowは、既存GROUND/P3 queueを含む総数です。P4固有の合否値には使用せず、P2/P3恒久ゲートとrelease comprehensiveの整合検査を正本とします。

---

## 7. P2 30固定seed回帰

seed `18001`〜`18030`、各5km、合計150km。

| 指標 | P4適用後 | 条件 |
| --- | ---: | --- |
| 0〜1kmの穴 | 全seed 6個 | 4〜6個 |
| 1〜2kmの穴 | 全seed 6個 | 6〜9個 |
| 2km以降平均穴間隔 | 0.1657〜0.1798km | 0.10〜0.18km |
| 2km以降最大穴間隔 | 0.2311km | 0.30km未満 |
| 加点アイテム | 7.2〜7.8個/km | 6〜10個/km |
| 取り逃がし対象 | 0〜0.8個/km | 0〜2個/km |
| 最大判断空白 | 0.767秒 | 1.2秒未満 |
| 最大同時地上危険数 | 2 | 2以下 |

```text
30seed failures: 0
二重計数: 0
不正spawnSource: 0
presented > generated: 0
console error / warning: 0 / 0
```

判定: **PASS**

---

## 8. P3回帰

### 10,000回選択

```text
8パターン各1,250回
単一最大比率12.5%
同一パターン3連続0
最大連続2
定義エラー0
```

### 単体実行

```text
開始成功
完了1
中断0
解決step 3
queue overflow 0
mandatory timeout 0
穴だけ連続0
```

### P1固定seed自然走行

```text
seed 17001: 開始5 / 完了5 / 中断0
seed 17002: 開始5 / 完了5 / 中断0
seed 17003: 開始4 / 完了4 / 中断0
step skip 0
```

P4 AIRはP3の第1stepへ採用されません。

判定: **PASS**

---

## 9. 150km耐久

| 項目 | P4結果 |
| --- | ---: |
| 実走行距離 | 152.05km |
| 最終スコア | 150.00km |
| 穴 | 844個 |
| 地上障害物 | 1,134個 |
| 対向障害物 | 289個 |
| 加点アイテム | 1,186個 |
| 最大穴間隔 | 0.228km |
| 平均穴間隔 | 0.180km |
| 最大障害物間隔 | 0.178km |
| 平均障害物間隔 | 0.134km |
| 対向最短TTC | 1.01秒 |
| 2km以内最短TTC | 1.38秒 |
| 回避不能対向障害物 | 0 |
| 穴だけ連続 | 0 |

2km以内対向障害物は1個以上を維持しています。TTC最低条件は緩和していません。

判定: **PASS**

---

## 10. 最終自動ゲート

実行順:

```bash
node tests/progressive-autoplay.js
node tests/endurance-150km.js
node tests/release-comprehensive.js
node tests/effective-presentation-metrics.js
node tests/p2-density-regression.js
node tests/p3-pattern-regression.js
node tests/p4-air-obstacle-regression.js
```

結果:

```text
progressive autoplay PASS
endurance 150km PASS
release finalVerdict WARN
release criticalIssues 0
P1 effective presentation PASS
P2 30seed PASS
P3 pattern regression PASS
P4 air obstacle regression PASS
console error 0
console warning 0
Supabase本番送信 0
```

`release finalVerdict=WARN`の理由はPlaywright未導入のみです。

検証ワークフロー:

```text
Apply P4 airborne obstacle on PR
Run 29704983044
全機能ゲート・commit・push・一時ファイル削除 SUCCESS
```

---

## 11. 変更していないもの

- ジャンプ力
- 重力
- 固定タイムステップ
- 穴幅
- 穴落ち判定
- 地上障害物速度
- 対向障害物TTC最低条件
- P2密度目標
- P3パターン定義
- アイテム点数
- スコア、ペナルティ
- 通常UI
- ランキング
- Supabase URL、Publishable key
- RPC形式
- pending queue key
- 逃走・無敵の完成調整

---

## 12. 未確認

- iPhone SE実機3プレイ
- iPhone 17 Pro実機3プレイ
- 18px実効出現閾値の実機妥当性
- 吊り下げバーの初見認識性
- Playwright/WebKit
- Codeberg Pages公開版

自動合格条件は満たしています。P4はmainへ反映済みですが、実機確認は未完了です。


## v21 P5 逃走・無敵専用構成

- 15秒逃走を4フェーズへ分割。
- 逃走専用の地上、SMALL hole、報酬、2km以降対向requestを追加。
- 無敵4秒を実プレイ時間基準へ変更。
- 無敵障害物2〜3回、終了後LARGE hole抑制、突破表示を追加。
- P1〜P4、progressive、release、150km耐久を回帰ゲートとして維持する。


## v22 実機フィードバックUI修正

- 実機指摘に基づき地面を水平化。
- ホームと結果の詳細ランキングを`details`で初期非表示化。
- ホームの情報優先順位と操作配置を再構成。
- コンセプト文言を「落とした積荷と落ちてるお金を拾い集めよう」へ統一。
- 👯‍♀️無敵を実プレイ時間8秒へ延長。
- player物理サイズを維持し、🚚描画だけ36pxへ縮小。
- ルール情報を7区分へ整理。
- `tests/device-feedback-ui-regression.js`とP1〜P5全回帰で検証する。

- 8秒無敵の実効障害物提示目標は4〜6個。補完requestは2〜3個のまま維持する。


## v22 実機フィードバック最終検証

```text
CLIENT_VERSION: kiriganaito-2026-07-20-v22-device-feedback-ui
地面: 全X・visualScroll変更前後で同一groundY
ホームランキング: details / 初期closed
結果ランキング: details / 初期closed
コンセプト適用数: 3
ルール必須情報: 全項目PASS
player物理サイズ: 42x34維持
🚚描画: 36px
無敵初期値: 8秒
wall-clockのみ30秒: 8秒維持
4秒プレイ後: 約4秒
8秒プレイ後: 0秒
8秒無敵の実効障害物提示: 4個
無敵補完request計画: 3個
無敵中の穴落ち: 有効
console error / warning: 0 / 0
device-feedback-ui failures: 0
P5 failures: 0
```

検証ワークフロー `Apply device feedback UI on PR` Run `29727539458` で、progressive autoplay、150km endurance、release comprehensive、P1〜P5、専用UIゲート、artifact生成、commit、push、一時ファイル削除がすべて成功した。
