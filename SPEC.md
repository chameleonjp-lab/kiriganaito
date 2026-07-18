# kiriganaito SPEC

Version: `kiriganaito-2026-07-11-v14-world-zones`

## 固定設定
- `GAME_SLUG`、`PUBLIC_URL`、Supabase URL、Publishable key、RPC パス、RPC 引数、pending queue キー、旧キー移行処理は変更しません。
- ランキング送信は `/rest/v1/rpc/submit_score` を使い、`p_game_slug`、`p_display_name`、`p_score`、`p_client_version` のみを送ります。`p_score` は整数メートルです。
- `index.html` 1 ファイル構成、外部ライブラリなし、穴即終了、警戒度3終了、2段ジャンプなしを維持します。
- ホーム画面、結果画面、HTML meta の client version は `kiriganaito-2026-07-11-v14-world-zones` に統一します。

## v7 スコア計算
結果画面の大きな記録、`resultSnapshot.score`、ランキング RPC の `p_score` は同じ `scoreMeters` を使います。Supabase/RPC/ランキング payload 形状は変更しません。

新しい計算式:

```js
基礎距離 = 実走行距離 + アイテム加算
総ペナルティ = 事故ペナルティ + 取り逃がしペナルティ
ペナルティ適用上限 = Math.round(基礎距離 * 0.5)
実適用ペナルティ = Math.min(総ペナルティ, ペナルティ適用上限)
最終スコア = 基礎距離 - 実適用ペナルティ
```

実走行距離がある限り、事故ペナルティや取り逃がしペナルティだけで記録を完全に 0 にしません。結果画面には、実走行距離、アイテム加算、基礎距離、事故ペナルティ、取り逃がしペナルティ、総ペナルティ、ペナルティ適用上限、実適用ペナルティ、カットされたペナルティ、最終スコアを表示します。

`zeroReason` は `normal_non_zero`、`penalty_capped`、`bug_zero_run`、`bug_render_stale` のいずれかです。実走行距離があるのに最終スコアが 0 の場合は表示または計算のバグとして扱います。

## アイテムと取り逃がしペナルティ
- 加点アイテムは高密度化し、💰 70%、🔩 15%、⚙️ 15% を基本にします。
- 💰 は取り逃がしペナルティなしです。
- 🔩/⚙️ の通常配置は `missPenalty = 0` にし、取り逃がし対象のチャレンジアイテムだけ少数に制限します。
- 加点アイテムを増やしても取り逃がしペナルティが比例して暴走しないよう、チャレンジ比率とペナルティ適用上限で二重に制限します。
- 結果画面には、加点アイテム出現数、加点アイテム取得数、取得率、取り逃がし対象アイテム数、取り逃がし発生数、取り逃がしペナルティを表示します。

## 👯‍♀️ 無敵
- 👯‍♀️取得時の無敵は `performance.now()` ベースの実時間4秒です。
- 判定は `nowMs() < run.dancerInvincibleUntil` 相当で行い、ゲーム速度倍率、逃走モード、ロジック dt によって短縮されません。
- 無敵は障害物事故のみ無効化します。穴には無敵中でも落ち、即終了します。
- 無敵取得後は 0.4〜1.2 秒相当以内から障害物を出し、4秒以内に 2〜3 個の障害物を計画的に出します。穴を無敵直後に詰め込みすぎません。
- 結果画面には無敵中に出た障害物数、無敵で防いだ事故数を表示します。

