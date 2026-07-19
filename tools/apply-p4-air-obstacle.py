from pathlib import Path

ROOT = Path('.')
INDEX = ROOT / 'index.html'
SPEC = ROOT / 'SPEC.md'
REPORT = ROOT / 'TEST_REPORT.md'
OLD_VERSION = 'kiriganaito-2026-07-19-v19-decision-patterns'
NEW_VERSION = 'kiriganaito-2026-07-20-v20-air-obstacle'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    return text.replace(old, new, 1)


index = INDEX.read_text()
index = index.replace(OLD_VERSION, NEW_VERSION)

index = replace_once(
    index,
    '        ONCOMING_OBSTACLE: "oncoming_obstacle",\n        SCORE_ITEM: "score_item",',
    '        ONCOMING_OBSTACLE: "oncoming_obstacle",\n        AIR_OBSTACLE: "air_obstacle",\n        SCORE_ITEM: "score_item",',
    'spawn request kind',
)

index = replace_once(
    index,
    '      const P3_PATTERN_DEFS = Object.freeze([',
    '''      const P4_AIR = Object.freeze({
        MIN_KM: 2,
        FIRST_MIN_KM: 2.20,
        FIRST_MAX_KM: 2.55,
        INTERVAL_MIN_KM: 0.90,
        INTERVAL_MAX_KM: 1.30,
        WIDTH: 58,
        HEIGHT: 24,
        Y_OFFSET: 76,
        MIN_GROUND_CLEARANCE_PX: 12,
        GROUND_BEFORE_KM: 0.16,
        GROUND_AFTER_KM: 0.16,
        HOLE_BEFORE_KM: 0.18,
        HOLE_AFTER_KM: 0.18,
        ONCOMING_BEFORE_KM: 0.20,
        ONCOMING_AFTER_KM: 0.20,
        VISIBLE_CLEAR_LEFT_PX: -150,
        VISIBLE_CLEAR_RIGHT_PX: 120,
      });
      const P3_PATTERN_DEFS = Object.freeze([''',
    'P4 constants',
)

index = replace_once(
    index,
    '          obstacleSpawnCount: 0,\n          oncomingSpawnCount: 0,',
    '''          obstacleSpawnCount: 0,
          airObstacleSpawnCount: 0,
          airObstacleContactCount: 0,
          airObstacleGroundSafePassCount: 0,
          airObstacleFullBlockViolationCount: 0,
          airObstacleBefore2kmCount: 0,
          airObstacleChaseSpawnCount: 0,
          airObstacleFirstSpawnKm: -1,
          oncomingSpawnCount: 0,''',
    'run air counters',
)

index = replace_once(
    index,
    '          nextOncomingAt: 0.9 + rand(0, 0.2),\n          chaseGraceUntil: 0,',
    '''          nextOncomingAt: 0.9 + rand(0, 0.2),
          nextAirObstacleAt: rand(P4_AIR.FIRST_MIN_KM, P4_AIR.FIRST_MAX_KM),
          lastAirObstacleAt: -9,
          chaseGraceUntil: 0,''',
    'spawn air schedule',
)

