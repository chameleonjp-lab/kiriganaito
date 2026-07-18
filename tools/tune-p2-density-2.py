from pathlib import Path

index_path = Path("index.html")
index = index_path.read_text()

old_defer = '''      function shouldDeferSpawnRequest(req, km) {
        if (!isNonMandatoryGroundRequest(req)) return false;
        if (spawn.needObstacleBeforeNextHole) return true;
        if (isOncomingCriticallyOverdue(km)) return req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
        if (isHoleReservationActive(km)) return true;
        if (isScoreItemReservationActive(km)) return true;
        return isOncomingReservationActive(km) && req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
      }'''
new_defer = '''      function shouldDeferSpawnRequest(req, km) {
        if (req && req.kind === SPAWN_REQUEST_KIND.HOLE && isOncomingCriticallyOverdue(km)) return true;
        if (!isNonMandatoryGroundRequest(req)) return false;
        if (spawn.needObstacleBeforeNextHole) return true;
        if (isOncomingCriticallyOverdue(km)) return req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
        if (isHoleReservationActive(km)) return true;
        if (isScoreItemReservationActive(km)) return true;
        return isOncomingReservationActive(km) && req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
      }'''
if old_defer not in index:
    raise SystemExit("second-pass defer block missing")
index = index.replace(old_defer, new_defer, 1)

old_due_hole = '''        if (dueHole && !spawn.needObstacleBeforeNextHole && chaseReady) {'''
new_due_hole = '''        if (dueHole && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {'''
if old_due_hole not in index:
    raise SystemExit("due hole condition missing")
index = index.replace(old_due_hole, new_due_hole, 1)

old_retry = 'req.nextAttemptKm = km + SPAWN_DIRECTOR_LIMITS.retryKm;'
new_retry = 'req.nextAttemptKm = km + (req.kind === SPAWN_REQUEST_KIND.HOLE ? 0.003 : SPAWN_DIRECTOR_LIMITS.retryKm);'
retry_count = index.count(old_retry)
if retry_count < 2:
    raise SystemExit(f"expected at least two retry assignments, found {retry_count}")
index = index.replace(old_retry, new_retry)

index_path.write_text(index)
