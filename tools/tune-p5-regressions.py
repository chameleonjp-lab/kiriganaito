from pathlib import Path

path = Path('tests/effective-presentation-metrics.js')
text = path.read_text()

old_chase = '''  const chase = advanceScenario(1800, SPAWN_SOURCE.CHASE, () => {
    run.runMeters = 2500;
    run.maxRunMeters = 2500;
    run.lastNonZeroRunMeters = 2500;
    run.chase = 15;
    run.elapsed = 2;
    spawn.chaseGraceUntil = 0;
    spawn.nextChaseEventAt = 0;
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
  });'''
new_chase = '''  const chase = advanceScenario(1800, SPAWN_SOURCE.CHASE, () => {
    run.runMeters = 2500;
    run.maxRunMeters = 2500;
    run.lastNonZeroRunMeters = 2500;
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
    spawn.nextHoleAt = 99;
    spawn.nextObstacleAt = 99;
    spawn.nextOncomingAt = 99;
    spawn.nextScoreItemAt = 99;
    spawn.nextItemAt = 99;
    startP5ChaseSession(2.5);
    run.chase = 13.90;
  });'''

old_invincible = '''  const invincible = advanceScenario(600, SPAWN_SOURCE.INVINCIBLE, () => {
    run.runMeters = 2500;
    run.maxRunMeters = 2500;
    run.lastNonZeroRunMeters = 2500;
    run.dancerInvincibleUntil = performance.now() + 4000;
    run.forceObstacleDuringInvincibleUntil = performance.now() + 4000;
    run.invincibleObstaclePlanCount = 3;
    run.invincibleObstacleSpawned = 0;
    spawn.nextObstacleAt = 2.5;
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
  });'''
new_invincible = '''  const invincible = advanceScenario(600, SPAWN_SOURCE.INVINCIBLE, () => {
    run.runMeters = 2500;
    run.maxRunMeters = 2500;
    run.lastNonZeroRunMeters = 2500;
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
    spawn.nextHoleAt = 99;
    spawn.nextObstacleAt = 99;
    spawn.nextOncomingAt = 99;
    spawn.nextScoreItemAt = 99;
    spawn.nextItemAt = 99;
    activateDancerInvincible();
    run.invincibleObstaclePlanCount = 3;
    spawn.nextInvincibleObstacleAt = run.elapsed;
  });'''

for old, new, label in [
    (old_chase, new_chase, 'P1 chase source scenario'),
    (old_invincible, new_invincible, 'P1 invincible source scenario'),
]:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1, got {count}')
    text = text.replace(old, new, 1)

path.write_text(text)
print('P1 source scenarios updated for P5 APIs')