## 対向/接近障害物
- 0.80km 未満では対向/接近障害物を出しません。序盤の初見殺しを避けます。
- 対向障害物は 0.80km 以降に低頻度で予告的に出始めます。0.80〜1.50km は 0.35〜0.55km ごとに候補を作ります。
- 1.50〜2.00km は強制候補を動かし、2.00km 以内に最低1回は対向障害物を実出現させます。安全距離不足の場合は 0.02〜0.04km 後に短距離再試行します。
- 2.00km 以降は通常スケジュールで出します。2.00〜5.00km は 0.12〜0.22km、5.00km 以降は 0.09〜0.18km、逃走中かつ2.00km以降は 0.07〜0.14km ごとに候補を作ります。
- 安全距離やTTCが不足しそうな場合でも、対向障害物の出現数を減らして安全化するのではなく、専用速度倍率と初期位置で反射回避可能性を確保します。TTC不足時はまず対向障害物の速度を下げ、速度調整でも安全化できない場合のみ生成を却下します。
- 0.80〜2.00km の対向障害物は低速の学習用です。0.80〜1.50km は歩行者・ランナー中心で最低TTC 0.90秒以上、1.50〜2.00km は自転車までを基本にして最低TTC 0.80秒以上を維持します。
- 2.00km 以降にバイク・車を段階的に解禁します。5.00km 以降や逃走中でも、避け不能になる速度は禁止し、逃走中でも最低TTC 0.50秒未満は禁止します。
- 結果画面には対向障害物候補数、対向障害物出現数、対向障害物失敗再試行数、2km以内対向障害物出現数、2km以内対向障害物候補数、2km以内対向障害物再試行数、速度調整数、平均/最小/最大速度倍率、TTC不足による最終却下数を表示します。

## 穴間必須障害物
- 穴と穴の間には、必ず1つ以上の通常障害物または対向障害物を出します。穴だけが連続する配置は禁止します。
- 穴生成に成功したら `spawn.needObstacleBeforeNextHole` を true にし、障害物生成に成功するまで次の穴を禁止または短距離延期します。障害物生成に成功したら false に戻し、次の穴を生成可能にします。
- 穴間必須障害物にも 0.80km 以降は対向障害物を一定比率で混ぜます。0.00〜0.80km は通常障害物のみ、0.80〜1.50km は通常障害物 85% / 対向障害物 15%、1.50〜2.00km は通常障害物 75% / 対向障害物 25%、2.00〜5.00km は通常障害物 65% / 対向障害物 35%、5.00km 以降は通常障害物 55% / 対向障害物 45%、逃走中かつ2.00km以降は通常障害物 45% / 対向障害物 55% を目安にランダムに混ぜます。
- 対向障害物が安全距離不足で出せない場合は通常障害物へフォールバックし、「対向障害物候補だけ増えて出現しない」状態や長距離プレイで `betweenHoleOncomingSpawnCount` が 0 のままになる状態を避けます。
- 穴直後 0.07km 以内、大穴直後 0.22km 以内の通常障害物、大穴直後 0.28km 以内の対向障害物、障害物直後 0.07km 以内の穴、対向障害物直後 0.18km 以内の大穴は禁止します。穴を越えた着地地点の即障害物、障害物直後の即穴、穴+障害物+穴で1回ジャンプでは処理不能な配置、2段ジャンプ必須配置を作りません。
- 結果画面には穴間必須障害物出現数、穴間通常障害物出現数、穴間対向障害物出現数、穴間障害物生成失敗再試行数、穴だけ連続した回数を表示します。`consecutiveHoleViolationCount` は通常 0 でなければいけません。

## アイテム配置の競技性
加点アイテムは10倍級に増やしつつ、低い位置、中間位置、高い位置、穴の手前、穴の奥、障害物の後、障害物の前を混ぜます。同じ高さ・同じ間隔・同じジャンプリズムが3個以上続かないよう、`run.lastItemLane` と `run.lastItemTimingType` で直近配置を避けます。2段ジャンプ必須、取れない高さ、完全な運任せ配置は禁止します。

## 密度と逃走中
「何もない道」は、画面内または直近予定に穴・障害物・加点アイテム・無敵アイテムがない状態です。v8 では穴、障害物、加点アイテム、対向障害物のスケジュールを独立させ、同じフレームで複数種が出せるようにし、最大数も増やして空白率を従来の半分に近づけます。結果画面またはテストには最大空白時間、最大空白距離、空白率を出します。

