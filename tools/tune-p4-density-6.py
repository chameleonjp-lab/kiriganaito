from pathlib import Path

path = Path('index.html')
text = path.read_text()

old_constants = '''        WIDTH: 58,
        HEIGHT: 24,
        Y_OFFSET: 76,'''
new_constants = '''        WIDTH: 58,
        HEIGHT: 24,
        Y_OFFSET: 76,
        SPAWN_X: -190,'''
if text.count(old_constants) != 1:
    raise SystemExit(f'P4 spawn X constant: expected 1, got {text.count(old_constants)}')
text = text.replace(old_constants, new_constants, 1)

old_can = '''      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (spawn.nextHoleAt - km < 0.010) return false;
        if (spawn.nextObstacleAt - km < 0.010) return false;
        if (spawn.nextOncomingAt - km < 0.012) return false;
        if (isGroundHazardNearAirCorridor()) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }'''
new_can = '''      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (isGroundHazardNearAirCorridor(P4_AIR.SPAWN_X, P4_AIR.WIDTH)) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }'''
if text.count(old_can) != 1:
    raise SystemExit(f'P4 rear spawn canSpawn: expected 1, got {text.count(old_can)}')
text = text.replace(old_can, new_can, 1)

for old, new, label in [
    ('          x: opt.x ?? -P4_AIR.WIDTH - 18,', '          x: opt.x ?? P4_AIR.SPAWN_X,', 'entity default X'),
    ('            () => ({ x: -P4_AIR.WIDTH - 18 }),', '            () => ({ x: P4_AIR.SPAWN_X }),', 'request payload X'),
    ('            req.payload.x = -P4_AIR.WIDTH - 18;', '            req.payload.x = P4_AIR.SPAWN_X;', 'fallback X'),
]:
    if text.count(old) != 1:
        raise SystemExit(f'{label}: expected 1, got {text.count(old)}')
    text = text.replace(old, new, 1)

old_schedules = '''        spawn.lastAirObstacleAt = km;
        spawn.lastDangerAt = km;
        spawn.nextObstacleAt = Math.max(spawn.nextObstacleAt, km + P4_AIR.GROUND_AFTER_KM);
        spawn.nextHoleAt = Math.max(spawn.nextHoleAt, km + P4_AIR.HOLE_AFTER_KM);
        spawn.nextOncomingAt = Math.max(spawn.nextOncomingAt, km + P4_AIR.ONCOMING_AFTER_KM);
        return true;'''
new_schedules = '''        spawn.lastAirObstacleAt = km;
        spawn.lastDangerAt = km;
        return true;'''
if text.count(old_schedules) != 1:
    raise SystemExit(f'remove P2 schedule mutation: expected 1, got {text.count(old_schedules)}')
text = text.replace(old_schedules, new_schedules, 1)

old_enqueue = '''        let airObstacleQueuedNow = false;
        if (dueAirObstacle && canSpawnAirObstacle(km)) {
          const key = "air-obstacle:" + spawn.nextAirObstacleAt.toFixed(4);
          airObstacleQueuedNow = enqueueSpawnRequestIfNew(
            WORLD_ZONE.AIR,
            SPAWN_REQUEST_KIND.AIR_OBSTACLE,
            SPAWN_SOURCE.NORMAL,
            km,
            key,
            () => ({ x: P4_AIR.SPAWN_X }),
            SPAWN_REQUEST_KIND.AIR_OBSTACLE
          );
        }'''
new_enqueue = '''        if (dueAirObstacle && canSpawnAirObstacle(km)) {
          const key = "air-obstacle:" + spawn.nextAirObstacleAt.toFixed(4);
          enqueueSpawnRequestIfNew(
            WORLD_ZONE.AIR,
            SPAWN_REQUEST_KIND.AIR_OBSTACLE,
            SPAWN_SOURCE.NORMAL,
            km,
            key,
            () => ({ x: P4_AIR.SPAWN_X }),
            SPAWN_REQUEST_KIND.AIR_OBSTACLE
          );
        }'''
if text.count(old_enqueue) != 1:
    raise SystemExit(f'remove same-frame reservation: expected 1, got {text.count(old_enqueue)}')
text = text.replace(old_enqueue, new_enqueue, 1)

replacements = [
    ('        if (dueScoreItem && !airObstacleQueuedNow) {', '        if (dueScoreItem) {', 'restore item schedule'),
    ('        if (dueHole && !airObstacleQueuedNow && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {', '        if (dueHole && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {', 'restore hole schedule'),
    ('        if (dueObstacle && !airObstacleQueuedNow && chaseReady && !suppressNormalGround && !reserveOncoming) {', '        if (dueObstacle && chaseReady && !suppressNormalGround && !reserveOncoming) {', 'restore ground schedule'),
    ('        if (!airObstacleQueuedNow && (oncomingDue || forceEarlyOncoming) && (!suppressNormalGround || forceEarlyOncoming)) {', '        if ((oncomingDue || forceEarlyOncoming) && (!suppressNormalGround || forceEarlyOncoming)) {', 'restore oncoming schedule'),
]
for old, new, label in replacements:
    if text.count(old) != 1:
        raise SystemExit(f'{label}: expected 1, got {text.count(old)}')
    text = text.replace(old, new, 1)

path.write_text(text)
print('P4 rear-lane insertion applied without P2 schedule mutation')
