from pathlib import Path

path = Path('tests/p5-chase-invincible-regression.js')
text = path.read_text()
old = '''    for (const entity of obstacles) {
      if (entity.spawnSource !== SPAWN_SOURCE.INVINCIBLE || seen.has(entity)) continue;
      const width = Math.max(1, Number(entity.w) || 1);'''
new = '''    for (const entity of obstacles) {
      if (entity.p5InvincibleSessionId !== run.invincibleSessionId || seen.has(entity)) continue;
      const width = Math.max(1, Number(entity.w) || 1);'''
count = text.count(old)
if count != 1:
    raise SystemExit(f'P5 visible invincible session condition: expected 1, got {count}')
path.write_text(text.replace(old, new, 1))
print('P5 invincible presentation test counts every visible session hazard')
