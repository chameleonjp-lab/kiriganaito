from pathlib import Path

path = Path('index.html')
text = path.read_text()
old = '        const crowd = obstacles.filter(o => o.active && o.x > -40 && o.x < W + 90).length + holes.filter(h => h.x > -60 && h.x < W + 90).length;'
new = '        const crowd = obstacles.filter(o => o.active && o.zone !== WORLD_ZONE.AIR && o.x > -40 && o.x < W + 90).length + holes.filter(h => h.x > -60 && h.x < W + 90).length;'
if text.count(old) != 1:
    raise SystemExit(f'oncoming ground crowd metric: expected 1, got {text.count(old)}')
path.write_text(text.replace(old, new, 1))
print('P4 AIR excluded from ground/oncoming crowd metric')
