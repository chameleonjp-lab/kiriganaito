from pathlib import Path

path = Path('index.html')
text = path.read_text()

if text.count('        SCROLL_PX: 190,') != 1:
    raise SystemExit(f'P4 fast scroll constant: expected 1, got {text.count("        SCROLL_PX: 190,")}')
text = text.replace('        SCROLL_PX: 190,', '        SCROLL_PX: 360,', 1)

old_corridor = '''      function isGroundHazardNearAirCorridor(airX = -P4_AIR.WIDTH - 18, airWidth = P4_AIR.WIDTH) {
        const left = airX - 18;
        const right = airX + airWidth + 18;
        const groundObstacle = obstacles.some((entity) =>
          entity.active !== false && entity.zone === WORLD_ZONE.GROUND && entity.objectRole === OBJECT_ROLE.HAZARD &&
          entity.x + entity.w > left && entity.x < right
        );
        const hole = holes.some((entity) => entity.x + entity.w > left && entity.x < right);
        return groundObstacle || hole;
      }'''
new_corridor = '''      function isGroundHazardNearAirCorridor(airX = P4_AIR.SPAWN_X, airWidth = P4_AIR.WIDTH) {
        const left = airX - 18;
        const right = player.x + 80;
        const groundObstacle = obstacles.some((entity) =>
          entity.active !== false && entity.zone === WORLD_ZONE.GROUND && entity.objectRole === OBJECT_ROLE.HAZARD &&
          entity.x + entity.w > left && entity.x < right
        );
        const hole = holes.some((entity) => entity.x + entity.w > left && entity.x < right);
        return groundObstacle || hole;
      }'''
if text.count(old_corridor) != 1:
    raise SystemExit(f'P4 protected approach corridor: expected 1, got {text.count(old_corridor)}')
text = text.replace(old_corridor, new_corridor, 1)

path.write_text(text)
print('P4 protected fast-pass corridor applied')
