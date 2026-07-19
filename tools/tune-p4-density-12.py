from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text()

replacements = [
    (
        '        SCROLL_PX: STATIC_OBSTACLE_SCROLL_PX,',
        '        SCROLL_PX: 190,',
        'anchored P4 follow speed',
    ),
    (
        '''      function isGroundHazardNearAirCorridor(airX = P4_AIR.SPAWN_X, airWidth = P4_AIR.WIDTH) {
        const left = airX - 18;
        const right = player.x + 80;
        const groundObstacle = obstacles.some((entity) =>
          entity.active !== false && entity.zone === WORLD_ZONE.GROUND && entity.objectRole === OBJECT_ROLE.HAZARD &&
          entity.x + entity.w > left && entity.x < right
        );
        const hole = holes.some((entity) => entity.x + entity.w > left && entity.x < right);
        return groundObstacle || hole;
      }''',
        '''      function isGroundHazardNearAirCorridor(airX = P4_AIR.SPAWN_X, airWidth = P4_AIR.WIDTH) {
        const left = airX - 18;
        const right = airX + airWidth + 18;
        const groundObstacle = obstacles.some((entity) =>
          entity.active !== false && entity.zone === WORLD_ZONE.GROUND && entity.objectRole === OBJECT_ROLE.HAZARD &&
          entity.x + entity.w > left && entity.x < right
        );
        const hole = holes.some((entity) => entity.x + entity.w > left && entity.x < right);
        return groundObstacle || hole;
      }''',
        'local P4 spawn corridor',
    ),
    (
        '''      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (isGroundHazardNearAirCorridor(P4_AIR.SPAWN_X, P4_AIR.WIDTH)) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }''',
        '''      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (km - safeNumber(spawn.lastGroundObstacleAt, -9) > 0.003) return false;
        if (obstacles.some((entity) => entity.active !== false && entity.zone === WORLD_ZONE.AIR && entity.objectRole === OBJECT_ROLE.HAZARD)) return false;
        if (isGroundHazardNearAirCorridor(P4_AIR.SPAWN_X, P4_AIR.WIDTH)) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }''',
        'anchor P4 after ground success',
    ),
    (
        '          lastObstacleAt: -9,\n          lastOncomingAt: -9,',
        '          lastObstacleAt: -9,\n          lastGroundObstacleAt: -9,\n          lastOncomingAt: -9,',
        'ground anchor state',
    ),
    (
        '''        spawn.lastObstacleAt = km;
        spawn.lastDangerAt = km;''',
        '''        spawn.lastObstacleAt = km;
        if (dir === -1) spawn.lastGroundObstacleAt = km;
        spawn.lastDangerAt = km;''',
        'ground anchor update',
    ),
]

for old, new, label in replacements:
    count = index.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1, got {count}')
    index = index.replace(old, new, 1)
index_path.write_text(index)

p4_test_path = Path('tests/p4-air-obstacle-regression.js')
p4_test = p4_test_path.read_text()
old_reset = '''    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;'''
new_reset = '''    spawn.lastObstacleAt = -9;
    spawn.lastGroundObstacleAt = km;
    spawn.lastOncomingAt = -9;'''
if p4_test.count(old_reset) != 1:
    raise SystemExit(f'P4 direct ground anchor reset: expected 1, got {p4_test.count(old_reset)}')
p4_test_path.write_text(p4_test.replace(old_reset, new_reset, 1))

print('P4 anchored behind a successful ground obstacle')
