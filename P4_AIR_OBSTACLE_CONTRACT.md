# kiriganaito P4 空中障害物契約

- 対象段階: `COMPLETION_PLAN_v1.md` P4
- 基準: P3 `kiriganaito-2026-07-19-v19-decision-patterns`
- 予定版: `kiriganaito-2026-07-20-v20-air-obstacle`
- 作業ブランチ: `ai/kiriganaito-v20-air-obstacle`

## 1. 目的

地上障害物や穴に対して常にジャンプするだけだった判断へ、地上に留まる選択を追加します。

P4では空中障害物を1種類だけ導入します。P3までの密度、穴間必須障害物、対向障害物TTC、スコア、ランキング連携は変更しません。

## 2. 空中障害物

名称: 吊り下げバー

表示:

- 上部から吊られた2本の支持線
- 暗色の横棒
- 黄色の警告帯
- 地上との隙間が視覚的に分かる影

外部画像や既存作品の素材は使いません。Canvas図形だけで描画します。

## 3. メタデータ

```text
zone: air
movementType: world_scroll
objectRole: hazard
heightBand: mid
spawnSource: normal
```

SpawnDirectorでは `AIR_OBSTACLE` requestとしてAIR queueへ登録します。

## 4. 当たり判定契約

### 地上走行

地上時の縮小済みplayer rectangleと、縮小済み空中障害物rectangleは重ならないこと。

最低地上クリアランス:

```text
12px以上
```

### ジャンプ

通常ジャンプの上昇・下降中に、空中障害物rectangleと交差できる高さとします。

空中障害物との接触は既存障害物事故と同じです。

- 通常時: 事故、ペナルティ、警戒度+1、15秒逃走
- 👯‍♀️無敵時: 障害物を無効化し、事故にしない
- 穴判定には影響しない

## 5. 出現条件

```text
2.00km未満: 出現0
2.00km以降: 低頻度
逃走中: 新規出現0
無敵中: 新規出現0
P3 pattern進行中: 新規出現0
穴間必須障害物待ち: 新規出現0
```

初回予定:

```text
2.20〜2.55km
```

次回間隔:

```text
0.90〜1.30km
```

この範囲は初期値です。P1/P2/P3回帰を壊す場合は、頻度を下げる方向だけ調整できます。

## 6. 上下完全封鎖の禁止

空中障害物を生成する時点で、次を禁止します。

- 画面へ接近中の穴
- 画面へ接近中の地上障害物
- 画面へ接近中の対向障害物
- 近距離に期限が来る穴・地上・対向request

空中障害物成功後は、既存の次回予定を安全側へ繰り下げます。

```text
次の地上障害物: 空中障害物から0.16km以上
次の穴: 空中障害物から0.18km以上
次の対向障害物: 空中障害物から0.20km以上
```

既に成立しているP2/P3の安全距離は短縮しません。

## 7. P3との関係

P4の空中障害物はP3判断パターンへまだ組み込みません。

- P3 `A` は空中報酬のまま
- 空中障害物は独立した低頻度request
- P3 pattern中は空中障害物を生成しない
- P3 pattern第1stepとして採用しない

空中障害物を含む複合パターンは、P4の実機確認後に別途判断します。

## 8. カウンター

最低限次を記録します。

```text
airObstacleSpawnCount
airObstacleContactCount
airObstacleGroundSafePassCount
```

resultSnapshotと自動artifactへ格納し、通常結果画面には追加しません。

## 9. 自動合格条件

```text
地上クリアランス >= 12px
地上状態で接触0
通常ジャンプ状態で接触1
2km未満出現0
逃走中出現0
無敵中出現0
1000配置で上下完全封鎖0
queue overflow 0
mandatory timeout 0
unavoidableOncomingCount 0
consecutiveHoleViolationCount 0
P1/P2/P3ゲート維持
console error / warning 0
Supabase本番送信0
```

## 10. 変更禁止

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

- iPhone SE幅で上部支持線と地上隙間が分かる
- iPhone 17 Proでジャンプ中の接触位置が納得できる
- 初見で「跳ばない方が安全」と理解できる
- 地上障害物や穴との完全封鎖がない
- 3プレイ中に頻出しすぎない

実機確認が終わるまでPRはDraftのまま維持します。
