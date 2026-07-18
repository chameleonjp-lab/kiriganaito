from pathlib import Path

index_path = Path("index.html")
index = index_path.read_text()

old_constant = '        ONCOMING_CRITICAL_OVERDUE_KM: 0.18,'
new_constant = '        ONCOMING_CRITICAL_OVERDUE_KM: 0.24,'
if old_constant not in index:
    raise SystemExit("critical oncoming threshold missing")
index = index.replace(old_constant, new_constant, 1)

old_critical = '''      function isOncomingCriticallyOverdue(km) {
        return km >= 0.8 && km - spawn.nextOncomingAt >= P2_DENSITY.ONCOMING_CRITICAL_OVERDUE_KM;
      }'''
new_critical = '''      function needsSecondKmHoleQuota(km) {
        return km >= 1 && km < 2 && safeInt(run.holeBand1to2Count) < 6;
      }
      function isOncomingCriticallyOverdue(km) {
        if (needsSecondKmHoleQuota(km)) return false;
        return km >= 0.8 && km - spawn.nextOncomingAt >= P2_DENSITY.ONCOMING_CRITICAL_OVERDUE_KM;
      }'''
if old_critical not in index:
    raise SystemExit("critical oncoming helper missing")
index = index.replace(old_critical, new_critical, 1)

old_run_fields = '''          holeSpawnCount: 0,
          obstacleSpawnCount: 0,'''
new_run_fields = '''          holeSpawnCount: 0,
          holeBand0to1Count: 0,
          holeBand1to2Count: 0,
          obstacleSpawnCount: 0,'''
if old_run_fields not in index:
    raise SystemExit("run hole fields anchor missing")
index = index.replace(old_run_fields, new_run_fields, 1)

old_hole_record = '''        if (entity.zone === WORLD_ZONE.HOLE) { run.holeSpawnCount++; if (source === SPAWN_SOURCE.CHASE) run.chaseHoleSpawnCount++; }'''
new_hole_record = '''        if (entity.zone === WORLD_ZONE.HOLE) {
          run.holeSpawnCount++;
          if (km < 1) run.holeBand0to1Count = safeInt(run.holeBand0to1Count) + 1;
          else if (km < 2) run.holeBand1to2Count = safeInt(run.holeBand1to2Count) + 1;
          if (source === SPAWN_SOURCE.CHASE) run.chaseHoleSpawnCount++;
        }'''
if old_hole_record not in index:
    raise SystemExit("hole record anchor missing")
index = index.replace(old_hole_record, new_hole_record, 1)

index_path.write_text(index)
