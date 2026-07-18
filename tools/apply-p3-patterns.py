from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


root = Path(".")
index_path = root / "index.html"
index = index_path.read_text()

index = index.replace(
    "kiriganaito-2026-07-18-v18-effective-density",
    "kiriganaito-2026-07-19-v19-decision-patterns",
)

run_anchor = """          spawnEarlyOncomingResolvedCount: 0,
          spawnPatternResolvedCount: 0,
        };"""
run_replacement = """          spawnEarlyOncomingResolvedCount: 0,
          spawnPatternResolvedCount: 0,
          patternStartedCount: 0,
          patternCompletedCount: 0,
          patternAbortedCount: 0,
          patternStepResolvedCount: 0,
          patternStepSkippedCount: 0,
          patternMaxConsecutiveSame: 0,
          patternCurrentConsecutiveSame: 0,
          patternHistory: [],
          patternCounts: {},
          patternAbortReasons: {},
        };"""
index = replace_once(index, run_anchor, run_replacement, "run pattern state")

spawn_anchor = """          lastScoreItemAt: -9,
          lastPatternName: "none",
          nextChaseEventAt: 999,"""
spawn_replacement = """          lastScoreItemAt: -9,
          lastPatternName: "none",
          nextPatternAt: 0.22,
          patternNextId: 1,
          patternBag: [],
          patternBagKey: "",
          activePattern: null,
          nextChaseEventAt: 999,"""
index = replace_once(index, spawn_anchor, spawn_replacement, "spawn pattern state")

p2_anchor = """      const P2_DENSITY = Object.freeze({
        SCORE_ITEM_MIN_GAP_KM: 0.11,
        SCORE_ITEM_PREPARE_KM: 0.06,
        ONCOMING_OVERDUE_KM: 0.08,
        ONCOMING_CRITICAL_OVERDUE_KM: 0.275,
      });
      function spawnRequestQueue(zone) { return spawn.requests && spawn.requests[zone] ? spawn.requests[zone] : []; }"""

