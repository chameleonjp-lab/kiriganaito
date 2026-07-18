# kiriganaito P1 実効出現計測

- 対象段階: `COMPLETION_PLAN_v1.md` の P1
- 基準実装: `kiriganaito-2026-07-12-v16-spawn-director-correctness`
- 作業ブランチ: `ai/kiriganaito-v17-effective-presentation-metrics`
- 目的: 生成数ではなく、プレイヤーがCanvas上で認識できた対象数と間隔を測定する
- この差分の性質: 計測・テストのみ。ゲームバランス、速度、当たり判定、スコア、UIは変更しない

## 1. 計測対象

次の5分類を個別に測定します。

1. 穴
2. 通常地上障害物
3. 対向障害物
4. 加点アイテム
5. パワーアップ `👯‍♀️`

各オブジェクトは、計測中に初めて認識可能位置へ入った時だけ `presented = true` とし、同じオブジェクトを2回数えません。

## 2. 認識可能位置の定義

次の条件をすべて満たした時点を実効出現とします。

```text
entity.active !== false
entity.x + min(entity.w, 18px) >= 0
entity.x < canvas width
```

これは、左端から対象の一部が入っただけの瞬間ではなく、最大18px分が画面へ入った時点を認識可能とみなす定義です。

P2の密度調整では、この定義を固定したまま生成数と実効出現数の差を比較します。実機で認識時点が不自然と判明した場合は、P1内で定義を改訂し、P2開始前に固定します。

## 3. 測定値

### 3-1. 分類別

各分類について次を記録します。

- 生成数
- 実効出現数
- 実効出現率
- 平均出現間隔（km）
- 最大出現間隔（km）
- 平均出現間隔（秒）
- 最大出現間隔（秒）

### 3-2. 空白

0.5km到達後について、穴・障害物・アイテム・パワーアップのいずれも新しく認識されない最大区間を記録します。

- 最大空白距離
- 最大空白時間

### 3-3. 同時危険数

Canvas内に同時に存在する次の対象数を測定します。

- 穴
- 通常地上障害物
- 対向障害物

これらの合計最大値を `maxSimultaneousStrongHazards` として記録します。

### 3-4. 出現理由

v14以降の `spawnSource` を使い、実効出現を次の理由別に集計します。

- `normal`
- `between_holes`
- `chase`
- `invincible`
- `early_oncoming`
- `pattern`

分類別・出現理由別の両方を記録します。

## 4. 自動計測

実行コマンド:

```bash
node tests/effective-presentation-metrics.js
```

測定条件:

- 固定seed: `17001`, `17002`, `17003`
- 1 seedあたり: `5km`
- 当たり判定と穴落ちは無効化し、同一走行内で出現測定を継続
- Supabase本番送信なし
- Canvas幅: `320px`

出力:

```text
artifacts/p1-effective-presentation-metrics.json
```

## 5. P1合格条件

自動計測では最低限、次を満たす必要があります。

```text
各seedが5kmへ到達する
同じentityを2回数えない
presented数がgenerated数を超えない
spawnSource別合計がpresented総数と一致する
不正なspawnSourceが0
全間隔値が有限値
console error 0
console warning 0
```

P1では密度値そのものを合否判定にしません。P1の役割は、P2で密度を直すための信頼できる観測値を作ることです。

## 6. 変更禁止

この作業では次を変更しません。

- `index.html` のゲーム処理
- SpawnDirectorの順序・再試行・代替
- 出現間隔
- 出現確率
- 穴幅
- 障害物速度
- 対向障害物TTC
- アイテム点数
- スコア計算
- 当たり判定
- UI
- ランキング
- Supabase

## 7. 現在の状態

このPRはP1の計測基盤を追加する最初の差分です。

- 独立したNodeハーネスで、現在の `index.html` をそのまま読み込んで測定する
- ゲーム本体のバランスを変えずに、P2の入力データを生成する
- GitHub Actionsで同じ計測を再実行できるようにする

実機上の認識しやすさは、この自動計測だけでは確定しません。P1完了判定には、後続の実機確認で「18px表示時点が認識可能か」を確認する必要があります。
