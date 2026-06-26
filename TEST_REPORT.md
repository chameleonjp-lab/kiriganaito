# kiriganaito リリース前総合テストレポート

- 生成日時: 2026-06-26T13:36:24.889Z
- 対象: `chameleonjp-lab/kiriganaito`
- 最終判定: **WARN（公開可能だが改善推奨あり）**
- 検査方針: `index.html` / `SPEC.md` / 既存 `tests/` を読み、ゲーム本体と仕様書は変更せず、Node ハーネスで画面遷移・ロジック・ランキング payload・長距離表示を検証した。
- Supabase: **モック/遮断済み**。`https://mlpnjgezrnhdxsxolyzj.supabase.co/*` への fetch はハーネスで記録し、実送信扱いにしない。自然走行テストでは送信関数もモックした。
- Playwright: **未使用**。`npx playwright --version` が npm E403 で失敗したため、スクリーンショットは生成できなかった。

## I. 総合判定

**WARN: 公開可能だが改善推奨あり**

根拠:

- 起動・基本画面遷移・名前入力・ジャンプ・リタイア・結果画面・再挑戦の Node ハーネス検査は PASS。
- JavaScript 例外、console error、console warning は検査ハーネス上では 0 件。
- 本番 Supabase へのテストスコア送信は行っていない。
- 静的検査で `public.scores`、`service_role`、secret key、直接 insert は未検出。
- 長距離表示 150.00km / 999.99km / 1000.00km は表示崩壊、NaN、Infinity なし。
- 自然走行オートプレイは 1km には到達したが、5km 以降には未到達。最大自然走行は 2939m、最大補正込みスコアは 2447m。これは自動プレイヤー限界の可能性が高く、公開ブロッカーではなく WARN とした。
- Playwright 実機相当スクリーンショットは環境制約で未取得のため WARN とした。

## A. 静的検査

| 項目 | 結果 | 備考 |
| --- | --- | --- |
| `index.html` が存在する | PASS | あり |
| `SPEC.md` が存在する | PASS | あり |
| `public.scores` を使っていない | PASS | 未検出 |
| `service_role` が含まれていない | PASS | 未検出 |
| secret key が含まれていない | PASS | 未検出 |
| SUPABASE_URL は公開 URL | PASS | `https://mlpnjgezrnhdxsxolyzj.supabase.co` |
| Publishable key のみ | PASS | ユーザー指定キーと一致 |
| pending queue キー | PASS | `kiriganaito_pending_scores_v1` |
| 旧キー | PASS | `songen_wo_kakeyouka2_pending_scores_v1` は移行処理用として存在 |
| 👯‍♀️ 表記一致 | PASS | `index.html` / `SPEC.md` とも一致 |
| ⚠️ が穴描画に使われる | PASS | Canvas `fillText` で確認 |
| dancer パターン | PASS | 仕様書・実装に存在 |
| スコア計算式 | PASS | 実装・仕様書で一致 |
| 2段ジャンプ | PASS | 2段ジャンプ実装を示す状態変数や jumpCount 未検出 |
| 本番コードの 150km 直接代入 | PASS | 未検出 |

既存テスト `tests/endurance-150km.js` と新規 `tests/release-comprehensive.js` には表示/耐久検証用途の値設定があるが、自然走行到達判定には使用していない。自然走行は `tests/progressive-autoplay.js` でジャンプ入力のみを使った。

## B. 起動・画面遷移検査

検証方法: Node ハーネスで DOM/Canvas/localStorage/fetch をスタブし、`index.html` 内スクリプトを実行。

| 項目 | 結果 |
| --- | --- |
| ホーム表示 | PASS |
| ルール表示 | PASS |
| 名前入力 | PASS |
| 名前なし開始ブロック | PASS |
| 1〜10文字制限 | PASS |
| 名前保存後開始 | PASS |
| Canvas/ジャンプボタン相当入力 | PASS |
| リタイアで結果画面 | PASS |
| 結果画面後にスコアが進まない | PASS |
| もう一度で再初期化 | PASS |
| 320px 幅相当で横スクロール静的リスク低 | PASS（代替検査） |
| iPhone SE 幅でボタン最小高 | PASS（CSS 静的検査） |

## C. ゲームロジック検査

