from pathlib import Path

index_path = Path("index.html")
index = index_path.read_text()

old_helpers = '''      const P2_DENSITY = Object.freeze({
        SCORE_ITEM_OVERDUE_KM: 0.10,
        ONCOMING_OVERDUE_KM: 0.10,
      });
      function spawnRequestQueue(zone) { return spawn.requests && spawn.requests[zone] ? spawn.requests[zone] : []; }
      function hasPendingSpawnRequestKind(kind) {
        const zones = [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE];
        for (let z = 0; z < zones.length; z++) {
          const q = spawnRequestQueue(zones[z]);
          for (let i = 0; i < q.length; i++) {
            const req = q[i];
            if (req.kind === kind && req.status !== SPAWN_REQUEST_STATUS.RESOLVED && req.status !== SPAWN_REQUEST_STATUS.SKIPPED) return true;
          }
        }
        return false;
      }
      function isHoleReservationActive(km) {
        return !spawn.needObstacleBeforeNextHole && (km >= spawn.nextHoleAt || hasPendingSpawnRequestKind(SPAWN_REQUEST_KIND.HOLE));
      }
      function isScoreItemReservationActive(km) {
        const dueAt = spawn.nextScoreItemAt ?? spawn.nextItemAt;
        return !spawn.needObstacleBeforeNextHole && !isHoleReservationActive(km) && km - dueAt >= P2_DENSITY.SCORE_ITEM_OVERDUE_KM;
      }
      function isOncomingReservationActive(km) {
        return km >= 0.8 && !spawn.needObstacleBeforeNextHole && !isHoleReservationActive(km) && !isScoreItemReservationActive(km) && km - spawn.nextOncomingAt >= P2_DENSITY.ONCOMING_OVERDUE_KM;
      }
      function isNonMandatoryGroundRequest(req) {
        if (!req || req.zone !== WORLD_ZONE.GROUND) return false;
        if (req.spawnSource !== SPAWN_SOURCE.NORMAL && req.spawnSource !== SPAWN_SOURCE.CHASE) return false;
        return req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE || req.kind === SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE;
      }
      function shouldDeferSpawnRequest(req, km) {
        if (!isNonMandatoryGroundRequest(req)) return false;
        if (spawn.needObstacleBeforeNextHole) return true;
        if (isHoleReservationActive(km)) return true;
        if (isScoreItemReservationActive(km)) return true;
        return isOncomingReservationActive(km) && req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
      }'''
new_helpers = '''      const P2_DENSITY = Object.freeze({
        SCORE_ITEM_MIN_GAP_KM: 0.11,
        SCORE_ITEM_PREPARE_KM: 0.06,
        ONCOMING_OVERDUE_KM: 0.08,
        ONCOMING_CRITICAL_OVERDUE_KM: 0.18,
      });
      function spawnRequestQueue(zone) { return spawn.requests && spawn.requests[zone] ? spawn.requests[zone] : []; }
      function hasPendingSpawnRequestKind(kind) {
        const zones = [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE];
        for (let z = 0; z < zones.length; z++) {
          const q = spawnRequestQueue(zones[z]);
          for (let i = 0; i < q.length; i++) {
            const req = q[i];
            if (req.kind === kind && req.status !== SPAWN_REQUEST_STATUS.RESOLVED && req.status !== SPAWN_REQUEST_STATUS.SKIPPED) return true;
          }
        }
        return false;
      }
      function getScoreItemDueAt() {
        const scheduled = spawn.nextScoreItemAt ?? spawn.nextItemAt;
        return Math.max(scheduled, safeNumber(spawn.lastScoreItemAt, -9) + P2_DENSITY.SCORE_ITEM_MIN_GAP_KM);
      }
      function isOncomingCriticallyOverdue(km) {
        return km >= 0.8 && km - spawn.nextOncomingAt >= P2_DENSITY.ONCOMING_CRITICAL_OVERDUE_KM;
      }
      function isHoleReservationActive(km) {
        const due = km >= spawn.nextHoleAt || hasPendingSpawnRequestKind(SPAWN_REQUEST_KIND.HOLE);
        return !spawn.needObstacleBeforeNextHole && due && !isOncomingCriticallyOverdue(km);
      }
      function isScoreItemReservationActive(km) {
        return !spawn.needObstacleBeforeNextHole && !isOncomingCriticallyOverdue(km) && !isHoleReservationActive(km) && km >= getScoreItemDueAt() - P2_DENSITY.SCORE_ITEM_PREPARE_KM;
      }
      function isOncomingReservationActive(km) {
        if (isOncomingCriticallyOverdue(km)) return true;
        return km >= 0.8 && !spawn.needObstacleBeforeNextHole && !isHoleReservationActive(km) && !isScoreItemReservationActive(km) && km - spawn.nextOncomingAt >= P2_DENSITY.ONCOMING_OVERDUE_KM;
      }
      function isNonMandatoryGroundRequest(req) {
        if (!req || req.zone !== WORLD_ZONE.GROUND) return false;
        if (req.spawnSource !== SPAWN_SOURCE.NORMAL && req.spawnSource !== SPAWN_SOURCE.CHASE) return false;
        return req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE || req.kind === SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE;
      }
      function shouldDeferSpawnRequest(req, km) {
        if (!isNonMandatoryGroundRequest(req)) return false;
        if (spawn.needObstacleBeforeNextHole) return true;
        if (isOncomingCriticallyOverdue(km)) return req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
        if (isHoleReservationActive(km)) return true;
        if (isScoreItemReservationActive(km)) return true;
        return isOncomingReservationActive(km) && req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
      }'''
if old_helpers not in index:
    raise SystemExit("initial P2 helper block missing")
index = index.replace(old_helpers, new_helpers, 1)