p3_block = r'''      const P2_DENSITY = Object.freeze({
        SCORE_ITEM_MIN_GAP_KM: 0.11,
        SCORE_ITEM_PREPARE_KM: 0.06,
        ONCOMING_OVERDUE_KM: 0.08,
        ONCOMING_CRITICAL_OVERDUE_KM: 0.275,
      });
      const P3_PATTERN = Object.freeze({
        PREPARE_KM: 0.006,
        MAX_STEP_LATE_KM: 0.08,
        MAX_PATTERN_SPAN_KM: 0.46,
        EARLY_DELAY_MIN_KM: 0.20,
        EARLY_DELAY_MAX_KM: 0.30,
        NORMAL_DELAY_MIN_KM: 0.36,
        NORMAL_DELAY_MAX_KM: 0.56,
        O_TO_H_SAFE_KM: 0.18,
      });
      const P3_PATTERN_DEFS = Object.freeze([
        { name: "G_S_H", learning: true, minKm: 0, steps: [
          { symbol: "G", offsetKm: 0, payload: { dir: -1, emoji: "🚶", x: -44 } },
          { symbol: "H", offsetKm: 0.09, payload: { kind: "SMALL", w: 30 } },
        ] },
        { name: "H_S_G", learning: true, minKm: 0, steps: [
          { symbol: "H", offsetKm: 0, payload: { kind: "SMALL", w: 30 } },
          { symbol: "G", offsetKm: 0.10, satisfiesBetweenHole: true, payload: { dir: -1, emoji: "🚶", x: -44 } },
        ] },
        { name: "G_A", learning: true, minKm: 0, steps: [
          { symbol: "G", offsetKm: 0, payload: { dir: -1, emoji: "🚶", x: -44 } },
          { symbol: "A", offsetKm: 0, overlay: true, payload: { lane: "high", high: true, type: "💰", x: -44, challenge: false } },
        ] },
        { name: "H_A", learning: true, minKm: 0, steps: [
          { symbol: "H", offsetKm: 0, payload: { kind: "SMALL", w: 30, x: -46 } },
          { symbol: "A", offsetKm: 0, overlay: true, payload: { lane: "high", high: true, type: "💰", x: -44, challenge: false } },
        ] },
        { name: "O_S_H", learning: false, minKm: 1, steps: [
          { symbol: "O", offsetKm: 0, payload: { dir: 1, emoji: "🚶" } },
          { symbol: "H", offsetKm: 0.18, payload: { kind: "SMALL", w: 30 } },
        ] },
        { name: "H_S_O", learning: false, minKm: 1, steps: [
          { symbol: "H", offsetKm: 0, payload: { kind: "SMALL", w: 30 } },
          { symbol: "O", offsetKm: 0.16, satisfiesBetweenHole: true, payload: { dir: 1, emoji: "🚶" } },
        ] },
        { name: "G_A_H", learning: false, minKm: 1, steps: [
          { symbol: "G", offsetKm: 0, payload: { dir: -1, emoji: "🏃🏻", x: -44 } },
          { symbol: "A", offsetKm: 0.045, payload: { lane: "mid", high: false, type: "💰", x: -44, challenge: false } },
          { symbol: "H", offsetKm: 0.13, payload: { kind: "SMALL", w: 30 } },
        ] },
        { name: "P_G_G", learning: false, minKm: 2, requiresPowerup: true, steps: [
          { symbol: "P", offsetKm: 0, payload: { type: "👯‍♀️", lane: "mid", high: false, x: -36 } },
          { symbol: "G", offsetKm: 0.07, payload: { dir: -1, emoji: "🏃🏻", x: -44 } },
          { symbol: "G", offsetKm: 0.145, payload: { dir: -1, emoji: "🚴", x: -44 } },
        ] },
      ]);
      function decisionPatternByName(name) {
        return P3_PATTERN_DEFS.find((def) => def.name === name) || null;
      }
      function availableDecisionPatterns(km) {
        return P3_PATTERN_DEFS.filter((def) => {
          if (km < 1) return def.learning === true;
          if (km < def.minKm) return false;
          if (def.requiresPowerup && km < run.nextDancerAt) return false;
          return true;
        });
      }
      function shuffleDecisionPatternNames(names) {
        const result = names.slice();
        for (let i = result.length - 1; i > 0; i--) {
          const j = (Math.random() * (i + 1)) | 0;
          const tmp = result[i]; result[i] = result[j]; result[j] = tmp;
        }
        return result;
      }
      function rememberDecisionPatternChoice(name) {
        const history = Array.isArray(run.patternHistory) ? run.patternHistory : [];
        const previous = history.length ? history[history.length - 1] : "";
        run.patternCurrentConsecutiveSame = previous === name ? safeInt(run.patternCurrentConsecutiveSame) + 1 : 1;
        run.patternMaxConsecutiveSame = Math.max(safeInt(run.patternMaxConsecutiveSame), run.patternCurrentConsecutiveSame);
        history.push(name);
        while (history.length > 12) history.shift();
        run.patternHistory = history;
        run.patternCounts[name] = safeInt(run.patternCounts[name]) + 1;
      }
      function selectNextDecisionPattern(km, remember = true) {
        const available = availableDecisionPatterns(km);
        if (!available.length) return null;
        const key = available.map((def) => def.name).join("|");
        if (spawn.patternBagKey !== key || !Array.isArray(spawn.patternBag) || !spawn.patternBag.length) {
          spawn.patternBagKey = key;
          spawn.patternBag = shuffleDecisionPatternNames(available.map((def) => def.name));
        }
        const history = Array.isArray(run.patternHistory) ? run.patternHistory : [];
        const last = history.length > 0 ? history[history.length - 1] : "";
        const secondLast = history.length > 1 ? history[history.length - 2] : "";
        let pickIndex = spawn.patternBag.length - 1;
        if (last && last === secondLast && spawn.patternBag[pickIndex] === last) {
          const alternate = spawn.patternBag.findIndex((name) => name !== last);
          if (alternate >= 0) pickIndex = alternate;
        }
        const name = spawn.patternBag.splice(pickIndex, 1)[0];
        if (remember) rememberDecisionPatternChoice(name);
        return decisionPatternByName(name);
      }
      function validateDecisionPatternDefinitions() {
        const errors = [];
        const learning = P3_PATTERN_DEFS.filter((def) => def.learning);
        if (learning.length !== 4) errors.push("learning pattern count must be 4");
        for (const def of P3_PATTERN_DEFS) {
          const hazardAt = {};
          const hazards = [];
          for (let i = 0; i < def.steps.length; i++) {
            const step = def.steps[i];
            if (!["G", "O", "A", "H", "P"].includes(step.symbol)) errors.push(def.name + ": unknown symbol " + step.symbol);
            if (!Number.isFinite(step.offsetKm) || step.offsetKm < 0) errors.push(def.name + ": invalid offset");
            if (["G", "O", "H"].includes(step.symbol)) {
              const key = step.offsetKm.toFixed(4);
              hazardAt[key] = safeInt(hazardAt[key]) + 1;
              hazards.push(step);
            }
            if (step.overlay && step.symbol !== "A") errors.push(def.name + ": only A may overlay");
          }
          for (const key in hazardAt) if (hazardAt[key] > 1) errors.push(def.name + ": simultaneous hazards");
          hazards.sort((a, b) => a.offsetKm - b.offsetKm);
          for (let i = 1; i < hazards.length; i++) {
            const before = hazards[i - 1], after = hazards[i], gap = after.offsetKm - before.offsetKm;
            if (before.symbol === "G" && after.symbol === "H" && gap < SPAWN.HOLE_AFTER_OBSTACLE) errors.push(def.name + ": G-H gap");
            if (before.symbol === "H" && after.symbol === "G" && gap < SPAWN.OBSTACLE_AFTER_HOLE) errors.push(def.name + ": H-G gap");
            if (before.symbol === "H" && after.symbol === "O" && gap < SPAWN.ONCOMING_AFTER_HOLE_SAFE_GAP) errors.push(def.name + ": H-O gap");
            if (before.symbol === "O" && after.symbol === "H" && gap < P3_PATTERN.O_TO_H_SAFE_KM) errors.push(def.name + ": O-H gap");
          }
        }
        return errors;
      }
      function nextDecisionPatternDelay(km) {
        return km < 1 ? rand(P3_PATTERN.EARLY_DELAY_MIN_KM, P3_PATTERN.EARLY_DELAY_MAX_KM) : rand(P3_PATTERN.NORMAL_DELAY_MIN_KM, P3_PATTERN.NORMAL_DELAY_MAX_KM);
      }
      function startDecisionPattern(def, km) {
        if (!def || spawn.activePattern) return false;
        const id = spawn.patternNextId++;
        spawn.activePattern = {
          id,
          name: def.name,
          startKm: km,
          status: "active",
          steps: def.steps.map((step, index) => ({
            index,
            symbol: step.symbol,
            offsetKm: step.offsetKm,
            dueKm: km + step.offsetKm,
            overlay: Boolean(step.overlay),
            satisfiesBetweenHole: Boolean(step.satisfiesBetweenHole),
            payload: Object.assign({}, step.payload || {}),
            status: "waiting",
          })),
        };
        spawn.lastPatternName = def.name;
        spawn.nextPatternAt = km + nextDecisionPatternDelay(km);
        run.patternStartedCount = safeInt(run.patternStartedCount) + 1;
        return true;
      }
      function finishDecisionPattern(km) {
        if (!spawn.activePattern || spawn.activePattern.status !== "active") return;
        spawn.activePattern.status = "completed";
        run.patternCompletedCount = safeInt(run.patternCompletedCount) + 1;
        spawn.activePattern = null;
        spawn.nextPatternAt = Math.max(spawn.nextPatternAt, km + nextDecisionPatternDelay(km));
      }
      function abortDecisionPattern(reason, km) {
        const active = spawn.activePattern;
        if (!active || active.status !== "active") return;
        active.status = "aborted";
        active.abortReason = reason;
        run.patternAbortedCount = safeInt(run.patternAbortedCount) + 1;
        run.patternAbortReasons[reason] = safeInt(run.patternAbortReasons[reason]) + 1;
        spawn.nextPatternAt = Math.max(spawn.nextPatternAt, km + 0.18);
      }
      function cleanupOrphanedPatternRequests() {
        const active = spawn.activePattern && spawn.activePattern.status === "active" ? spawn.activePattern.id : null;
        const zones = [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE];
        for (const zone of zones) {
          const kept = [];
          for (const req of spawnRequestQueue(zone)) {
            if (req.patternId && req.patternId !== active) {
              if (req.status !== SPAWN_REQUEST_STATUS.RESOLVED && req.status !== SPAWN_REQUEST_STATUS.SKIPPED) run.spawnRequestSkippedCount++;
            } else kept.push(req);
          }
          spawn.requests[zone] = kept;
        }
        if (spawn.activePattern && spawn.activePattern.status === "aborted") spawn.activePattern = null;
      }
      function maybeStartDecisionPattern(km) {
        cleanupOrphanedPatternRequests();
        const active = spawn.activePattern;
        if (active && active.status === "active") {
          if (run.chase > 0 || isDancerInvincible()) abortDecisionPattern("mode_changed", km);
          else if (km - active.startKm > P3_PATTERN.MAX_PATTERN_SPAN_KM) abortDecisionPattern("pattern_timeout", km);
          cleanupOrphanedPatternRequests();
          return;
        }
        if (km < spawn.nextPatternAt || run.chase > 0 || isDancerInvincible()) return;
        if (spawn.needObstacleBeforeNextHole || pendingSpawnRequestCount() > 0) return;
        if (isHoleReservationActive(km) || isScoreItemReservationActive(km) || isOncomingCriticallyOverdue(km)) return;
        const def = selectNextDecisionPattern(km, true);
        if (def) startDecisionPattern(def, km);
      }
      function isDecisionPatternReservationActive() {
        return Boolean(spawn.activePattern && spawn.activePattern.status === "active");
      }
      function decisionPatternOwnsBetweenHoleObstacle() {
        const active = spawn.activePattern;
        return Boolean(active && active.status === "active" && active.steps.some((step) => step.satisfiesBetweenHole && step.status !== "resolved" && step.status !== "skipped"));
      }
      function makeDecisionPatternRequest(active, step) {
        let zone, kind, fallbackKind;
        const payload = Object.assign({}, step.payload || {});
        if (step.symbol === "G") { zone = WORLD_ZONE.GROUND; kind = SPAWN_REQUEST_KIND.GROUND_OBSTACLE; fallbackKind = kind; payload.dir = -1; payload.x = payload.x ?? -44; }
        else if (step.symbol === "O") { zone = WORLD_ZONE.GROUND; kind = SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE; fallbackKind = kind; payload.dir = 1; payload.x = getOncomingSpawnX(step.dueKm); }
        else if (step.symbol === "A") { zone = WORLD_ZONE.AIR; kind = SPAWN_REQUEST_KIND.SCORE_ITEM; fallbackKind = kind; }
        else if (step.symbol === "H") { zone = WORLD_ZONE.HOLE; kind = SPAWN_REQUEST_KIND.HOLE; fallbackKind = kind; }
        else if (step.symbol === "P") { zone = WORLD_ZONE.GROUND; kind = SPAWN_REQUEST_KIND.POWERUP; fallbackKind = kind; }
        else return null;
        const req = makeSpawnRequest(zone, kind, SPAWN_SOURCE.PATTERN, step.dueKm, "pattern:" + active.id + ":" + step.index, payload, fallbackKind);
        req.patternId = active.id;
        req.patternName = active.name;
        req.patternStepIndex = step.index;
        req.patternSymbol = step.symbol;
        req.patternAllowsItemPlacement = step.symbol === "A";
        req.satisfiesBetweenHole = step.satisfiesBetweenHole;
        if (step.satisfiesBetweenHole) req.priority = SPAWN_SOURCE_PRIORITY[SPAWN_SOURCE.BETWEEN_HOLES];
        return req;
      }
      function collectDecisionPatternRequests(km) {
        maybeStartDecisionPattern(km);
        const active = spawn.activePattern;
        if (!active || active.status !== "active") return;
        for (const step of active.steps) {
          if (step.status !== "waiting") continue;
          if (km < step.dueKm - P3_PATTERN.PREPARE_KM) continue;
          const req = makeDecisionPatternRequest(active, step);
          if (req && enqueueSpawnRequest(req)) {
            step.status = "queued";
            if (step.symbol === "O") run.oncomingCandidateCount++;
          } else if (km - step.dueKm > P3_PATTERN.MAX_STEP_LATE_KM) {
            step.status = "skipped";
            run.patternStepSkippedCount = safeInt(run.patternStepSkippedCount) + 1;
            abortDecisionPattern("enqueue_timeout", km);
          }
        }
      }
      function recordDecisionPatternRequestOutcome(req, success, km, entity) {
        if (!req || !req.patternId) return;
        const active = spawn.activePattern;
        if (!active || active.id !== req.patternId || active.status !== "active") return;
        const step = active.steps.find((candidate) => candidate.index === req.patternStepIndex);
        if (!step) return;
        if (entity) {
          entity.patternId = req.patternId;
          entity.patternName = req.patternName;
          entity.patternStepIndex = req.patternStepIndex;
          entity.patternSymbol = req.patternSymbol;
        }
        if (success) {
          step.status = "resolved";
          run.patternStepResolvedCount = safeInt(run.patternStepResolvedCount) + 1;
          if (active.steps.every((candidate) => candidate.status === "resolved")) finishDecisionPattern(km);
        } else {
          step.status = "skipped";
          run.patternStepSkippedCount = safeInt(run.patternStepSkippedCount) + 1;
          abortDecisionPattern("step_skipped", km);
        }
      }
      function spawnRequestQueue(zone) { return spawn.requests && spawn.requests[zone] ? spawn.requests[zone] : []; }'''

