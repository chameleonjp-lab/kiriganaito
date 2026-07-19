from pathlib import Path

index_path = Path('index.html')
index = index_path.read_text()
old = '''        GROUND_BEFORE_KM: 0.09,
        GROUND_AFTER_KM: 0.11,
        HOLE_BEFORE_KM: 0.10,
        HOLE_AFTER_KM: 0.14,
        ONCOMING_BEFORE_KM: 0.12,
        ONCOMING_AFTER_KM: 0.14,'''
new = '''        GROUND_BEFORE_KM: 0.09,
        GROUND_AFTER_KM: 0.012,
        HOLE_BEFORE_KM: 0.10,
        HOLE_AFTER_KM: 0.012,
        ONCOMING_BEFORE_KM: 0.12,
        ONCOMING_AFTER_KM: 0.020,'''
if index.count(old) != 1:
    raise SystemExit(f'P4 post-gap constants: expected 1, got {index.count(old)}')
index_path.write_text(index.replace(old, new, 1))

metrics_path = Path('tests/effective-presentation-metrics.js')
metrics = metrics_path.read_text()
old_metric = '      if (entity.active !== false && entity.x < W && entity.x + (entity.w || 0) > 0) simultaneousHazards += 1;'
new_metric = '      if (entity.active !== false && entity.zone !== WORLD_ZONE.AIR && entity.x < W && entity.x + (entity.w || 0) > 0) simultaneousHazards += 1;'
if metrics.count(old_metric) != 1:
    raise SystemExit(f'P2 strong ground hazard metric: expected 1, got {metrics.count(old_metric)}')
metrics_path.write_text(metrics.replace(old_metric, new_metric, 1))

print('P4 minimal post-spacing and P2 ground-hazard metric applied')
