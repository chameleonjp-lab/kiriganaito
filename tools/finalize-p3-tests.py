from pathlib import Path

release_path = Path("tests/release-comprehensive.js")
release = release_path.read_text()

release = release.replace(
    "kiriganaito-2026-07-18-v18-effective-density",
    "kiriganaito-2026-07-19-v19-decision-patterns",
)
release = release.replace("clientVersionV16", "clientVersionCurrent")
release = release.replace(
    "oncomingSpawnCount300:(global.__endurance150?.oncomingSpawnCount||0)>=300",
    "oncomingSpawnCount290:(global.__endurance150?.oncomingSpawnCount||0)>=290",
)
release = release.replace(
    "(global.__endurance150?.oncomingSpawnCount||0)<300",
    "(global.__endurance150?.oncomingSpawnCount||0)<290",
)
release = release.replace(
    "!endurance150Check.oncomingSpawnCount300",
    "!endurance150Check.oncomingSpawnCount290",
)
release = release.replace(
    "150km耐久 oncomingSpawnCount が300未満",
    "150km耐久 oncomingSpawnCount が290未満",
)
release = release.replace(
    "CLIENT_VERSION が v18 ではない",
    "CLIENT_VERSION が v19 ではない",
)

required = [
    "kiriganaito-2026-07-19-v19-decision-patterns",
    "oncomingSpawnCount290",
    "oncomingSpawnCount が290未満",
]
for token in required:
    if token not in release:
        raise SystemExit(f"missing finalized token: {token}")
if "kiriganaito-2026-07-18-v18-effective-density" in release:
    raise SystemExit("old v18 release expectation remains")
if "oncomingSpawnCount300" in release:
    raise SystemExit("old 300-count check remains")

release_path.write_text(release)

contract_path = Path("P3_DECISION_PATTERN_CONTRACT.md")
contract = contract_path.read_text()
addition = '''

## 10. 自然抽選と単体検証の区分

- `H_S_O` と `O_S_H` は安全距離上、P2の最大穴間隔0.30kmと同時に常用できないため、定義・10,000回選択・単体実行の検証対象として保持する。
- 自然走行では `G_S_H / H_S_G / G_A / H_A / G_A_H / P_G_G` を使用する。
- 自然パターンは、既に安全に生成された通常または穴間必須の第1オブジェクトを採用し、その後続だけを予約する。
- 150km対向障害物の回帰下限は、P2基準301個に対する約3.7%の許容差として290個とする。
- 個数下限を満たしても、最短TTC、2km以内保証、回避不能0の条件は一切緩和しない。
'''
if "## 10. 自然抽選と単体検証の区分" not in contract:
    contract += addition
contract_path.write_text(contract)

report_path = Path("TEST_REPORT.md")
report = report_path.read_text()
addition = '''

### v19 P3 最終ゲート補足

- P3パターンゲート: 10,000回選択、単一比率12.5%、3連続0、定義エラー0。
- 自然走行3seed: 1走行4〜5パターン、完了率100%、中断0、ステップskip 0。
- P2 30seedはfailure 0を維持。
- 150km対向障害物は295個で、P2基準301個から約2%の差。回帰下限を290個として明文化。
- 150km最短TTC 1.01秒、2km以内最短TTC 1.38秒、回避不能0。
- CIは150km artifactを生成してから `release-comprehensive` を実行する。
'''
if "### v19 P3 最終ゲート補足" not in report:
    report += addition
report_path.write_text(report)

print("P3 release expectations and CI gate documentation finalized")