index = replace_once(index, p2_anchor, p3_block, "P3 pattern block")

collect_anchor = """        const forceEarlyOncoming = (earlyOncomingDue || (km >= 2 && !run.earlyOncomingSpawned));
        const reserveHole = isHoleReservationActive(km);
        const reserveScoreItem = isScoreItemReservationActive(km);
        const reserveOncoming = isOncomingReservationActive(km);
        const suppressNormalGround = spawn.needObstacleBeforeNextHole || reserveHole || reserveScoreItem;"""
collect_replacement = """        const forceEarlyOncoming = (earlyOncomingDue || (km >= 2 && !run.earlyOncomingSpawned));
        collectDecisionPatternRequests(km);
        const reservePattern = isDecisionPatternReservationActive();
        const reserveHole = isHoleReservationActive(km);
        const reserveScoreItem = isScoreItemReservationActive(km);
        const reserveOncoming = isOncomingReservationActive(km);
        const suppressNormalGround = spawn.needObstacleBeforeNextHole || reservePattern || reserveHole || reserveScoreItem;"""
index = replace_once(index, collect_anchor, collect_replacement, "collect pattern reservation")

index = replace_once(
    index,
    "if (spawn.needObstacleBeforeNextHole && chaseReady) {",
    "if (spawn.needObstacleBeforeNextHole && chaseReady && !decisionPatternOwnsBetweenHoleObstacle()) {",
    "pattern owns mandatory obstacle",
)
index = replace_once(index, "if (dueScoreItem) {", "if (dueScoreItem && !reservePattern) {", "suppress normal item")
index = replace_once(
    index,
    "if (dueHole && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {",
    "if (dueHole && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {",
    "suppress normal hole",
)
index = replace_once(
    index,
    "if (km >= run.nextDancerAt) {",
    "if (km >= run.nextDancerAt && !reservePattern) {",
    "suppress normal dancer",
)

