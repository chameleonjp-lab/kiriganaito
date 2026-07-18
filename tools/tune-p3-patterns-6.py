from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


index_path = Path("index.html")
index = index_path.read_text()
index = replace_once(
    index,
    '''        const compatible = availableDecisionPatterns(km).filter((def) => def.steps[0] && def.steps[0].symbol === symbol && def.name !== "H_S_O");''',
    '''        const compatible = availableDecisionPatterns(km).filter((def) => def.steps[0] && def.steps[0].symbol === symbol && def.name !== "H_S_O" && def.name !== "O_S_H");''',
    "exclude O-S-H from natural adoption",
)
index_path.write_text(index)
print("O_S_H remains defined and tested but is excluded from natural P2 scheduling")
