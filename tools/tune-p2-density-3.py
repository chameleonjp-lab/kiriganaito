from pathlib import Path

index_path = Path("index.html")
index = index_path.read_text()

old_fallback = '''        } else if (req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE || req.kind === SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE) {
          if (req.fallbackStage === 1) { req.kind = SPAWN_REQUEST_KIND.GROUND_OBSTACLE; req.payload.dir = -1; req.payload.emoji = "🚶"; req.payload.x = -44; }
          else return false;
        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) {'''
new_fallback = '''        } else if (req.kind === SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE) {
          if (req.fallbackStage <= 2) {
            req.kind = SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE;
            req.payload.dir = 1;
            req.payload.emoji = "🚶";
            req.payload.x = getOncomingSpawnX(km);
          } else return false;
        } else if (req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE) {
          if (req.fallbackStage === 1) { req.kind = SPAWN_REQUEST_KIND.GROUND_OBSTACLE; req.payload.dir = -1; req.payload.emoji = "🚶"; req.payload.x = -44; }
          else return false;
        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) {'''
if old_fallback not in index:
    raise SystemExit("normal oncoming fallback block missing")
index = index.replace(old_fallback, new_fallback, 1)

index_path.write_text(index)
