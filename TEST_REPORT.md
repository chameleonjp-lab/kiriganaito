# kiriganaito TEST_REPORT

- 現行 CLIENT_VERSION: `kiriganaito-2026-07-19-v19-decision-patterns`
- 現行段階: `P3 地上・空中報酬・穴の判断パターン`
- 基準main: `bc7aef38e3502d22266b9466f2ab1064cb1b7f30`
- 作業ブランチ: `ai/kiriganaito-v19-decision-patterns`
- Draft Pull Request: `#38`
- 最終実装コミット: `e748bde5a0471ea6b9a39b82a199a930a4844415`
- 最終テストゲートコミット: `4cacf330a7d30718c23c2212afc64515d99c8a53`
- 状態: 自動ゲート合格、実機未確認、Draft維持

---

## 1. これまでの基盤

### v16 SpawnDirector正確性

- 1 requestが最大1 entityだけを生成する契約を固定。
- 重複key確認後にpayloadを作成。
- 再試行時の乱数結果を固定。
- `fallbackStage / attemptsInStage / totalAttempts`で有限再試行化。
- 成功カウンターを`recordSpawnSuccess()`へ一元化。
- 成功後のschedule更新を一元化。

### P1 実効出現計測

対象がCanvasへ最大18px入った時点を実効出現として測定する。

P1初回基準:

| 分類 | 実効出現数 | 最大間隔 |
| --- | ---: | ---: |
| 穴 | 16 / 15km | 1.312km / 33.02秒 |
| 通常地上障害物 | 153 / 15km | 0.232km / 5.32秒 |
| 対向障害物 | 54 / 15km | 0.483km / 11.92秒 |
| 加点アイテム | 119 / 15km | 1.332km / 30.95秒 |
| 👯‍♀️ | 8 / 15km | 1.628km / 37.22秒 |

生成物は認識可能位置へ到達しており、当時の穴不足は生成後消失ではなく、予約競合と生成間隔が主因だった。

### P2 実効出現密度

- 穴予約時に通常地上予定を一時保留。
- 穴間必須障害物を優先。
- 0〜1km、1〜2kmの穴を安定化。
- 対向障害物と穴の予約競合を調整。
- 加点アイテムの最低間隔と期限超過予約を導入。
- TTC、速度、穴幅、当たり判定は変更していない。

---

## 2. P3実装内容

既存オブジェクトだけを使い、短い判断シーケンスを導入した。

記号:

```text
G: 通常方向の地上障害物
O: 対向障害物
A: 空中報酬
H: 穴
P: 👯‍♀️
S: 危険物を置かない安全距離
```

### 0〜1kmの学習用

- `G_S_H`
- `H_S_G`
- `G_A`
- `H_A`

### 1km以降の複合パターン

- `O_S_H`
- `H_S_O`
- `G_A_H`

### 2km以降かつ👯‍♀️出現可能時

- `P_G_G`

### 自然走行で使用するパターン

P2の最大穴間隔0.30kmを維持するため、自然走行では次を使用する。

- `G_S_H`
- `H_S_G`
- `G_A`
- `H_A`
- `G_A_H`
- `P_G_G`

`H_S_O`と`O_S_H`は、安全距離契約上、P2最大穴間隔と常用を両立しないため、定義・選択分布・単体実行の検証対象として保持する。

### 開始方式

独立した新規出現として開始せず、既に安全条件を通過して生成された通常または穴間必須の第1オブジェクトをパターン第1ステップとして採用する。

これにより、P3開始のための新しい空白や、P2の予定置換を増やさない。

---

## 3. P3安全契約

- 同一時刻に危険物を2個重ねない。
- 同時配置は「危険1個 + 報酬1個」だけ。
- `G→H`, `H→G`, `H→O`, `O→H`は既存安全距離以上。
- 穴後のパターン内`G/O`は穴間必須障害物を担当できる。
- 既存TTC、混雑判定、穴落ち判定を通過させる。
- 逃走・無敵への状態変化、期限超過、step失敗時は通常SpawnDirectorへ復帰する。
- 新しい操作、障害物、アイテムは追加しない。

---

## 4. 10,000回選択ゲート

| 指標 | 結果 | 条件 |
| --- | ---: | --- |
| 定義安全エラー | 0 | 0 |
| 各8パターンの選択数 | 各1,250回 | 偏りなし |
| 単一パターン最大比率 | 12.5% | 25%以下 |
| 同一パターン3連続 | 0 | 0 |
| 最大連続数 | 2 | 2以下 |