index = replace_once(
    index,
    '      function canSpawnItem(km) {',
    '''      function nextAirObstacleInterval() {
        return rand(P4_AIR.INTERVAL_MIN_KM, P4_AIR.INTERVAL_MAX_KM);
      }
      function airObstacleGroundClearancePx(entity = null) {
        const y = entity && Number.isFinite(entity.y) ? entity.y : groundY - P4_AIR.Y_OFFSET;
        const h = entity && Number.isFinite(entity.h) ? entity.h : P4_AIR.HEIGHT;
        const obstacleBottom = y + h - 3;
        const groundPlayerTop = groundY - player.h + HIT.PLAYER_SHRINK_TOP;
        return groundPlayerTop - obstacleBottom;
      }
      function isGroundHazardNearAirCorridor() {
        const left = P4_AIR.VISIBLE_CLEAR_LEFT_PX;
        const right = W + P4_AIR.VISIBLE_CLEAR_RIGHT_PX;
        const groundObstacle = obstacles.some((entity) =>
          entity.active !== false && entity.zone === WORLD_ZONE.GROUND && entity.objectRole === OBJECT_ROLE.HAZARD &&
          entity.x + entity.w > left && entity.x < right
        );
        const hole = holes.some((entity) => entity.x + entity.w > left && entity.x < right);
        return groundObstacle || hole;
      }
      function isAirObstacleReservationActive(km) {
        if (!run || !spawn || km < P4_AIR.MIN_KM) return false;
        if (run.chase > 0 || isDancerInvincible() || spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        return km >= spawn.nextAirObstacleAt || hasPendingSpawnRequestKind(SPAWN_REQUEST_KIND.AIR_OBSTACLE);
      }
      function canSpawnAirObstacle(km) {
        if (km < P4_AIR.MIN_KM || run.chase > 0 || isDancerInvincible()) return false;
        if (spawn.needObstacleBeforeNextHole || isDecisionPatternReservationActive()) return false;
        if (isGroundHazardNearAirCorridor()) return false;
        if (km - spawn.lastHoleAt < P4_AIR.HOLE_BEFORE_KM) return false;
        if (km - spawn.lastObstacleAt < P4_AIR.GROUND_BEFORE_KM) return false;
        if (km - spawn.lastOncomingAt < P4_AIR.ONCOMING_BEFORE_KM) return false;
        return airObstacleGroundClearancePx() >= P4_AIR.MIN_GROUND_CLEARANCE_PX;
      }
      function scheduleNextAirObstacle(km) {
        spawn.nextAirObstacleAt = km + nextAirObstacleInterval();
      }
      function spawnAirObstaclePattern(km, opt = {}) {
        if (!canSpawnAirObstacle(km)) return false;
        const entity = {
          x: opt.x ?? -P4_AIR.WIDTH - 18,
          y: opt.y ?? groundY - P4_AIR.Y_OFFSET,
          w: P4_AIR.WIDTH,
          h: P4_AIR.HEIGHT,
          active: true,
          direction: -1,
          speed: 0,
          emoji: "",
          airKind: "hanging_bar",
          zone: WORLD_ZONE.AIR,
          movementType: MOVEMENT_TYPE.WORLD_SCROLL,
          objectRole: OBJECT_ROLE.HAZARD,
          heightBand: HEIGHT_BAND.MID,
          spawnSource: opt.spawnSource || SPAWN_SOURCE.NORMAL,
          groundSafeCounted: false,
        };
        if (airObstacleGroundClearancePx(entity) < P4_AIR.MIN_GROUND_CLEARANCE_PX) return false;
        if (isGroundHazardNearAirCorridor()) run.airObstacleFullBlockViolationCount = safeInt(run.airObstacleFullBlockViolationCount) + 1;
        obstacles.push(entity);
        spawn.lastAirObstacleAt = km;
        spawn.lastDangerAt = km;
        spawn.nextObstacleAt = Math.max(spawn.nextObstacleAt, km + P4_AIR.GROUND_AFTER_KM);
        spawn.nextHoleAt = Math.max(spawn.nextHoleAt, km + P4_AIR.HOLE_AFTER_KM);
        spawn.nextOncomingAt = Math.max(spawn.nextOncomingAt, km + P4_AIR.ONCOMING_AFTER_KM);
        return true;
      }
      function canSpawnItem(km) {''',
    'air helper functions',
)

