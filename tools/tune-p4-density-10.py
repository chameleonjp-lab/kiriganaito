from pathlib import Path

path = Path('index.html')
text = path.read_text()
old = '''      function decisionPatternSymbolForEntity(entity) {
        if (!entity) return "";
        if (entity.zone === WORLD_ZONE.HOLE) return "H";'''
new = '''      function decisionPatternSymbolForEntity(entity) {
        if (!entity) return "";
        if (entity.zone === WORLD_ZONE.AIR && entity.objectRole === OBJECT_ROLE.HAZARD) return "";
        if (entity.zone === WORLD_ZONE.HOLE) return "H";'''
if text.count(old) != 1:
    raise SystemExit(f'P3 AIR adoption exclusion: expected 1, got {text.count(old)}')
path.write_text(text.replace(old, new, 1))
print('P4 AIR excluded from P3 ground-pattern adoption')