判定: **PASS**

---

## 5. 単体パターン実行ゲート

対象: `G_A_H`

| 指標 | 結果 |
| --- | ---: |
| 開始 | 成功 |
| 完了 | 1 |
| 中断 | 0 |
| 解決step | 3 |
| entity metadata step | 0, 1, 2 |
| queue overflow | 0 |
| mandatory timeout | 0 |
| 穴だけ連続 | 0 |

判定: **PASS**

---

## 6. 自然走行P1固定seed

| seed | 開始 | 完了 | 中断 | 解決step | pattern提示entity | 最大同一連続 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 17001 | 5 | 5 | 0 | 11 | 6 | 2 |
| 17002 | 5 | 5 | 0 | 11 | 6 | 1 |
| 17003 | 4 | 4 | 0 | 8 | 4 | 1 |

- 完了率: 100%
- step skip: 0
- 自然走行で`spawnSource=pattern`を確認。
- 最大判断空白: 0.667秒以下。

判定: **PASS**

---

## 7. P2 30固定seed回帰

seed `18001`〜`18030`、各5km、合計150km。

| 指標 | P3適用後 | 条件 |
| --- | ---: | --- |
| 0〜1kmの穴 | 全seed 6個 | 4〜6個 |
| 1〜2kmの穴 | 全seed 6個 | 6〜9個 |
| 2km以降平均穴間隔 | 0.1657〜0.1798km | 0.10〜0.18km |
| 2km以降最大穴間隔 | 0.2311km | 0.30km未満 |
| 加点アイテム | 7.2〜7.8個/km | 6〜10個/km |
| 取り逃がし対象 | 0〜0.8個/km | 0〜2個/km |
| 最大判断空白 | 0.767秒 | 1.2秒未満 |
| 最大同時危険数 | 2 | 2以下 |

- failures: 0
- 同一entity二重計数: 0
- 不正spawnSource: 0
- presented > generated: 0
- console error / warning: 0

判定: **PASS**

---

## 8. 150km耐久

standalone endurance artifact:

| 項目 | P3結果 |
| --- | ---: |
| 穴 | 844個 |
| 障害物 | 1,139個 |
| 対向障害物 | 295個 |
| 加点アイテム | 1,188個 |
| 最大穴間隔 | 0.228km |
| 平均穴間隔 | 0.181km |
| 対向障害物最短TTC | 1.01秒 |
| 2km以内最短TTC | 1.38秒 |
| 回避不能対向障害物 | 0 |
| 穴だけ連続 | 0 |

release内部150kmハーネス:

```text
対向障害物 292個
回帰下限 290個
0.8km未満の対向障害物 0
2km以内の対向障害物 1以上
最短TTC 0.848秒
2km以内最短TTC 1.160秒
回避不能 0
```

P2 standalone基準301個に対し約2%の差であり、回帰下限290個を満たす。個数許容差を設けても、TTCと回避不能0の条件は緩和しない。

---

## 9. 最終自動ゲート

実行順:

```bash
node tests/progressive-autoplay.js
node tests/endurance-150km.js
node tests/release-comprehensive.js
node tests/effective-presentation-metrics.js
node tests/p2-density-regression.js
node tests/p3-pattern-regression.js
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
console error 0
console warning 0
Supabase本番送信 0
```

`release finalVerdict=WARN`の理由はPlaywright未導入のみ。

検証ワークフロー:

- `Apply P3 decision patterns on PR` Run `29650896741`: SUCCESS
- `Finalize P3 test gates on PR` Run `29651062086`: SUCCESS

---

## 10. 変更していないもの

- ジャンプ
- 重力
- 固定タイムステップ
- 穴幅
- 穴落ち判定
- 障害物速度
- TTC最低条件
- スコア、ペナルティ
- 通常UI、Canvas描画
- ランキング
- Supabase URL、Publishable key
- RPC形式
- pending queue key

---

## 11. 未確認

- iPhone SE実機3プレイ
- iPhone 17 Pro実機3プレイ
- 18px実効出現閾値の実機妥当性
- Playwright/WebKit
- Codeberg Pages公開版

自動合格条件は満たしている。実機確認が終わるまでPR #38はDraftのまま維持し、Ready化・マージ・公開は行わない。
