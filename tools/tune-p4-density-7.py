from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text()
old_const = '''        Y_OFFSET: 76,
        SPAWN_X: -190,'''
new_const = '''        Y_OFFSET: 76,
        SPAWN_X: -190,
        SCROLL_PX: 190,'''
if index.count(old_const) != 1:
    raise SystemExit(f'P4 scroll constant: expected 1, got {index.count(old_const)}')
index = index.replace(old_const, new_const, 1)

old_move = '''          let relPx =
            o.direction === 1
              ? (BASE_SPEED + o.speed) * 42
              : STATIC_OBSTACLE_SCROLL_PX;'''
new_move = '''          let relPx =
            o.zone === WORLD_ZONE.AIR
              ? P4_AIR.SCROLL_PX
              : o.direction === 1
                ? (BASE_SPEED + o.speed) * 42
                : STATIC_OBSTACLE_SCROLL_PX;'''
if index.count(old_move) != 1:
    raise SystemExit(f'P4 air movement branch: expected 1, got {index.count(old_move)}')
index_path.write_text(index.replace(old_move, new_move, 1))

p4_test_path = Path('tests/p4-air-obstacle-regression.js')
p4_test = p4_test_path.read_text()
replacements = [
    ('  holes.push({ x: -80, prevX: -80,', '  holes.push({ x: P4_AIR.SPAWN_X + 10, prevX: P4_AIR.SPAWN_X + 10,', 'direct hole conflict'),
    ('  obstacles.push({ x: -60, y: groundY - 32,', '  obstacles.push({ x: P4_AIR.SPAWN_X + 10, y: groundY - 32,', 'direct ground conflict'),
]
for old, new, label in replacements:
    if p4_test.count(old) != 1:
        raise SystemExit(f'{label}: expected 1, got {p4_test.count(old)}')
    p4_test = p4_test.replace(old, new, 1)
p4_test_path.write_text(p4_test)

print('P4 rear obstacle speed made slower than every ground hazard')
