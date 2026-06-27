# kiriganaito SPEC

Version: `kiriganaito-2026-06-28-v7-result-dom-density`

## 固定設定
- `GAME_SLUG`、`PUBLIC_URL`、Supabase URL、Publishable key、RPC パス、RPC 引数、pending queue キー、旧キー移行処理は変更しません。
- ランキング送信は `/rest/v1/rpc/submit_score` を使い、`p_game_slug`、`p_display_name`、`p_score`、`p_client_version` のみを送ります。`p_score` は整数メートルです。
- `index.html` 1 ファイル構成、外部ライブラリなし、穴即終了、警戒度3終了、2段ジャンプなしを維持します。
- ホーム画面、結果画面、HTML meta の client version は `kiriganaito-2026-06-28-v7-result-dom-density` に統一します。

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
- 3.00km 未満では対向/接近障害物を出しません。
- 3.00km 以降は必ず候補を作り、3.00〜4.00km で最低1回は実出現するようにします。
- 3.00km 以降は 0.12〜0.22km、5.00km 以降は 0.09〜0.18km、逃走中かつ3km以降は 0.07〜0.14km ごとに候補を作ります。
- 安全距離で出せない場合は 0.03〜0.06km 後に再試行します。大穴直後や大穴直前の避け不能配置は禁止します。
- 結果画面には対向障害物候補数、対向障害物出現数を表示します。

## アイテム配置の競技性
加点アイテムは10倍級に増やしつつ、低い位置、中間位置、高い位置、穴の手前、穴の奥、障害物の後、障害物の前を混ぜます。同じ高さ・同じ間隔・同じジャンプリズムが3個以上続かないよう、`run.lastItemLane` と `run.lastItemTimingType` で直近配置を避けます。2段ジャンプ必須、取れない高さ、完全な運任せ配置は禁止します。

## 密度と逃走中
「何もない道」は、画面内または直近予定に穴・障害物・加点アイテム・無敵アイテムがない状態です。v7 では穴、障害物、加点アイテム、対向障害物のスケジュールを独立させ、同じフレームで複数種が出せるようにし、最大数も増やして空白率を従来の半分に近づけます。結果画面またはテストには最大空白時間、最大空白距離、空白率を出します。

逃走開始直後 0.7 秒は短い余白を置き、その後は 0.4〜0.8 秒ごとに小穴、静止障害物、加点アイテム、3km以降の対向障害物を追加します。👯‍♀️ の比率は増やしません。結果画面には `run.chaseObstacleSpawnCount`、`run.chaseHoleSpawnCount`、`run.chaseScoreItemSpawnCount`、`run.chaseOncomingSpawnCount` を表示します。

## 速度上昇
1kmごとに `getRunSpeedMultiplier(km) = Math.min(1.35, 1 + Math.floor(km) * 0.035)` で速度を少しずつ上げます。実走行距離加算、道路スクロール、穴、障害物、アイテム、対向障害物、逃走中倍率との組み合わせに使います。ジャンプ力と重力は変更しません。結果画面には最大速度倍率を表示します。

## テスト方針
- `node tests/progressive-autoplay.js`
- `node tests/release-comprehensive.js`
- 可能なら `node tests/endurance-150km.js`
- client version、旧文字列なし、`.children = []` なし、結果内訳、診断値、ペナルティ上限、p_score 一致、無敵実時間4秒、無敵中障害物、対向障害物、配置リズム、逃走中密度、空白率、速度倍率、Supabase本番送信なし、console error/warning なしを確認します。

## v7 result DOM / density hotfix
- CLIENT_VERSION は `kiriganaito-2026-06-28-v7-result-dom-density`。
- 結果画面の `resultComment` は DOM キャッシュ `el` に登録し、`finishGame()` は `buildResultSnapshot()`、`renderResultHeader()`、`renderResultBreakdown()`、`renderResultVersion()` の段階描画に分割する。
- 結果内訳はランキング欄より上に、記録の内訳、プレイ内容、出現数、診断、ランキング送信 payload の `p_score`、`zeroReason`、version を表示する。
- 穴生成失敗時は通常間隔を再加算せず `retryHoleSoon(km)` により 0.006〜0.014km で短距離リトライする。小穴中心に増やし、穴同士の接触と2段ジャンプ必須配置は禁止する。
- 3km以降の対向障害物は `retryOncomingSoon(km)` で 0.02〜0.04km 後に再試行し、候補だけ増えて出現しない状態を避ける。対向障害物候補数、出現数、失敗再試行数を結果に表示する。
- Supabase は既存 RPC `submit_score` / `get_best_score_ranking` と publishable key のみを使い、テストでは本番送信しない。