should_defer_anchor = """      function shouldDeferSpawnRequest(req, km) {
        if (req && req.kind === SPAWN_REQUEST_KIND.HOLE && isOncomingCriticallyOverdue(km)) return true;"""
should_defer_replacement = """      function shouldDeferSpawnRequest(req, km) {
        if (req && req.spawnSource === SPAWN_SOURCE.PATTERN) return false;
        if (req && req.kind === SPAWN_REQUEST_KIND.HOLE && isOncomingCriticallyOverdue(km)) return true;"""
index = replace_once(index, should_defer_anchor, should_defer_replacement, "pattern defer bypass")

item_resolve_anchor = """        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) ok = canSpawnItem(km) && spawnItemPattern(km, d, Object.assign({}, req.payload, { spawnSource: req.spawnSource, directorManaged: true }));"""
item_resolve_replacement = """        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) {
          const itemPlacementAllowed = req.patternAllowsItemPlacement === true || canSpawnItem(km);
          ok = itemPlacementAllowed && spawnItemPattern(km, d, Object.assign({}, req.payload, { spawnSource: req.spawnSource, directorManaged: true }));
        }"""
index = replace_once(index, item_resolve_anchor, item_resolve_replacement, "pattern item placement")

success_anchor = """          advanceScheduleAfterResolution(req, entity, km, d);
          req.status = SPAWN_REQUEST_STATUS.RESOLVED;
          return true;"""
