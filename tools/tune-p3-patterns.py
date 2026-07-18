from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


index_path = Path("index.html")
index = index_path.read_text()

old_maybe_start = '''        if (km < spawn.nextPatternAt || run.chase > 0 || isDancerInvincible()) return;
        if (spawn.needObstacleBeforeNextHole || pendingSpawnRequestCount() > 0) return;
        if (isHoleReservationActive(km) || isScoreItemReservationActive(km) || isOncomingCriticallyOverdue(km)) return;
        const def = selectNextDecisionPattern(km, true);
        if (def) startDecisionPattern(def, km);'''
new_maybe_start = '''        if (km < spawn.nextPatternAt || run.chase > 0 || isDancerInvincible()) return;
        if (spawn.needObstacleBeforeNextHole) return;
        if (km >= 0.8 && km < 2 && !run.earlyOncomingSpawned) return;
        const mandatorySources = [SPAWN_SOURCE.BETWEEN_HOLES, SPAWN_SOURCE.EARLY_ONCOMING, SPAWN_SOURCE.INVINCIBLE];
        const zones = [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE];
        const mandatoryPending = zones.some((zone) => spawnRequestQueue(zone).some((req) => mandatorySources.includes(req.spawnSource) && req.status !== SPAWN_REQUEST_STATUS.RESOLVED && req.status !== SPAWN_REQUEST_STATUS.SKIPPED));
        if (mandatoryPending) return;
        const def = selectNextDecisionPattern(km, false);
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
index = replace_once(index, old_maybe_start, new_maybe_start, "relax pattern start gate")

old_defer = '''      function shouldDeferSpawnRequest(req, km) {
        if (req && req.spawnSource === SPAWN_SOURCE.PATTERN) return false;
        if (req && req.kind === SPAWN_REQUEST_KIND.HOLE && isOncomingCriticallyOverdue(km)) return true;'''
new_defer = '''      function shouldDeferSpawnRequest(req, km) {
        if (req && req.spawnSource === SPAWN_SOURCE.PATTERN) return false;
        if (isDecisionPatternReservationActive() && req && (req.spawnSource === SPAWN_SOURCE.NORMAL || req.spawnSource === SPAWN_SOURCE.CHASE)) return true;
        if (req && req.kind === SPAWN_REQUEST_KIND.HOLE && isOncomingCriticallyOverdue(km)) return true;'''
index = replace_once(index, old_defer, new_defer, "defer normal requests during pattern")
index_path.write_text(index)


test_path = Path("tests/p3-pattern-regression.js")
test = test_path.read_text()
old_capture = '''  const maxSelectionShare = Math.max(...Object.values(selectionCounts)) / selections.length;

  startGame();'''
new_capture = '''  const maxSelectionShare = Math.max(...Object.values(selectionCounts)) / selections.length;
  const selectionMaxConsecutive = run.patternMaxConsecutiveSame;

  startGame();'''
test = replace_once(test, old_capture, new_capture, "capture selector consecutive count")

old_runtime_setup = '''  run.nextDancerAt = 99;
  spawn.nextHoleAt = 99;'''
new_runtime_setup = '''  run.nextDancerAt = 99;
  run.earlyOncomingSpawned = true;
  spawn.nextHoleAt = 99;'''
test = replace_once(test, old_runtime_setup, new_runtime_setup, "disable early oncoming interference")

test = replace_once(
    test,
    '''    selectionMaxConsecutive: run.patternMaxConsecutiveSame,''',
    '''    selectionMaxConsecutive,''',
    "report captured consecutive count",
)

test_path.write_text(test)
print("P3 pattern start and runtime interference fixes applied")