逃走開始直後 0.7 秒は短い余白を置き、その後は 0.4〜0.8 秒ごとに小穴、静止障害物、加点アイテム、2km以降の対向障害物を追加します。👯‍♀️ の比率は増やしません。結果画面には `run.chaseObstacleSpawnCount`、`run.chaseHoleSpawnCount`、`run.chaseScoreItemSpawnCount`、`run.chaseOncomingSpawnCount` を表示します。

## 速度上昇
1kmごとに `getRunSpeedMultiplier(km) = Math.min(1.35, 1 + Math.floor(km) * 0.035)` で速度を少しずつ上げます。実走行距離加算、道路スクロール、穴、障害物、アイテム、対向障害物、逃走中倍率との組み合わせに使います。ジャンプ力と重力は変更しません。結果画面には最大速度倍率を表示します。

## テスト方針
- `node tests/progressive-autoplay.js`
- `node tests/release-comprehensive.js`
- 可能なら `node tests/endurance-150km.js`
- client version、旧文字列なし、`.children = []` なし、結果内訳、診断値、ペナルティ上限、p_score 一致、無敵実時間4秒、無敵中障害物、対向障害物、配置リズム、逃走中密度、空白率、速度倍率、Supabase本番送信なし、console error/warning なしを確認します。

## v7 result DOM / density hotfix
- CLIENT_VERSION は `kiriganaito-2026-07-11-v14-world-zones`。
- 結果画面の `resultComment` は DOM キャッシュ `el` に登録し、`finishGame()` は `buildResultSnapshot()`、`renderResultHeader()`、`renderResultBreakdown()`、`renderResultVersion()` の段階描画に分割する。
- 結果内訳はランキング欄より上に、記録の内訳、プレイ内容、出現数、診断、ランキング送信 payload の `p_score`、`zeroReason`、version を表示する。
- 穴生成失敗時は通常間隔を再加算せず `retryHoleSoon(km)` により 0.006〜0.014km で短距離リトライする。小穴中心に増やし、穴同士の接触と2段ジャンプ必須配置は禁止する。
- 0.80km以降の対向障害物は `retryOncomingSoon(km)` で 0.02〜0.04km 後に再試行し、候補だけ増えて出現しない状態を避ける。対向障害物候補数、出現数、失敗再試行数を結果に表示する。
- Supabase は既存 RPC `submit_score` / `get_best_score_ranking` と publishable key のみを使い、テストでは本番送信しない。

## 対向障害物の反射回避可能性（v12〜v13継続）

- 対向障害物は `0.80km` 以降に出現しますが、必ずプレイヤーが画面上で認識できる位置に現れてから接触判定が成立するまでの反射回避猶予を持たせます。出現数を削って安全化するのではなく、速度倍率と初期位置で安全化します。
- 最低反応猶予は `0.80〜1.50km: 0.90秒`、`1.50〜2.00km: 0.80秒`、`2.00〜5.00km: 0.70秒`、`5.00km以降: 0.62秒` とします。逃走中は `0.55秒` を基準にしますが、逃走中でも `0.50秒未満` は禁止します。
- 対向障害物の Time To Collision は、生成座標そのものではなく、左画面端で認識可能になった位置からプレイヤー接触位置までを、`updateThings()` と同じ相対速度（`(BASE_SPEED + obstacle.speed) * 42 * getSpeedMultiplierByKm(km) * chase倍率`）で割って推定します。TTCが最低反応猶予を下回る場合は、`estimateMaxSafeOncomingSpeed()` 相当で安全速度を逆算し、速度調整後のTTCで再判定します。
- `0.80〜1.50km` は歩行者中心、`1.50〜2.00km` は自転車までを基本とし、バイク・車は `2.00km` 以降に段階的に混ぜます。
- 穴直後の着地点、大穴直後、対向障害物直後の大穴、画面内の複合回避が過密な状態では対向障害物を生成しません。
- `oncoming_unavoidable` は許容しません。`oncoming_unavoidable === 0` および `unavoidableOncomingCount === 0` をリリース条件にします。