success_replacement = """          advanceScheduleAfterResolution(req, entity, km, d);
          req.status = SPAWN_REQUEST_STATUS.RESOLVED;
          recordDecisionPatternRequestOutcome(req, true, km, entity);
          return true;"""
index = replace_once(index, success_anchor, success_replacement, "pattern success outcome")

skip_anchor = """            req.status = SPAWN_REQUEST_STATUS.SKIPPED; run.spawnRequestSkippedCount++; if (req.spawnSource === SPAWN_SOURCE.BETWEEN_HOLES) resolveBetweenHoleObstacle(km, req.payload && req.payload.dir); advanceScheduleAfterResolution(req, null, km, d); return true;"""
skip_replacement = """            req.status = SPAWN_REQUEST_STATUS.SKIPPED;
            run.spawnRequestSkippedCount++;
            recordDecisionPatternRequestOutcome(req, false, km, null);
            if (req.spawnSource === SPAWN_SOURCE.BETWEEN_HOLES) resolveBetweenHoleObstacle(km, req.payload && req.payload.dir);
            advanceScheduleAfterResolution(req, null, km, d);
            return true;"""
index = replace_once(index, skip_anchor, skip_replacement, "pattern skip outcome")

snapshot_anchor = """          spawnEarlyOncomingResolvedCount: safeInt(run.spawnEarlyOncomingResolvedCount),
          spawnPatternResolvedCount: safeInt(run.spawnPatternResolvedCount),
          spawnPendingCount: pendingSpawnRequestCount(),"""
