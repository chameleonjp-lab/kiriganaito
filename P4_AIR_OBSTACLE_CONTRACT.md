# kiriganaito P4 空中障害物契約

- 対象段階: `COMPLETION_PLAN_v1.md` P4
- 基準: P3 `kiriganaito-2026-07-19-v19-decision-patterns`
- 現行版: `kiriganaito-2026-07-20-v20-air-obstacle`
- 作業ブランチ: `ai/kiriganaito-v20-air-obstacle`
- Draft Pull Request: `#39`

## 1. 目的

地上障害物や穴に対して常にジャンプするだけだった判断へ、地上に留まる選択を追加します。

P4では空中障害物を1種類だけ導入します。P3までの密度、穴間必須障害物、対向障害物TTC、スコア、ランキング連携は変更しません。

## 2. 空中障害物

名称: **吊り下げバー**

表示:

- 上部から吊られた2本の支持線
- 暗色の横棒
- 黄色の警告帯
- 地上との隙間が分かる影

外部画像や既存作品の素材は使わず、Canvas図形だけで描画します。

## 3. メタデータ

```text
zone: air
movementType: world_scroll
objectRole: hazard
heightBand: mid
spawnSource: normal
airKind: hanging_bar
```

SpawnDirectorでは`AIR_OBSTACLE` requestとしてAIR queueへ登録します。

## 4. 当たり判定契約

### 地上走行

地上時の縮小済みplayer rectangleと、縮小済み空中障害物rectangleは重なりません。

```text
最低地上クリアランス: 12px以上
固定seed検査値: 29px
```

### ジャンプ

通常ジャンプの上昇・下降中は空中障害物rectangleと交差します。

接触時は既存障害物事故と同じです。

- 通常時: 事故、ペナルティ、警戒度+1、15秒逃走
- 👯‍♀️無敵時: 障害物を無効化し、事故にしない
- 穴判定には影響しない

## 5. 出現条件

```text
2.00km未満: 出現0
2.00km以降: 低頻度
逃走中: 新規出現0
👯‍♀️無敵中: 新規出現0
P3 pattern進行中: 新規出現0
穴間必須障害物待ち: 新規出現0
同時に有効な空中障害物: 最大1個
```

正式スケジュール:

```text
初回due: 2.35km
成功後の次回due: 1.10km後
自然走行での初回実出現: 約2.379〜2.387km
7km走行時: 各固定seed 4個
```

初回dueへ達しても即時生成はしません。次の安全な地上障害物成功直後まで待機します。

## 6. 正式な配置方式

P4はP2の穴・地上・対向予定を停止、延期、消費しません。

### 6-1. 地上障害物への追従

通常の地上障害物が既存安全判定を通過して生成された直後だけ、吊り下げバーを後方へ追加します。

```text
地上障害物: 通常位置
吊り下げバー初期X: -190px
吊り下げバー速度: 190px/s × 既存速度倍率
```

地上物、穴、2km以降の対向物より吊り下げバーを低速にし、先行する危険へ追いつかない構造です。

### 6-2. 同一X帯の禁止

生成時には、吊り下げバーの初期X帯と水平に重なる穴・地上障害物がないことを確認します。

自然走行中も、空中障害物と地上危険のrectangleが同一X帯へ入らないことをP4専用ゲートで検査します。

### 6-3. P2予定を変更しない

吊り下げバー成功後に次を変更しません。

- `nextHoleAt`
- `nextObstacleAt`
- `nextOncomingAt`
- P2の穴数、穴間隔、アイテム密度
- P3の判断パターン進行

AIRは既存の地上混雑数にも含めません。上下封鎖はP4専用指標で独立検査します。

## 7. P3との関係

P4の空中障害物はP3判断パターンへまだ組み込みません。

- P3の`A`は空中報酬のまま
- P3 pattern中は空中障害物を生成しない
- P3 pattern第1stepとして採用しない
- `decisionPatternSymbolForEntity()`はAIR HAZARDを地上`G`へ分類しない

空中障害物を含む複合パターンは、P4の実機確認後に別工程で判断します。

## 8. カウンター

resultSnapshotと自動artifactへ次を格納します。通常結果画面には追加しません。

```text
airObstacleSpawnCount
airObstacleContactCount
airObstacleGroundSafePassCount
airObstacleFullBlockViolationCount
airObstacleBefore2kmCount
airObstacleChaseSpawnCount
airObstacleFirstSpawnKm
```

P1実効出現計測にも`airObstacle`分類を追加します。

## 9. 自動試験結果

### 9-1. 直接検査

```text
metadata error: 0
地上クリアランス: 29px
地上状態で接触: 0
通常ジャンプで接触: 1
2km未満の直接生成: 拒否
逃走中の直接生成: 拒否
無敵中の直接生成: 拒否
1000 geometry placements failure: 0
穴との生成時競合: 拒否
地上障害物との生成時競合: 拒否
console error / warning: 0
```

### 9-2. 自然走行

seed `20001`〜`20005`、各7km:

```text
各seedの空中障害物: 4個
生成数と実効出現数: 一致
初回実出現: 約2.379〜2.387km
2km未満出現: 0
逃走中出現: 0
上下完全封鎖: 0
水平重複: 0
mandatory timeout: 0
unavoidableOncomingCount: 0
consecutiveHoleViolationCount: 0
console error / warning: 0
```

P4自然走行で記録される既存SpawnDirector全体のqueue overflowは、P4固有の合否値には使用しません。P2/P3恒久ゲートとrelease comprehensiveの整合検査を回帰判定の正本とします。

### 9-3. 全回帰

次をすべて通過しています。

```text
progressive autoplay
150km endurance
release comprehensive
P1 effective presentation
P2 30-seed density gate
P3 decision pattern gate
P4 airborne obstacle gate
```

## 10. 変更していないもの

- ジャンプ力、重力、固定タイムステップ
- 地上障害物速度
- 対向障害物TTC
- 穴幅、穴落ち判定
- P2密度目標
- P3パターン定義
- アイテム点数
- スコア式
- 通常UI
- ランキング、Supabase、RPC、pending key
- 逃走・無敵の完成調整

## 11. 実機確認

自動試験後も次を確認します。

- iPhone SE幅で支持線、警告帯、地上隙間が分かる
- iPhone 17 Proでジャンプ中の接触位置が納得できる
- 初見で「跳ばない方が安全」と理解できる
- 地上障害物や穴との完全封鎖がない
- 3プレイ中に頻出しすぎない

実機確認が終わるまでPRはDraftのまま維持します。Ready化、マージ、公開は行いません。