old_spawn_state = '''          lastObstacleAt: -9,
          lastOncomingAt: -9,
          lastPatternName: "none",'''
new_spawn_state = '''          lastObstacleAt: -9,
          lastOncomingAt: -9,
          lastScoreItemAt: -9,
          lastPatternName: "none",'''
if old_spawn_state not in index:
    raise SystemExit("spawn state anchor missing")
index = index.replace(old_spawn_state, new_spawn_state, 1)

old_due_item = '        const dueScoreItem = km >= (spawn.nextScoreItemAt ?? spawn.nextItemAt);'
new_due_item = '        const dueScoreItem = km >= getScoreItemDueAt();'
if old_due_item not in index:
    raise SystemExit("due item anchor missing")
index = index.replace(old_due_item, new_due_item, 1)

old_due_hole_wait = '        } else if (dueHole && spawn.needObstacleBeforeNextHole) spawn.nextHoleAt = Math.max(spawn.nextHoleAt, km + 0.012);'
new_due_hole_wait = '''        } else if (dueHole && spawn.needObstacleBeforeNextHole) {
          if (km < 1) spawn.nextHoleAt = Math.max(spawn.nextHoleAt, km + 0.012);
          else spawn.nextHoleAt = Math.max(spawn.nextHoleAt, km);
        }'''
if old_due_hole_wait not in index:
    raise SystemExit("due hole wait anchor missing")
index = index.replace(old_due_hole_wait, new_due_hole_wait, 1)

old_reward_record = '        if (entity.objectRole === OBJECT_ROLE.REWARD) { run.scoreItemSpawnCount++; run.itemSpawnCount++; if (source === SPAWN_SOURCE.CHASE) run.chaseScoreItemSpawnCount++; }'
new_reward_record = '        if (entity.objectRole === OBJECT_ROLE.REWARD) { run.scoreItemSpawnCount++; run.itemSpawnCount++; spawn.lastScoreItemAt = km; if (source === SPAWN_SOURCE.CHASE) run.chaseScoreItemSpawnCount++; }'
if old_reward_record not in index:
    raise SystemExit("reward record anchor missing")
index = index.replace(old_reward_record, new_reward_record, 1)
index_path.write_text(index)

metrics_path = Path("tests/effective-presentation-metrics.js")
metrics = metrics_path.read_text()
old_metric_vars = '''  let maxDecisionBlankSecAfter500m = 0;
  let lastDecisionSec = 0;
  let presentedMissTargetCount = 0;'''
new_metric_vars = '''  let maxDecisionBlankSecAfter500m = 0;
  let currentDecisionBlankSec = 0;
  let presentedMissTargetCount = 0;'''
if old_metric_vars not in metrics:
    raise SystemExit("event blank vars missing")
metrics = metrics.replace(old_metric_vars, new_metric_vars, 1)

old_event_blank = '''    if (measurementStarted) {
      maxDecisionBlankSecAfter500m = Math.max(maxDecisionBlankSecAfter500m, entity.presentedSec - lastDecisionSec);
      lastDecisionSec = entity.presentedSec;
    }
'''
if old_event_blank not in metrics:
    raise SystemExit("event blank record missing")
metrics = metrics.replace(old_event_blank, "", 1)

old_start = '''      lastAnyKm = run.runMeters / 1000;
      lastAnySec = run.elapsed;
      lastDecisionSec = run.elapsed;
    }'''
new_start = '''      lastAnyKm = run.runMeters / 1000;
      lastAnySec = run.elapsed;
      currentDecisionBlankSec = 0;
    }'''
if old_start not in metrics:
    raise SystemExit("blank start missing")
metrics = metrics.replace(old_start, new_start, 1)

old_tail = '''    if (measurementStarted) {
      const currentKm = run.runMeters / 1000;
      maxBlankKmAfter500m = Math.max(maxBlankKmAfter500m, currentKm - lastAnyKm);
      maxBlankSecAfter500m = Math.max(maxBlankSecAfter500m, run.elapsed - lastAnySec);
      maxDecisionBlankSecAfter500m = Math.max(maxDecisionBlankSecAfter500m, run.elapsed - lastDecisionSec);
    }
  }'''
new_tail = '''    const visibleContent =
      holes.some((entity) => entity.x < W && entity.x + (entity.w || 0) > 0) ||
      obstacles.some((entity) => entity.active !== false && entity.x < W && entity.x + (entity.w || 0) > 0) ||
      items.some((entity) => entity.active !== false && entity.x < W && entity.x + (entity.w || 0) > 0);
    if (measurementStarted) {
      const currentKm = run.runMeters / 1000;
      maxBlankKmAfter500m = Math.max(maxBlankKmAfter500m, currentKm - lastAnyKm);
      maxBlankSecAfter500m = Math.max(maxBlankSecAfter500m, run.elapsed - lastAnySec);
      currentDecisionBlankSec = visibleContent ? 0 : currentDecisionBlankSec + FIXED_STEP;
      maxDecisionBlankSecAfter500m = Math.max(maxDecisionBlankSecAfter500m, currentDecisionBlankSec);
    }
  }'''
if old_tail not in metrics:
    raise SystemExit("event blank tail missing")
metrics = metrics.replace(old_tail, new_tail, 1)
metrics_path.write_text(metrics)

release_path = Path("tests/release-comprehensive.js")
release = release_path.read_text()
release = release.replace(
    "kiriganaito-2026-07-12-v16-spawn-director-correctness",
    "kiriganaito-2026-07-18-v18-effective-density",
)
release = release.replace(
    "criticalIssues.push('CLIENT_VERSION が v14 ではない')",
    "criticalIssues.push('CLIENT_VERSION が v18 ではない')",
)
release_path.write_text(release)
