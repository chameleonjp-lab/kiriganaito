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
    '''        EARLY_DELAY_MIN_KM: 0.20,
        EARLY_DELAY_MAX_KM: 0.30,
        NORMAL_DELAY_MIN_KM: 0.36,
        NORMAL_DELAY_MAX_KM: 0.56,''',
    '''        EARLY_DELAY_MIN_KM: 0.35,
        EARLY_DELAY_MAX_KM: 0.45,
        NORMAL_DELAY_MIN_KM: 0.65,
        NORMAL_DELAY_MAX_KM: 0.85,''',
    "reduce pattern frequency",
)

old_helpers = '''      function nextDecisionPatternDelay(km) {
        return km < 1 ? rand(P3_PATTERN.EARLY_DELAY_MIN_KM, P3_PATTERN.EARLY_DELAY_MAX_KM) : rand(P3_PATTERN.NORMAL_DELAY_MIN_KM, P3_PATTERN.NORMAL_DELAY_MAX_KM);
      }
      function startDecisionPattern(def, km) {'''
new_helpers = '''      function nextDecisionPatternDelay(km) {
        return km < 1 ? rand(P3_PATTERN.EARLY_DELAY_MIN_KM, P3_PATTERN.EARLY_DELAY_MAX_KM) : rand(P3_PATTERN.NORMAL_DELAY_MIN_KM, P3_PATTERN.NORMAL_DELAY_MAX_KM);
      }
      function decisionPatternStartCompatibility(def, km) {
        if (!def || !def.steps || !def.steps.length) return false;
        const first = def.steps[0];
        let firstSafe = true;
        if (first.symbol === "G") firstSafe = canSpawnObstacle(km, -1);
        else if (first.symbol === "O") firstSafe = km >= 0.8 && canSpawnObstacle(km, 1);
        else if (first.symbol === "H") {
          const kind = first.payload && first.payload.kind || "SMALL";
          const width = first.payload && first.payload.w || HOLE_TYPES[kind].max;
          const x = first.payload && first.payload.x != null ? first.payload.x : -width - 16;
          firstSafe = canSpawnHole(km, kind, x, width);
        }
        if (!firstSafe) return false;
        const holeStep = def.steps.find((step) => step.symbol === "H");
        if (holeStep) {
          const expectedLead = holeStep.offsetKm;
          const actualLead = spawn.nextHoleAt - km;
          const tolerance = expectedLead === 0 ? 0.018 : 0.022;
          return actualLead >= expectedLead - tolerance && actualLead <= expectedLead + tolerance;
        }
        const span = def.steps.reduce((max, step) => Math.max(max, step.offsetKm), 0);
        const requiredHoleBuffer = span + SPAWN.HOLE_AFTER_OBSTACLE + 0.018;
        return spawn.nextHoleAt - km >= requiredHoleBuffer;
      }
      function selectStartableDecisionPattern(km) {
        const compatible = availableDecisionPatterns(km).filter((def) => decisionPatternStartCompatibility(def, km));
        if (!compatible.length) return null;
        const key = "start:" + compatible.map((def) => def.name).join("|");
        if (spawn.patternBagKey !== key || !Array.isArray(spawn.patternBag) || !spawn.patternBag.length) {
          spawn.patternBagKey = key;
          spawn.patternBag = shuffleDecisionPatternNames(compatible.map((def) => def.name));
        }
        const history = Array.isArray(run.patternHistory) ? run.patternHistory : [];
        const last = history.length ? history[history.length - 1] : "";
        const secondLast = history.length > 1 ? history[history.length - 2] : "";
        let pickIndex = spawn.patternBag.length - 1;
        if (last && last === secondLast && spawn.patternBag[pickIndex] === last) {
          const alternate = spawn.patternBag.findIndex((name) => name !== last);
          if (alternate >= 0) pickIndex = alternate;
        }
        const name = spawn.patternBag.splice(pickIndex, 1)[0];
        const def = decisionPatternByName(name);
        if (def) rememberDecisionPatternChoice(name);
        return def;
      }
      function startDecisionPattern(def, km) {'''
index = replace_once(index, old_helpers, new_helpers, "add schedule-aligned pattern selection")

old_start_selection = '''        const def = selectNextDecisionPattern(km, false);
        if (!def) return;
        const first = def.steps[0];
        let startable = true;
        if (first.symbol === "G") startable = canSpawnObstacle(km, -1);
        else if (first.symbol === "O") startable = km >= 0.8 && canSpawnObstacle(km, 1);
        else if (first.symbol === "H") {
          const kind = first.payload && first.payload.kind || "SMALL";
          const width = first.payload && first.payload.w || HOLE_TYPES[kind].max;
          const x = first.payload && first.payload.x != null ? first.payload.x : -width - 16;
          startable = canSpawnHole(km, kind, x, width);
        }
        if (!startable) {
          spawn.patternBag.unshift(def.name);
          spawn.nextPatternAt = km + 0.025;
          return;
        }
        rememberDecisionPatternChoice(def.name);
        startDecisionPattern(def, km);'''
new_start_selection = '''        const def = selectStartableDecisionPattern(km);
        if (!def) return;
        startDecisionPattern(def, km);'''
index = replace_once(index, old_start_selection, new_start_selection, "use aligned pattern selector")
index_path.write_text(index)

release_path = Path("tests/release-comprehensive.js")
release = release_path.read_text()
release = release.replace(
    "clientVersionV16:has('kiriganaito-2026-07-12-v16-spawn-director-correctness')",
    "clientVersionV16:has('kiriganaito-2026-07-19-v19-decision-patterns')",
)
release_path.write_text(release)
print("P3 patterns aligned with P2 hole schedule")
