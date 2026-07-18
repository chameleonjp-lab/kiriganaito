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
    '''        EARLY_DELAY_MIN_KM: 0.35,
        EARLY_DELAY_MAX_KM: 0.45,
        NORMAL_DELAY_MIN_KM: 0.65,
        NORMAL_DELAY_MAX_KM: 0.85,''',
    '''        EARLY_DELAY_MIN_KM: 0.45,
        EARLY_DELAY_MAX_KM: 0.55,
        NORMAL_DELAY_MIN_KM: 0.85,
        NORMAL_DELAY_MAX_KM: 1.05,''',
    "reduce natural pattern cadence",
)

index = replace_once(
    index,
    '''        const compatible = availableDecisionPatterns(km).filter((def) => def.steps[0] && def.steps[0].symbol === symbol);''',
    '''        const compatible = availableDecisionPatterns(km).filter((def) => def.steps[0] && def.steps[0].symbol === symbol && def.name !== "H_S_O");''',
    "exclude H-S-O from natural adoption",
)
index_path.write_text(index)
print("P3 natural cadence reduced and H_S_O kept as targeted-only pattern")
