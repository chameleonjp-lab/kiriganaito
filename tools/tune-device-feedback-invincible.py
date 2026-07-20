from pathlib import Path

path = Path('index.html')
text = path.read_text()
old = '''        if (!chase && isDancerInvincible() && run.invincibleSessionPresentedObstacleCount < run.invincibleObstaclePlanCount && run.elapsed >= spawn.nextInvincibleObstacleAt && !hasPendingInvincibleRequest()) {'''
new = '''        if (!chase && isDancerInvincible() && Math.max(safeInt(run.invincibleSessionPresentedObstacleCount), safeInt(run.invincibleObstacleSpawned)) < run.invincibleObstaclePlanCount && run.elapsed >= spawn.nextInvincibleObstacleAt && !hasPendingInvincibleRequest()) {'''
count = text.count(old)
if count != 1:
    raise SystemExit(f'invincible request cap: expected 1, got {count}')
path.write_text(text.replace(old, new, 1))
print('8-second invincibility request cap applied')