snapshot_replacement = """          spawnEarlyOncomingResolvedCount: safeInt(run.spawnEarlyOncomingResolvedCount),
          spawnPatternResolvedCount: safeInt(run.spawnPatternResolvedCount),
          patternStartedCount: safeInt(run.patternStartedCount),
          patternCompletedCount: safeInt(run.patternCompletedCount),
          patternAbortedCount: safeInt(run.patternAbortedCount),
          patternStepResolvedCount: safeInt(run.patternStepResolvedCount),
          patternStepSkippedCount: safeInt(run.patternStepSkippedCount),
          patternMaxConsecutiveSame: safeInt(run.patternMaxConsecutiveSame),
          patternCounts: Object.assign({}, run.patternCounts || {}),
          patternAbortReasons: Object.assign({}, run.patternAbortReasons || {}),
          activePatternName: spawn.activePattern ? spawn.activePattern.name : "",
          spawnPendingCount: pendingSpawnRequestCount(),"""
index = replace_once(index, snapshot_anchor, snapshot_replacement, "pattern snapshot")

index_path.write_text(index)

metrics_path = root / "tests" / "effective-presentation-metrics.js"
metrics = metrics_path.read_text()
metrics_anchor = """    maxSimultaneousStrongHazards,
    generatedRelationOk,"""