index = replace_once(
    index,
    '        if (entity.objectRole === OBJECT_ROLE.HAZARD) {\n          run.obstacleSpawnCount++;',
    '''        if (entity.objectRole === OBJECT_ROLE.HAZARD && entity.zone === WORLD_ZONE.AIR) {
          run.airObstacleSpawnCount = safeInt(run.airObstacleSpawnCount) + 1;
          if (run.airObstacleFirstSpawnKm < 0) run.airObstacleFirstSpawnKm = km;
          if (km < P4_AIR.MIN_KM) run.airObstacleBefore2kmCount = safeInt(run.airObstacleBefore2kmCount) + 1;
          if (run.chase > 0) run.airObstacleChaseSpawnCount = safeInt(run.airObstacleChaseSpawnCount) + 1;
        }
        if (entity.objectRole === OBJECT_ROLE.HAZARD && entity.zone !== WORLD_ZONE.AIR) {
          run.obstacleSpawnCount++;''',
    'air success counters',
)

index = replace_once(
    index,
    '        const forceEarlyOncoming = (earlyOncomingDue || (km >= 2 && !run.earlyOncomingSpawned));\n        collectDecisionPatternRequests(km);',
    '''        const forceEarlyOncoming = (earlyOncomingDue || (km >= 2 && !run.earlyOncomingSpawned));
        const dueAirObstacle = km >= spawn.nextAirObstacleAt;
        collectDecisionPatternRequests(km);''',
    'air due',
)

index = replace_once(
    index,
    '        const reserveOncoming = isOncomingReservationActive(km);\n        const suppressNormalGround = spawn.needObstacleBeforeNextHole || reservePattern || reserveHole || reserveScoreItem;',
    '''        const reserveOncoming = isOncomingReservationActive(km);
        const reserveAirObstacle = isAirObstacleReservationActive(km);
        const suppressNormalGround = spawn.needObstacleBeforeNextHole || reservePattern || reserveHole || reserveScoreItem || reserveAirObstacle;''',
    'air reservation',
)

index = replace_once(
    index,
    '        if (isDancerInvincible() && run.invincibleObstacleSpawned < run.invincibleObstaclePlanCount && km >= spawn.nextObstacleAt) {',
    '''        if (dueAirObstacle && reserveAirObstacle && canSpawnAirObstacle(km)) {
          const key = "air-obstacle:" + spawn.nextAirObstacleAt.toFixed(4);
          enqueueSpawnRequestIfNew(
            WORLD_ZONE.AIR,
            SPAWN_REQUEST_KIND.AIR_OBSTACLE,
            SPAWN_SOURCE.NORMAL,
            km,
            key,
            () => ({ x: -P4_AIR.WIDTH - 18 }),
            SPAWN_REQUEST_KIND.AIR_OBSTACLE
          );
        }
        if (isDancerInvincible() && run.invincibleObstacleSpawned < run.invincibleObstaclePlanCount && km >= spawn.nextObstacleAt) {''',
    'air enqueue',
)

index = replace_once(
    index,
    '        if (dueHole && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {',
    '        if (dueHole && !reservePattern && !reserveAirObstacle && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {',
    'air hole deferral',
)

index = replace_once(
    index,
    '        if (req && req.spawnSource === SPAWN_SOURCE.PATTERN) return false;\n        if (isDecisionPatternReservationActive()',
    '''        if (req && req.spawnSource === SPAWN_SOURCE.PATTERN) return false;
        if (req && req.kind !== SPAWN_REQUEST_KIND.AIR_OBSTACLE && isAirObstacleReservationActive(km)) {
          if (req.kind === SPAWN_REQUEST_KIND.HOLE || isNonMandatoryGroundRequest(req)) return true;
        }
        if (isDecisionPatternReservationActive()''',
    'air request deferral',
)

index = replace_once(
    index,
    '        if (req.kind === SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE && req.spawnSource === SPAWN_SOURCE.NORMAL) scheduleNext("oncoming", km, d);\n        if (req.spawnSource === SPAWN_SOURCE.CHASE)',
    '''        if (req.kind === SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE && req.spawnSource === SPAWN_SOURCE.NORMAL) scheduleNext("oncoming", km, d);
        if (req.kind === SPAWN_REQUEST_KIND.AIR_OBSTACLE) scheduleNextAirObstacle(km);
        if (req.spawnSource === SPAWN_SOURCE.CHASE)''',
    'air schedule resolution',
)

