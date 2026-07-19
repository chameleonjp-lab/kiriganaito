from pathlib import Path

path = Path('tests/p4-air-obstacle-regression.js')
text = path.read_text()

old_state = '''  let maxSimultaneousGroundAndAir = 0;
  let frames = 0;'''
new_state = '''  let maxSimultaneousGroundAndAir = 0;
  let firstOverlap = null;
  let frames = 0;'''
if text.count(old_state) != 1:
    raise SystemExit(f'P4 diagnostic state: expected 1, got {text.count(old_state)}')
text = text.replace(old_state, new_state, 1)

old_pair = '''        if (air.x < ground.x + ground.w && air.x + air.w > ground.x) horizontalBlockPairs++;'''
new_pair = '''        if (air.x < ground.x + ground.w && air.x + air.w > ground.x) {
          horizontalBlockPairs++;
          if (!firstOverlap) {
            firstOverlap = {
              km: run.runMeters / 1000,
              elapsed: run.elapsed,
              air: { x: air.x, w: air.w, speed: air.speed, airKind: air.airKind, source: air.spawnSource },
              ground: {
                x: ground.x,
                w: ground.w,
                zone: ground.zone,
                kind: ground.kind,
                emoji: ground.emoji,
                direction: ground.direction,
                speed: ground.speed,
                source: ground.spawnSource,
                patternName: ground.patternName,
                patternStep: ground.patternStep,
              },
            };
          }
        }'''
if text.count(old_pair) != 1:
    raise SystemExit(f'P4 diagnostic pair: expected 1, got {text.count(old_pair)}')
text = text.replace(old_pair, new_pair, 1)

old_report = '''    maxSimultaneousGroundAndAir,
    queueOverflow: run.spawnQueueOverflowCount,'''
new_report = '''    maxSimultaneousGroundAndAir,
    firstOverlap,
    queueOverflow: run.spawnQueueOverflowCount,'''
if text.count(old_report) != 1:
    raise SystemExit(f'P4 diagnostic report: expected 1, got {text.count(old_report)}')
text = text.replace(old_report, new_report, 1)

path.write_text(text)
print('P4 first horizontal overlap diagnostics added')