metrics_replacement = """    maxSimultaneousStrongHazards,
    patternStats: {
      started: safeInt(run.patternStartedCount),
      completed: safeInt(run.patternCompletedCount),
      aborted: safeInt(run.patternAbortedCount),
      stepResolved: safeInt(run.patternStepResolvedCount),
      stepSkipped: safeInt(run.patternStepSkippedCount),
      maxConsecutiveSame: safeInt(run.patternMaxConsecutiveSame),
      counts: Object.assign({}, run.patternCounts || {}),
      activePatternName: spawn.activePattern ? spawn.activePattern.name : "",
    },
    generatedRelationOk,"""
metrics = replace_once(metrics, metrics_anchor, metrics_replacement, "P1 pattern metrics")
metrics_path.write_text(metrics)

spec_path = root / "SPEC.md"
spec = spec_path.read_text()
if "## v19 判断パターン契約" not in spec:
    spec += """

## v19 判断パターン契約

- 現行 `CLIENT_VERSION` は `kiriganaito-2026-07-19-v19-decision-patterns`。
- 既存の `G / O / A / H / P` を2〜3ステップの短いパターンとして予約する。
- 0〜1kmは `G_S_H / H_S_G / G_A / H_A` の学習用4種類だけを使用する。
- 1km以降に `O_S_H / H_S_O / G_A_H`、2km以降かつ👯‍♀️出現可能時に `P_G_G` を解禁する。
- シャッフルバッグで単一パターン25%以下を保証し、同一パターン3連続を禁止する。
- パターン中も既存の安全距離、TTC、穴間必須障害物、最大同時危険数を維持する。
- パターンの失敗、期限超過、逃走・無敵への状態変化ではパターンを中断し、通常SpawnDirectorへ復帰する。
- 詳細契約は `P3_DECISION_PATTERN_CONTRACT.md` を正本とする。
"""
spec = spec.replace("kiriganaito-2026-07-18-v18-effective-density", "kiriganaito-2026-07-19-v19-decision-patterns")
spec_path.write_text(spec)

report_path = root / "TEST_REPORT.md"
report = report_path.read_text()
if "## v19 P3 判断パターン" not in report:
    report += """

## v19 P3 判断パターン

- 既存オブジェクトだけを使う8種類の短い判断パターンを導入。
- 0〜1kmは学習用4種類だけ、1km以降に複合パターンを段階解禁。
- 10,000回選択の分布、3連続禁止、定義安全性を `tests/p3-pattern-regression.js` で検査。
- P1実効出現、P2 30seed、progressive autoplay、release comprehensive、150km耐久を同時回帰検査する。
- 実機、Playwright/WebKit、Codeberg Pagesは未確認。
"""
report_path.write_text(report)

print("P3 decision pattern implementation applied")