index = replace_once(
    index,
    '        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) {',
    '''        } else if (req.kind === SPAWN_REQUEST_KIND.AIR_OBSTACLE) {
          if (req.fallbackStage === 1) {
            req.payload.x = -P4_AIR.WIDTH - 18;
          } else return false;
        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) {''',
    'air fallback',
)

index = replace_once(
    index,
    '        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) ok = canSpawnItem(km) && spawnItemPattern',
    '''        } else if (req.kind === SPAWN_REQUEST_KIND.AIR_OBSTACLE) {
          ok = spawnAirObstaclePattern(km, Object.assign({}, req.payload, { spawnSource: req.spawnSource }));
        } else if (req.kind === SPAWN_REQUEST_KIND.SCORE_ITEM) ok = canSpawnItem(km) && spawnItemPattern''',
    'air resolve',
)

index = replace_once(
    index,
    '          let o = obstacles[i];\n          let relPx =',
    '''          let o = obstacles[i];
          const previousX = o.x;
          let relPx =''',
    'air pass previous x',
)

index = replace_once(
    index,
    '          o.x += relPx * getSpeedMultiplierByKm((run.maxRunMeters || run.runMeters || 0) / 1000) * (run.chase > 0 ? CHASE_MULT : 1) * dt;\n          if (o.x > W + 70 || !o.active) obstacles.splice(i, 1);',
    '''          o.x += relPx * getSpeedMultiplierByKm((run.maxRunMeters || run.runMeters || 0) / 1000) * (run.chase > 0 ? CHASE_MULT : 1) * dt;
          if (o.zone === WORLD_ZONE.AIR && !o.groundSafeCounted && previousX <= player.x && o.x > player.x) {
            o.groundSafeCounted = true;
            if (player.onGround) run.airObstacleGroundSafePassCount = safeInt(run.airObstacleGroundSafePassCount) + 1;
          }
          if (o.x > W + 70 || !o.active) obstacles.splice(i, 1);''',
    'air pass counter',
)

index = replace_once(
    index,
    '      function obstacleRect(o) {\n        const topShrink = HIT.OBSTACLE_SHRINK + (o.emoji === "🚴" ? BIKE_SHRINK_TOP_EXTRA : 0);',
    '''      function obstacleRect(o) {
        if (o.zone === WORLD_ZONE.AIR) {
          return { x: o.x + 4, y: o.y + 3, w: o.w - 8, h: o.h - 6 };
        }
        const topShrink = HIT.OBSTACLE_SHRINK + (o.emoji === "🚴" ? BIKE_SHRINK_TOP_EXTRA : 0);''',
    'air obstacle rect',
)

index = replace_once(
    index,
    '          if (rects(pr, obstacleRect(o))) {\n            if (isDancerInvincible()) {',
    '''          if (rects(pr, obstacleRect(o))) {
            if (o.zone === WORLD_ZONE.AIR) run.airObstacleContactCount = safeInt(run.airObstacleContactCount) + 1;
            if (isDancerInvincible()) {''',
    'air collision counter',
)

