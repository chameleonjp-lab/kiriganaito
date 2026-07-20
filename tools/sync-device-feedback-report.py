from pathlib import Path

path = Path('TEST_REPORT.md')
text = path.read_text()
old = '''# kiriganaito TEST_REPORT

- 現行 CLIENT_VERSION: `kiriganaito-2026-07-20-v22-device-feedback-ui`
- 現行段階: `P4 空中障害物の試作と跳ぶ・跳ばない判断`
- 基準main: `0b16b4850fb511c5600bb8c3bfe1254b6e1d37b9`
- 作業ブランチ: `ai/kiriganaito-v20-air-obstacle`
- Draft Pull Request: `#39`
- 検証済み実装コミット: `871ecd25b3c6fc804cf6b10e80b3bb11ecb3de91`
- 状態: 自動ゲート合格、実機未確認、main反映済み
'''
new = '''# kiriganaito TEST_REPORT

- 現行 CLIENT_VERSION: `kiriganaito-2026-07-20-v22-device-feedback-ui`
- 現行段階: `P5実機フィードバックUI修正`
- 基準main: `343f576d375bdf526221f36556d61308e695af4d`
- 作業ブランチ: `ai/kiriganaito-v22-device-feedback-ui`
- Draft Pull Request: `#42`
- 検証済み実装コミット: `ffa0f11cd4f8d26121889a7ff81ae064257a0635`
- 状態: 自動ゲート合格、実機再確認待ち、Draft・未マージ
'''
if text.count(old) != 1:
    raise SystemExit(f'current report header mismatch: {text.count(old)}')
text = text.replace(old, new, 1)
section = '''

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
'''
if '## v22 実機フィードバック最終検証' not in text:
    text += section
path.write_text(text)
print('TEST_REPORT.md synchronized to v22 device feedback state')
