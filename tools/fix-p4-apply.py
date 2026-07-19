from pathlib import Path

path = Path('tools/apply-p4-air-obstacle.py')
text = path.read_text()

replace_once_old = """    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, got {count}')\n    return text.replace(old, new, 1)\n"""
replace_once_new = """    if label == 'air fallback' and count == 2:\n        return text.replace(old, new, 1)\n    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, got {count}')\n    return text.replace(old, new, 1)\n"""
if replace_once_old not in text:
    raise SystemExit('replace_once body not found')
text = text.replace(replace_once_old, replace_once_new, 1)

resolve_old = '''index = replace_once(
    index,
    '        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) ok = canSpawnItem(km) && spawnItemPattern',
    ''' + "'''" + '''        } else if (req.kind === SPAWN_REQUEST_KIND.AIR_OBSTACLE) {
          ok = spawnAirObstaclePattern(km, Object.assign({}, req.payload, { spawnSource: req.spawnSource }));
        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) ok = canSpawnItem(km) && spawnItemPattern''' + "'''" + ''',
    'air resolve',
)
'''
resolve_new = '''index = replace_once(
    index,
    ''' + "'''" + '''        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) {
          const itemPlacementAllowed = req.patternAllowsItemPlacement === true || canSpawnItem(km);''' + "'''" + ''',
    ''' + "'''" + '''        } else if (req.kind === SPAWN_REQUEST_KIND.AIR_OBSTACLE) {
          ok = spawnAirObstaclePattern(km, Object.assign({}, req.payload, { spawnSource: req.spawnSource }));
        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) {
          const itemPlacementAllowed = req.patternAllowsItemPlacement === true || canSpawnItem(km);''' + "'''" + ''',
    'air resolve',
)
'''
if resolve_old not in text:
    raise SystemExit('air resolve patch block not found')
text = text.replace(resolve_old, resolve_new, 1)

path.write_text(text)
print('P4 apply script matchers fixed')