## v13 穴落ち支持判定 / 密度 hotfix

- CLIENT_VERSION は `kiriganaito-2026-07-11-v14-world-zones`。
- 穴落ちは矩形衝突ではなく、プレイヤー足元の3支持点（左寄り・中央・右寄り）が穴の水平範囲内に入ったかで判定します。
- `HOLE_FALL_GROUND_TOLERANCE = 6px` とし、地上または着地可能高度で穴上にいる場合は、無敵中でも即 `finishGame("穴に落ちました")` にします。明確に空中を飛び越えている場合のみセーフです。
- 穴には `prevX` を保存し、現在位置だけでなく前フレームから現在フレームまでの swept 範囲が足元支持点を跨いだ場合も穴落ちにします。
- 更新順序は、入力/速度、プレイヤー位置、穴・障害物・アイテム移動、穴落ち支持判定、通常着地、障害物/アイテム判定の順にし、穴上で地面に着地できないようにします。
- 小穴中心に増やすため、穴スケジュール、穴種別幅、画面内穴間隔を v13 用に再調整します。大穴頻度は上げすぎず、穴間には必ず障害物または対向障害物を維持します。
- 対向障害物速度倍率は 0.80〜1.50km を約0.50、1.50〜2.00km を約0.60、2.00km以降を段階的に0.68〜0.84へ引き上げます。ただし TTC 最低条件と `unavoidableOncomingCount === 0` は維持します。


## v14 world-zone metadata contract

- CLIENT_VERSION は `kiriganaito-2026-07-11-v14-world-zones`。
- 世界内の出現物（穴・障害物・アイテム）は、生成時に `zone`、`movementType`、`objectRole`、`heightBand`、`spawnSource` を持ちます。
- `zone` は `GROUND` / `AIR` / `HOLE` のいずれかで管理します。
- `movementType` は `WORLD_SCROLL` / `ONCOMING` で管理します。
- `objectRole` は `HAZARD` / `REWARD` / `POWERUP` / `TERRAIN` で管理します。
- `heightBand` は `GROUND` / `LOW` / `MID` / `HIGH` で管理します。
- `spawnSource` は `NORMAL` / `BETWEEN_HOLES` / `CHASE` / `INVINCIBLE` / `EARLY_ONCOMING` / `PATTERN` で管理します。
- 穴は `HOLE` / `WORLD_SCROLL` / `TERRAIN` / `GROUND` として扱います。
- 通常障害物は `GROUND` / `WORLD_SCROLL` / `HAZARD` / `GROUND` として扱います。
- 対向障害物は `GROUND` / `ONCOMING` / `HAZARD` / `GROUND` として扱い、`direction === 1` と `movementType === ONCOMING` を一致させます。
- 💰、🔩、⚙️ は `AIR` / `WORLD_SCROLL` / `REWARD` として扱い、既存の `lane` に対応して `LOW` / `MID` / `HIGH` を設定します。互換性のため `lane` は残します。
- 👯‍♀️ は地上の置物として `GROUND` / `WORLD_SCROLL` / `POWERUP` / `GROUND` として扱います。空中レーンには移動しません。
- パーティクルはこの分類対象外です。
- 今回は空中障害物を追加しません。
- 今回は穴、障害物、対向障害物、アイテムの出現頻度・配置・速度・スコア・当たり判定・画面デザインを変更しません。

## v15 SpawnDirector 出現管理契約（現行）

