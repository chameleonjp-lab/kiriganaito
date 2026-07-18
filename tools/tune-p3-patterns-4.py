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
    '''          { symbol: "G", offsetKm: 0.10, satisfiesBetweenHole: true, payload: { dir: -1, emoji: "🚶", x: -44 } },''',
    '''          { symbol: "G", offsetKm: 0.085, satisfiesBetweenHole: true, payload: { dir: -1, emoji: "🚶", x: -44 } },''',
    "align H-S-G with mandatory obstacle gap",
)
index = replace_once(
    index,
    '''          { symbol: "O", offsetKm: 0.16, satisfiesBetweenHole: true, payload: { dir: 1, emoji: "🚶" } },''',
    '''          { symbol: "O", offsetKm: 0.145, satisfiesBetweenHole: true, payload: { dir: 1, emoji: "🚶" } },''',
    "align H-S-O with oncoming safe gap",
)
index = replace_once(
    index,
    '''          { symbol: "H", offsetKm: 0.13, payload: { kind: "SMALL", w: 30 } },''',
    '''          { symbol: "H", offsetKm: 0.09, payload: { kind: "SMALL", w: 30 } },''',
    "align G-A-H with next hole cycle",
)

index = replace_once(
    index,
    '''        if (!entity || !request || request.spawnSource !== SPAWN_SOURCE.NORMAL) return false;''',
    '''        if (!entity || !request || (request.spawnSource !== SPAWN_SOURCE.NORMAL && request.spawnSource !== SPAWN_SOURCE.BETWEEN_HOLES)) return false;''',
    "allow between-hole entity adoption",
)
index = replace_once(
    index,
    '''        const symbol = decisionPatternSymbolForEntity(entity);
        if (!["G", "O", "H", "P"].includes(symbol)) return false;''',
    '''        const symbol = decisionPatternSymbolForEntity(entity);
        if (!["G", "O", "H", "P"].includes(symbol)) return false;
        if (request.spawnSource === SPAWN_SOURCE.BETWEEN_HOLES && !["G", "O"].includes(symbol)) return false;''',
    "limit between-hole adoption symbols",
)

index = replace_once(
    index,
    '''        if (isDecisionPatternReservationActive() && req && (req.spawnSource === SPAWN_SOURCE.NORMAL || req.spawnSource === SPAWN_SOURCE.CHASE)) return true;''',
    '''        if (isDecisionPatternReservationActive() && req && (req.spawnSource === SPAWN_SOURCE.NORMAL || req.spawnSource === SPAWN_SOURCE.CHASE) && req.kind !== SPAWN_REQUEST_KIND.SCORE_ITEM) return true;''',
    "allow safe reward requests during pattern",
)
index = replace_once(
    index,
    '''        if (dueScoreItem && !reservePattern) {''',
    '''        if (dueScoreItem) {''',
    "keep normal reward cadence during pattern",
)
index_path.write_text(index)
print("P3 pattern adoption diversified and safe rewards preserved")
