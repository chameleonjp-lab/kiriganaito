from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


index_path = Path("index.html")
index = index_path.read_text()

adoption_block = r'''      function decisionPatternSymbolForEntity(entity) {
        if (!entity) return "";
        if (entity.zone === WORLD_ZONE.HOLE) return "H";
        if (entity.objectRole === OBJECT_ROLE.POWERUP) return "P";
        if (entity.objectRole === OBJECT_ROLE.REWARD) return "A";
        if (entity.objectRole === OBJECT_ROLE.HAZARD && entity.movementType === MOVEMENT_TYPE.ONCOMING) return "O";
        if (entity.objectRole === OBJECT_ROLE.HAZARD) return "G";
        return "";
      }
      function selectDecisionPatternForFirstSymbol(symbol, km) {
        const compatible = availableDecisionPatterns(km).filter((def) => def.steps[0] && def.steps[0].symbol === symbol);
        if (!compatible.length) return null;
        const history = Array.isArray(run.patternHistory) ? run.patternHistory : [];
        const last = history.length ? history[history.length - 1] : "";
        const secondLast = history.length > 1 ? history[history.length - 2] : "";
        const allowed = compatible.filter((def) => !(last && last === secondLast && def.name === last));
        if (!allowed.length) return null;
        const key = "adopt:" + symbol + ":" + allowed.map((def) => def.name).join("|");
        if (spawn.patternBagKey !== key || !Array.isArray(spawn.patternBag) || !spawn.patternBag.length) {
          spawn.patternBagKey = key;
          spawn.patternBag = shuffleDecisionPatternNames(allowed.map((def) => def.name));
        }
        const name = spawn.patternBag.pop();
        const def = decisionPatternByName(name);
        if (def) rememberDecisionPatternChoice(name);
        return def;
      }
      function maybeAdoptDecisionPatternFromEntity(entity, request, km) {
        if (!entity || !request || request.spawnSource !== SPAWN_SOURCE.NORMAL) return false;
        if (spawn.activePattern || run.chase > 0 || isDancerInvincible()) return false;
        if (km < spawn.nextPatternAt) return false;
        if (km >= 0.8 && km < 2 && !run.earlyOncomingSpawned) return false;
        const symbol = decisionPatternSymbolForEntity(entity);
        if (!["G", "O", "H", "P"].includes(symbol)) return false;
        if (symbol === "P" && spawn.nextHoleAt - km < 0.24) return false;
        const def = selectDecisionPatternForFirstSymbol(symbol, km);
        if (!def || !startDecisionPattern(def, km)) return false;
        const active = spawn.activePattern;
        const first = active && active.steps[0];
        if (!first || first.symbol !== symbol) {
          abortDecisionPattern("adoption_symbol_mismatch", km);
          cleanupOrphanedPatternRequests();
          return false;
        }
        first.status = "resolved";
        entity.patternId = active.id;
        entity.patternName = active.name;
        entity.patternStepIndex = first.index;
        entity.patternSymbol = first.symbol;
        run.patternStepResolvedCount = safeInt(run.patternStepResolvedCount) + 1;
        if (active.steps.every((step) => step.status === "resolved")) finishDecisionPattern(km);
        return true;
      }
'''
index = replace_once(
    index,
    '''      function startDecisionPattern(def, km) {''',
    adoption_block + '''      function startDecisionPattern(def, km) {''',
    "insert entity adoption scheduler",
)

old_idle_start = '''        if (km < spawn.nextPatternAt || run.chase > 0 || isDancerInvincible()) return;
        if (spawn.needObstacleBeforeNextHole) return;
        if (km >= 0.8 && km < 2 && !run.earlyOncomingSpawned) return;
        const mandatorySources = [SPAWN_SOURCE.BETWEEN_HOLES, SPAWN_SOURCE.EARLY_ONCOMING, SPAWN_SOURCE.INVINCIBLE];
        const zones = [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE];
        const mandatoryPending = zones.some((zone) => spawnRequestQueue(zone).some((req) => mandatorySources.includes(req.spawnSource) && req.status !== SPAWN_REQUEST_STATUS.RESOLVED && req.status !== SPAWN_REQUEST_STATUS.SKIPPED));
        if (mandatoryPending) return;
        const def = selectStartableDecisionPattern(km);
        if (!def) return;
        startDecisionPattern(def, km);'''
new_idle_start = '''        // New patterns begin by adopting an already-safe NORMAL entity in recordSpawnSuccess().
        // This avoids creating a new gap or replacing P2's scheduled first hazard.'''
index = replace_once(index, old_idle_start, new_idle_start, "disable independent pattern launch")

old_record_end = '''        if (entity.objectRole === OBJECT_ROLE.REWARD) { run.scoreItemSpawnCount++; run.itemSpawnCount++; spawn.lastScoreItemAt = km; if (source === SPAWN_SOURCE.CHASE) run.chaseScoreItemSpawnCount++; }
        if (entity.objectRole === OBJECT_ROLE.POWERUP) { run.invincibleItemSpawnCount++; run.dancerSpawnCount++; run.itemSpawnCount++; }
      }'''
new_record_end = '''        if (entity.objectRole === OBJECT_ROLE.REWARD) { run.scoreItemSpawnCount++; run.itemSpawnCount++; spawn.lastScoreItemAt = km; if (source === SPAWN_SOURCE.CHASE) run.chaseScoreItemSpawnCount++; }
        if (entity.objectRole === OBJECT_ROLE.POWERUP) { run.invincibleItemSpawnCount++; run.dancerSpawnCount++; run.itemSpawnCount++; }
        maybeAdoptDecisionPatternFromEntity(entity, request, km);
      }'''
index = replace_once(index, old_record_end, new_record_end, "adopt normal entity after success")
index_path.write_text(index)
print("P3 patterns now adopt existing safe NORMAL entities")