- 現行 CLIENT_VERSION は `kiriganaito-2026-07-11-v15-spawn-director`。
- 出現予定は `WORLD_ZONE.GROUND` / `WORLD_ZONE.AIR` / `WORLD_ZONE.HOLE` ごとの固定長キューで管理する。
- 出現予定は一意の `id`、重複抑止用 `key`、`zone`、`kind`、`spawnSource`、`dueKm`、`attempts`、`status`、`nextAttemptKm`、`payload` を持つ。
- 同じ `key` の未解決予定は重複登録しない。
- 通常試行は最大3回で、失敗後は `nextAttemptKm` まで待機する。
- 最大試行後は安全な代替またはスキップへ移り、必須予定は安全区間を予約して待機する。
- 代替時も穴・障害物・対向障害物の安全条件は緩和しない。
- 成功カウンターは `spawnSource` と生成物 metadata を正本として中央集計する方針とし、生成失敗や再試行は出現数へ加算しない。
- 今回は密度、出現確率、速度、穴幅、スコア、当たり判定、UI、ランキング、Supabase 仕様は変更対象外。

## v16 SpawnDirector 正確性契約（現行）

- 現行 CLIENT_VERSION は `kiriganaito-2026-07-12-v16-spawn-director-correctness`。
- 1 request は最大 1 entity だけを生成する。
- 低レベル生成関数（穴、障害物、通常アイテム、加点アイテム）の成功は `true`、失敗は `false` を返す。
- SpawnDirector は重複 key を確認してから payload を作成する。pending 中の同一 key では乱数、candidate、created、schedule 更新を進めない。
- request 作成時に payload と乱数結果を固定し、再試行では乱数を引き直さない。
- 1 段階の通常試行は最大 3 回で、request 全体にも固定の `totalAttempts` 上限を持つ。
- 代替は `fallbackStage` / `attemptsInStage` / `totalAttempts` で管理する。
- 成功カウンターは `recordSpawnSuccess()` だけで更新する。
- candidate カウンターは新規 enqueue 成功時だけ増やす。
- `created` / `rejected` / `skipped` を分け、`created = resolved + skipped + pending` の整合式に `rejected` は含めない。
- mandatory timeout は 1 request につき 1 回だけ記録する。
- v16 では密度定数、速度、穴幅、スコア、当たり判定、UI、ランキング、Supabase は変更しない。


## v18 P2 実効出現密度契約（現行）

- 現行 CLIENT_VERSION は `kiriganaito-2026-07-19-v19-decision-patterns`。
- 穴予定が期限へ達した時は、通常地上障害物と通常対向障害物を一時保留し、既存の穴安全距離を満たすための予約区間を作る。
- 穴生成後は `between_holes` の必須障害物を優先し、それが解決するまで通常地上予定を保留する。
- 加点アイテムが予定から0.10km以上遅れた場合は、穴予約を優先した上でアイテム安全区間を作る。
- 通常対向障害物が予定から0.10km以上遅れた場合は、通常地上障害物だけを一時保留する。
- `between_holes`、`early_oncoming`、`invincible` は通常予約より優先する。
- 穴幅、障害物速度、TTC最低条件、ジャンプ、当たり判定、点数、UI、ランキング、Supabaseは変更しない。
- P1の実効出現計測を継続し、30固定seedのP2密度ゲートで偏りを検査する。


## v19 判断パターン契約

- 現行 `CLIENT_VERSION` は `kiriganaito-2026-07-19-v19-decision-patterns`。
- 既存の `G / O / A / H / P` を2〜3ステップの短いパターンとして予約する。
- 0〜1kmは `G_S_H / H_S_G / G_A / H_A` の学習用4種類だけを使用する。
- 1km以降に `O_S_H / H_S_O / G_A_H`、2km以降かつ👯‍♀️出現可能時に `P_G_G` を解禁する。
- シャッフルバッグで単一パターン25%以下を保証し、同一パターン3連続を禁止する。
- パターン中も既存の安全距離、TTC、穴間必須障害物、最大同時危険数を維持する。
- パターンの失敗、期限超過、逃走・無敵への状態変化ではパターンを中断し、通常SpawnDirectorへ復帰する。
- 詳細契約は `P3_DECISION_PATTERN_CONTRACT.md` を正本とする。
