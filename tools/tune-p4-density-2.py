from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text()

replacements = [
    (
        '          nextAirObstacleAt: rand(P4_AIR.FIRST_MIN_KM, P4_AIR.FIRST_MAX_KM),',
        '          nextAirObstacleAt: 2.35,',
        'deterministic first air schedule',
    ),
    (
        '''      function nextAirObstacleInterval() {
        return rand(P4_AIR.INTERVAL_MIN_KM, P4_AIR.INTERVAL_MAX_KM);
      }''',
        '''      function nextAirObstacleInterval() {
        return 1.10;
      }''',
        'deterministic air interval',
    ),
    (
        '''      function isGroundHazardNearAirCorridor() {
        const left = P4_AIR.VISIBLE_CLEAR_LEFT_PX;
        const right = W + P4_AIR.VISIBLE_CLEAR_RIGHT_PX;
        const groundObstacle = obstacles.some((entity) =>
          entity.active !== false && entity.zone === WORLD_ZONE.GROUND && entity.objectRole === OBJECT_ROLE.HAZARD &&
          entity.x + entity.w > left && entity.x < right
        );
        const hole = holes.some((entity) => entity.x + entity.w > left && entity.x < right);
        return groundObstacle || hole;
      }''',
        '''      function isGroundHazardNearAirCorridor(airX = -P4_AIR.WIDTH - 18, airWidth = P4_AIR.WIDTH) {
        const left = airX - 18;
        const right = airX + airWidth + 18;
        const groundObstacle = obstacles.some((entity) =>
          entity.active !== false && entity.zone === WORLD_ZONE.GROUND && entity.objectRole === OBJECT_ROLE.HAZARD &&
          entity.x + entity.w > left && entity.x < right
        );
        const hole = holes.some((entity) => entity.x + entity.w > left && entity.x < right);
        return groundObstacle || hole;
      }''',
        'local horizontal air corridor',
    ),
    (
        '''        if (isGroundHazardNearAirCorridor()) return false;
        if (km - spawn.lastHoleAt < P4_AIR.HOLE_BEFORE_KM) return false;
        if (km - spawn.lastObstacleAt < P4_AIR.GROUND_BEFORE_KM) return false;
        if (km - spawn.lastOncomingAt < P4_AIR.ONCOMING_BEFORE_KM) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;''',
        '''        if (isGroundHazardNearAirCorridor()) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;''',
        'remove random-history pre-gap dependency',
    ),
    (
        '        if (isGroundHazardNearAirCorridor()) run.airObstacleFullBlockViolationCount = safeInt(run.airObstacleFullBlockViolationCount) + 1;',
        '        if (isGroundHazardNearAirCorridor(entity.x, entity.w)) run.airObstacleFullBlockViolationCount = safeInt(run.airObstacleFullBlockViolationCount) + 1;',
        'entity-specific block invariant',
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
old_test = '''    let airVisibleNow = 0;
    let groundVisibleNow = 0;
    for (const entity of obstacles) {
      if (entity.active === false || !(entity.x < W && entity.x + entity.w > 0)) continue;
      if (entity.zone === WORLD_ZONE.AIR) {
        airVisibleNow++;
        if (!counted.has(entity)) { counted.add(entity); visibleAir++; }
      } else groundVisibleNow++;
    }
    for (const hole of holes) if (hole.x < W && hole.x + hole.w > 0) groundVisibleNow++;
    if (airVisibleNow > 0 && groundVisibleNow > 0) maxSimultaneousGroundAndAir = Math.max(maxSimultaneousGroundAndAir, airVisibleNow + groundVisibleNow);'''
new_test = '''    const visibleAirEntities = [];
    const visibleGroundEntities = [];
    for (const entity of obstacles) {
      if (entity.active === false || !(entity.x < W && entity.x + entity.w > 0)) continue;
      if (entity.zone === WORLD_ZONE.AIR) {
        visibleAirEntities.push(entity);
        if (!counted.has(entity)) { counted.add(entity); visibleAir++; }
      } else visibleGroundEntities.push(entity);
    }
    for (const hole of holes) {
      if (hole.x < W && hole.x + hole.w > 0) visibleGroundEntities.push(hole);
    }
    let horizontalBlockPairs = 0;
    for (const air of visibleAirEntities) {
      for (const ground of visibleGroundEntities) {
        if (air.x < ground.x + ground.w && air.x + air.w > ground.x) horizontalBlockPairs++;
      }
    }
    maxSimultaneousGroundAndAir = Math.max(maxSimultaneousGroundAndAir, horizontalBlockPairs);'''
if p4_test.count(old_test) != 1:
    raise SystemExit(f'P4 overlap test block: expected 1, got {p4_test.count(old_test)}')
p4_test_path.write_text(p4_test.replace(old_test, new_test, 1))

print('P4 deterministic scheduling and horizontal blockade checks applied')