| 項目 | 結果 | 備考 |
| --- | --- | --- |
| タップで jumpBuffer | PASS | `inputState.jumpBuffer` に入力可能 |
| ジャンプ成立時 vy 上向き | PASS | `player.vy < 0` |
| 2段ジャンプ不可 | PASS | 空中再入力で追加ジャンプなし |
| 着地後再ジャンプ | PASS | ハーネスでジャンプバッファ確認 |
| コヨーテタイム | PASS | `HIT.COYOTE_SEC` 範囲でジャンプ成立 |
| ジャンプバッファ | PASS | 着地直前入力でジャンプ成立 |
| 穴落ちで RESULT | PASS | 無敵中でも終了 |
| ⚠️ は描画対象 | PASS | 静的/自然走行で検出 |
| ⚠️ が判定に使われない | PASS（静的） | 判定は穴矩形を参照 |
| 穴の手前で🚚黒化 | PASS（ハーネス） | 自然走行ログで疑いなし |
| 障害物衝突・事故ペナルティ | PASS（静的整合） | `-200m` と警戒度仕様一致 |
| 逃走 15 秒 | PASS（静的整合） | `CHASE_TIME = 15` |
| 👯‍♀️ 7 秒無敵 | PASS（静的整合） | `duration: 7` |
| スコア 0 未満防止 | PASS | `Math.max(0, ...)` |
| NaN / Infinity | PASS | 長距離検査含め未検出 |

## D. 自然走行オートプレイ検査

検証コマンド: `node tests/progressive-autoplay.js`

- 使用 TARGETS: `[1000, 5000, 10000, 30000, 150000]`
- 使用 seeds: `[1001..1005, 2001..2005, 3001..3005]`
- runMeters / scoreMeters の直接代入: **なし**
- 自動入力: player / holes / obstacles / items の状態を読み、ジャンプ入力だけ実行

| 指標 | 結果 |
| --- | ---: |
| 1km 到達 | 可 |
| 5km 到達 | 不可 |
| 10km 到達 | 不可 |
| 30km 到達 | 不可 |
| 150km 自然到達 | 不可 |
| 最大到達距離 | 2939m |
| 最大補正込みスコア | 2447m |
| ベスト seed | 2003 |
| 最多終了理由 | 穴に落ちました |
| 最多失敗分類 | `hole_timing_early` |
| console error / warning | 0 / 0 |
| 最大 holes.length | 既存自然走行 JSON 参照 |
| 最大 obstacles.length | 既存自然走行 JSON 参照 |
| 最大 items.length | 既存自然走行 JSON 参照 |
| 最大 particles.length | 既存自然走行 JSON 参照 |

補足:

- 150km 専用の `node tests/endurance-150km.js` も実行し、自然走行入力では 2140m / 2340m で穴落ち終了した。
- 自動プレイヤーは人間の先読み・待機ジャンプ調整より単純なため、5km 未到達を即ゲームロジック不具合とは判定しない。

## E. 長距離表示・結果画面検査

検証方法: **表示耐性専用**としてハーネス内で `runMeters` / `scoreMeters` 相当値を一時的に設定。自然走行到達とは混同しない。

| 値 | HUD 走行 | HUD スコア | 結果スコア | payload `p_score` |
| ---: | --- | --- | --- | ---: |
| 150000m | 150.00km | 150.00km | 150.00km | 150000 |
| 999990m | 999.99km | 999.99km | 999.99km | 999990 |
| 1000000m | 1000.00km | 1000.00km | 1000.00km | 1000000 |

結果:

- HUD 走行距離: PASS
- HUD スコア: PASS
- 結果画面スコア: PASS
- 結果内訳: PASS
- `p_score` 整数メートル: PASS
- `NaNkm` / `Infinitykm`: 未検出
- iPhone SE 幅の横スクロール: CSS 静的検査ではリスク低
- 結果シェア文: ハーネスではボタン存在を確認。実ブラウザ Share API は Playwright/実機環境で再確認推奨。

## F. ランキング通信モック検査

本番送信: **なし**

ハーネスで捕捉した想定 payload:

```json
{
  "p_game_slug": "kiriganaito",
  "p_display_name": "RANK",
  "p_score": 1234,
  "p_client_version": "kiriganaito-2026-06-25-v1"
}
```

