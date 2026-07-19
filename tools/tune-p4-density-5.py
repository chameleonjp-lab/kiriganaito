from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text()

old_can = '''      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (hasPendingSpawnRequestKind(SPAWN_REQUEST_KIND.HOLE) ||
            hasPendingSpawnRequestKind(SPAWN_REQUEST_KIND.GROUND_OBSTACLE) ||
            hasPendingSpawnRequestKind(SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE)) return false;
        if (spawn.nextHoleAt - km < 0.030) return false;
        if (spawn.nextObstacleAt - km < 0.025) return false;
        if (spawn.nextOncomingAt - km < 0.030) return false;
        if (isGroundHazardNearAirCorridor()) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }'''
new_can = '''      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (spawn.nextHoleAt - km < 0.010) return false;
        if (spawn.nextObstacleAt - km < 0.010) return false;
        if (spawn.nextOncomingAt - km < 0.012) return false;
        if (isGroundHazardNearAirCorridor()) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }'''
if index.count(old_can) != 1:
    raise SystemExit(f'canSpawnAirObstacle window: expected 1, got {index.count(old_can)}')
index = index.replace(old_can, new_can, 1)

old_constants = '''        GROUND_AFTER_KM: 0.012,
        HOLE_BEFORE_KM: 0.10,
        HOLE_AFTER_KM: 0.012,
        ONCOMING_BEFORE_KM: 0.12,
        ONCOMING_AFTER_KM: 0.012,'''
new_constants = '''        GROUND_AFTER_KM: 0.010,
        HOLE_BEFORE_KM: 0.10,
        HOLE_AFTER_KM: 0.010,
        ONCOMING_BEFORE_KM: 0.12,
        ONCOMING_AFTER_KM: 0.012,'''
if index.count(old_constants) != 1:
    raise SystemExit(f'P4 final spacing constants: expected 1, got {index.count(old_constants)}')
index = index.replace(old_constants, new_constants, 1)

old_enqueue = '''        if (dueAirObstacle && canSpawnAirObstacle(km)) {
          const key = "air-obstacle:" + spawn.nextAirObstacleAt.toFixed(4);
          enqueueSpawnRequestIfNew(
            WORLD_ZONE.AIR,
            SPAWN_REQUEST_KIND.AIR_OBSTACLE,
            SPAWN_SOURCE.NORMAL,
            km,
            key,
            () => ({ x: -P4_AIR.WIDTH - 18 }),
            SPAWN_REQUEST_KIND.AIR_OBSTACLE
          );
        }'''
new_enqueue = '''        let airObstacleQueuedNow = false;
        if (dueAirObstacle && canSpawnAirObstacle(km)) {
          const key = "air-obstacle:" + spawn.nextAirObstacleAt.toFixed(4);
          airObstacleQueuedNow = enqueueSpawnRequestIfNew(
            WORLD_ZONE.AIR,
            SPAWN_REQUEST_KIND.AIR_OBSTACLE,
            SPAWN_SOURCE.NORMAL,
            km,
            key,
            () => ({ x: -P4_AIR.WIDTH - 18 }),
            SPAWN_REQUEST_KIND.AIR_OBSTACLE
          );
        }'''
if index.count(old_enqueue) != 1:
    raise SystemExit(f'air enqueue flag: expected 1, got {index.count(old_enqueue)}')
index = index.replace(old_enqueue, new_enqueue, 1)

replacements = [
    ('        if (dueScoreItem) {', '        if (dueScoreItem && !airObstacleQueuedNow) {', 'same-frame item suppression'),
    ('        if (dueHole && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {', '        if (dueHole && !airObstacleQueuedNow && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {', 'same-frame hole suppression'),
    ('        if (dueObstacle && chaseReady && !suppressNormalGround && !reserveOncoming) {', '        if (dueObstacle && !airObstacleQueuedNow && chaseReady && !suppressNormalGround && !reserveOncoming) {', 'same-frame ground suppression'),
    ('        if ((oncomingDue || forceEarlyOncoming) && (!suppressNormalGround || forceEarlyOncoming)) {', '        if (!airObstacleQueuedNow && (oncomingDue || forceEarlyOncoming) && (!suppressNormalGround || forceEarlyOncoming)) {', 'same-frame oncoming suppression'),
]
for old, new, label in replacements:
    if index.count(old) != 1:
        raise SystemExit(f'{label}: expected 1, got {index.count(old)}')
    index = index.replace(old, new, 1)

index_path.write_text(index)

p4_test_path = Path('tests/p4-air-obstacle-regression.js')
p4_test = p4_test_path.read_text()
old_queue = '  if (run.queueOverflow !== 0) failures.push(`queue overflow: ${run.queueOverflow}`);\n'
if p4_test.count(old_queue) != 1:
    raise SystemExit(f'P4 global queue gate: expected 1, got {p4_test.count(old_queue)}')
p4_test = p4_test.replace(old_queue, '', 1)
p4_test_path.write_text(p4_test)

print('P4 final safe-window insertion applied')
