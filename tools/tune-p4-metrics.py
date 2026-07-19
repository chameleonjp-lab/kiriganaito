from pathlib import Path

path = Path('tests/effective-presentation-metrics.js')
text = path.read_text()

replacements = [
    (
        '  const categoryNames = ["hole", "groundObstacle", "oncoming", "scoreItem", "powerup"];',
        '  const categoryNames = ["hole", "groundObstacle", "airObstacle", "oncoming", "scoreItem", "powerup"];',
        2,
        'category lists',
    ),
    (
        '        recordPresented(entity.movementType === MOVEMENT_TYPE.ONCOMING ? "oncoming" : "groundObstacle", entity);',
        '        recordPresented(entity.zone === WORLD_ZONE.AIR ? "airObstacle" : entity.movementType === MOVEMENT_TYPE.ONCOMING ? "oncoming" : "groundObstacle", entity);',
        1,
        'air obstacle presentation classification',
    ),
    (
        '    groundObstacle: Math.max(0, safeInt(run.obstacleSpawnCount) - safeInt(run.oncomingSpawnCount)),\n    oncoming: safeInt(run.oncomingSpawnCount),',
        '    groundObstacle: Math.max(0, safeInt(run.obstacleSpawnCount) - safeInt(run.oncomingSpawnCount)),\n    airObstacle: safeInt(run.airObstacleSpawnCount),\n    oncoming: safeInt(run.oncomingSpawnCount),',
        1,
        'generated air obstacle',
    ),
    (
        '    groundObstacle: metrics.groundObstacle.count,\n    oncoming: metrics.oncoming.count,',
        '    groundObstacle: metrics.groundObstacle.count,\n    airObstacle: metrics.airObstacle.count,\n    oncoming: metrics.oncoming.count,',
        1,
        'presented air obstacle',
    ),
    (
        '    strongHazard: "A visible hole or active ground/oncoming obstacle intersecting the canvas.",',
        '    strongHazard: "A visible hole or active ground/oncoming/air obstacle intersecting the canvas.",',
        1,
        'definition',
    ),
]

for old, new, expected, label in replacements:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f'{label}: expected {expected}, got {count}')
    text = text.replace(old, new, expected)

path.write_text(text)
print('P4 effective presentation metrics updated')