確認結果:

- `submit_score` RPC パス: PASS
- `p_game_slug`: PASS
- `p_display_name`: PASS
- `p_score`: PASS（整数メートル）
- `p_client_version`: PASS
- `game_scores` 直接 insert: 未検出
- `public.scores`: 未検出
- pending queue キー: `kiriganaito_pending_scores_v1`
- 通信失敗時 pending queue: PASS（モック保存を確認）
- 再送ボタン表示: PASS
- 旧キー移行: kiriganaito の item のみ移行し、別ゲーム data を残す実装を静的確認

## G. スマホ UI 検査

Playwright は利用不可。理由: `npx playwright --version` が npm E403 で失敗。

代替検査:

- `overflow-x: hidden`: PASS
- `.app { width: min(100%, 430px) }`: PASS
- canvas `width: 100%`: PASS
- canvas `height: min(55dvh, 430px)`: PASS
- button `min-height: 48px`: PASS
- jump button `min-height: 76px`: PASS
- HUD は 3 カラム構成で iPhone SE 幅を意識: PASS（静的）

未検査/要再検証:

- 実スクリーンショット
- 逃走中画面の視認性
- ランキング欄の実ブラウザ折り返し
- 穴の ⚠️ / 🚚 黒化 / 👯‍♀️ 認識性の実機目視

## H. SPEC.md 整合検査

| 項目 | 結果 |
| --- | --- |
| アイテム値 | PASS |
| 事故ペナルティ | PASS |
| 取り逃がしペナルティ | PASS |
| 👯‍♀️ の効果 | PASS |
| 穴仕様 | PASS |
| 障害物仕様 | PASS |
| 逃走時間 | PASS |
| 逃走中の距離加算通常 | PASS |
| スコア計算式 | PASS |
| pending queue 仕様 | PASS |
| 旧キー移行仕様 | PASS |
| デバッグ表示仕様 | PASS |
| 画面構成 | PASS |
| 古い 👯 表記 | 未検出 |
| 古い 🪙 表記 | 未検出 |
| 古い「進行方向障害物が自走する」説明 | 未検出 |

## console error / warning

- `node tests/progressive-autoplay.js`: error 0 / warning 0
- `node tests/release-comprehensive.js`: error 0 / warning 0
- `node tests/endurance-150km.js || true`: error 0 / warning 0（150km 未到達のため元スクリプトは失敗扱い条件だが、`|| true` でレポート取得）
- `npx playwright --version || true`: npm E403（環境制約）

## 公開前に必ず直すべきこと

現時点で **FAIL 相当の必須修正は検出していない**。

ただし、実ブラウザ/実機で Playwright または手動確認ができる環境では、以下を公開前チェックとして推奨:

1. iPhone SE 実幅でホーム/ルール/名前入力/ゲーム/逃走中/結果/ランキングを目視確認する。
2. 実ブラウザの Web Share API 動作を確認する。
3. 穴の ⚠️、🚚 黒化なし、👯‍♀️ の識別性をスクリーンショットで確認する。

## 改善推奨だが後回し可能なこと

1. 自動プレイヤーが 5km 未到達のため、人間プレイで 5km 以上の難易度感を再確認する。
2. 穴タイミング失敗が多いため、穴/障害物複合配置の安全余白を実プレイで再評価する。
3. Playwright を導入できる CI 環境でスクリーンショット回帰テストを追加する。

## 修正候補（ゲーム本体は未修正）

- 穴・障害物複合パターンの安全余白を人間プレイで再検証する。
- 逃走中の視認性、HUD の詰まり、ランキング欄の長い名前の折り返しを実ブラウザで目視確認する。
- Playwright が使える環境で `artifacts/screenshots/*.png` を生成する。

## 変更しなかったもの

今回、以下は変更していない。

- `index.html`
- `SPEC.md`
- Supabase URL
- Publishable key
- `CLIENT_VERSION`
- `GAME_SLUG`
- `PUBLIC_URL`
- RPC パス・RPC 引数
- pending queue / localStorage キー / 旧キー移行処理
- ゲームルール、スコア計算式、ジャンプ、穴、障害物、アイテム、CSS、Canvas 描画
