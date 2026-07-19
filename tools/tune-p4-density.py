from pathlib import Path

path = Path('index.html')
text = path.read_text()

replacements = [
    ('        GROUND_BEFORE_KM: 0.16,\n        GROUND_AFTER_KM: 0.16,\n        HOLE_BEFORE_KM: 0.18,\n        HOLE_AFTER_KM: 0.18,\n        ONCOMING_BEFORE_KM: 0.20,\n        ONCOMING_AFTER_KM: 0.20,',
     '        GROUND_BEFORE_KM: 0.09,\n        GROUND_AFTER_KM: 0.11,\n        HOLE_BEFORE_KM: 0.10,\n        HOLE_AFTER_KM: 0.14,\n        ONCOMING_BEFORE_KM: 0.12,\n        ONCOMING_AFTER_KM: 0.14,',
     'balanced air safety gaps'),
    ('        const reserveAirObstacle = isAirObstacleReservationActive(km);\n        const suppressNormalGround = spawn.needObstacleBeforeNextHole || reservePattern || reserveHole || reserveScoreItem || reserveAirObstacle;',
     '        const suppressNormalGround = spawn.needObstacleBeforeNextHole || reservePattern || reserveHole || reserveScoreItem;',
     'remove air pre-reservation suppression'),
    ('        if (dueAirObstacle && reserveAirObstacle && canSpawnAirObstacle(km)) {',
     '        if (dueAirObstacle && canSpawnAirObstacle(km)) {',
     'enqueue only when corridor is already safe'),
    ('        if (dueHole && !reservePattern && !reserveAirObstacle && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {',
     '        if (dueHole && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {',
     'do not defer holes while waiting for air'),
    ('''        if (req && req.kind !== SPAWN_REQUEST_KIND.AIR_OBSTACLE && isAirObstacleReservationActive(km)) {
          if (req.kind === SPAWN_REQUEST_KIND.HOLE || isNonMandatoryGroundRequest(req)) return true;
        }
''',
     '',
     'do not defer existing requests for air'),
]

for old, new, label in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1, got {count}')
    text = text.replace(old, new, 1)

path.write_text(text)
print('P4 density interaction tuned')