index = replace_once(
    index,
    '''          if (o.direction === 1) {
            ctx.translate(o.x + 16, o.y + 16);
            ctx.scale(-1, 1);
            ctx.fillText(o.emoji, 0, 0);
          } else ctx.fillText(o.emoji, o.x + 16, o.y + 16);''',
    '''          if (o.zone === WORLD_ZONE.AIR) {
            ctx.strokeStyle = "rgba(210,220,240,0.72)";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(o.x + 8, Math.max(0, o.y - 34));
            ctx.lineTo(o.x + 8, o.y + 2);
            ctx.moveTo(o.x + o.w - 8, Math.max(0, o.y - 34));
            ctx.lineTo(o.x + o.w - 8, o.y + 2);
            ctx.stroke();
            ctx.fillStyle = "#252a35";
            ctx.fillRect(o.x, o.y, o.w, o.h);
            ctx.fillStyle = "#f2c84b";
            for (let stripe = 3; stripe < o.w - 5; stripe += 12) ctx.fillRect(o.x + stripe, o.y + 4, 6, o.h - 8);
            ctx.strokeStyle = "rgba(255,245,178,0.9)";
            ctx.lineWidth = 2;
            ctx.strokeRect(o.x + 1, o.y + 1, o.w - 2, o.h - 2);
            ctx.globalAlpha = 0.22;
            ctx.fillStyle = "#05070b";
            ctx.beginPath();
            ctx.ellipse(o.x + o.w / 2, getGroundY(o.x + o.w / 2) + 6, o.w * 0.42, 5, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1;
          } else if (o.direction === 1) {
            ctx.translate(o.x + 16, o.y + 16);
            ctx.scale(-1, 1);
            ctx.fillText(o.emoji, 0, 0);
          } else ctx.fillText(o.emoji, o.x + 16, o.y + 16);''',
    'air drawing',
)

index = replace_once(
    index,
    '          obstacleSpawnCount: run.obstacleSpawnCount || 0,\n          oncomingSpawnCount: run.oncomingSpawnCount || 0,',
    '''          obstacleSpawnCount: run.obstacleSpawnCount || 0,
          airObstacleSpawnCount: safeInt(run.airObstacleSpawnCount),
          airObstacleContactCount: safeInt(run.airObstacleContactCount),
          airObstacleGroundSafePassCount: safeInt(run.airObstacleGroundSafePassCount),
          airObstacleFullBlockViolationCount: safeInt(run.airObstacleFullBlockViolationCount),
          airObstacleBefore2kmCount: safeInt(run.airObstacleBefore2kmCount),
          airObstacleChaseSpawnCount: safeInt(run.airObstacleChaseSpawnCount),
          airObstacleFirstSpawnKm: safeNumber(run.airObstacleFirstSpawnKm, -1),
          oncomingSpawnCount: run.oncomingSpawnCount || 0,''',
    'air result snapshot',
)

INDEX.write_text(index)

for path in [SPEC, REPORT, ROOT / 'tests/release-comprehensive.js', ROOT / 'tests/p1-effective-presentation.js', ROOT / 'tests/effective-presentation-metrics.js', ROOT / 'tests/p2-density-regression.js', ROOT / 'tests/p3-pattern-regression.js']:
    if path.exists():
        path.write_text(path.read_text().replace(OLD_VERSION, NEW_VERSION))

spec = SPEC.read_text()
if '## v20 P4 空中障害物' not in spec:
    spec += '''\n\n## v20 P4 空中障害物\n\n- 2km以降へ低頻度の吊り下げバーを1種類追加する。\n- `AIR / HAZARD / MID / NORMAL` のmetadataを持つ。\n- 地上走行は安全で、通常ジャンプ中は接触する。\n- 逃走中、無敵中、P3 pattern中、穴間必須障害物待ちには新規生成しない。\n- AIR queueの`AIR_OBSTACLE` requestとして管理する。\n- 空中障害物成功後は地上0.16km、穴0.18km、対向0.20kmの安全区間を予約する。\n- P2/P3密度、安全距離、TTC、スコア、ランキング連携は変更しない。\n'''
SPEC.write_text(spec)

report = REPORT.read_text()
if '## v20 P4 空中障害物' not in report:
    report += '''\n\n## v20 P4 空中障害物\n\n- Canvas図形の吊り下げバーを1種類追加。\n- 2km以降の低頻度、逃走・無敵・P3 pattern中は出現禁止。\n- 地上クリアランス12px以上、通常ジャンプ中は接触可能。\n- 1,000配置の完全封鎖検査と自然走行固定seed検査を追加。\n- P1/P2/P3、progressive、release、150km耐久を回帰ゲートとして維持する。\n'''
REPORT.write_text(report)

print('P4 implementation patch applied')
