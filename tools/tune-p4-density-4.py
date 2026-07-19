from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text()
old = '''      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (isGroundHazardNearAirCorridor()) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }'''
new = '''      function canSpawnAirObstacle(km) {
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
if index.count(old) != 1:
    raise SystemExit(f'canSpawnAirObstacle: expected 1, got {index.count(old)}')
index = index.replace(old, new, 1)
index = index.replace('        ONCOMING_AFTER_KM: 0.020,', '        ONCOMING_AFTER_KM: 0.012,', 1)
index_path.write_text(index)

p4_test_path = Path('tests/p4-air-obstacle-regression.js')
p4_test = p4_test_path.read_text()
old_reset = '''    spawn.lastOncomingAt = -9;
    spawn.needObstacleBeforeNextHole = false;
    spawn.activePattern = null;'''
new_reset = '''    spawn.lastOncomingAt = -9;
    spawn.needObstacleBeforeNextHole = false;
    spawn.activePattern = null;
    spawn.nextHoleAt = km + 0.50;
    spawn.nextObstacleAt = km + 0.50;
    spawn.nextOncomingAt = km + 0.50;'''
if p4_test.count(old_reset) != 1:
    raise SystemExit(f'P4 direct reset schedule: expected 1, got {p4_test.count(old_reset)}')
p4_test_path.write_text(p4_test.replace(old_reset, new_reset, 1))

print('P4 inserts only into pre-existing schedule gaps')
