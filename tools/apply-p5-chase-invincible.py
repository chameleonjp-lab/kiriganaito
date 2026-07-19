from pathlib import Path

ROOT = Path('.')
INDEX = ROOT / 'index.html'
SPEC = ROOT / 'SPEC.md'
REPORT = ROOT / 'TEST_REPORT.md'
OLD_VERSION = 'kiriganaito-2026-07-20-v20-air-obstacle'
NEW_VERSION = 'kiriganaito-2026-07-20-v21-chase-invincible'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    return text.replace(old, new, 1)


index = INDEX.read_text().replace(OLD_VERSION, NEW_VERSION)

index = replace_once(
    index,
    '''      const P3_PATTERN_DEFS = Object.freeze([''',
    '''      const P5_CHASE_PHASE = Object.freeze({
        IDLE: "idle",
        GRACE: "grace",
        GROUND_REWARD: "ground_reward",
        MIXED: "mixed",
        FINALE: "finale",
      });
      const P5_CHASE = Object.freeze({
        GRACE_END_SEC: 1,
        GROUND_REWARD_END_SEC: 6,
        MIXED_END_SEC: 12,
        END_SEC: 15,
        LARGE_HOLE_BLOCK_KM: 0.14,
        INVINCIBLE_DURATION_SEC: 4,
        INVINCIBLE_REQUEST_GAP_SEC: 0.72,
        EVENTS: Object.freeze([
          { at: 1.05, type: "score" },
          { at: 1.65, type: "ground" },
          { at: 2.30, type: "score" },
          { at: 2.95, type: "ground" },
          { at: 3.60, type: "score" },
          { at: 4.25, type: "ground" },
          { at: 4.90, type: "score" },
          { at: 5.55, type: "ground" },
          { at: 6.20, type: "hole" },
          { at: 6.85, type: "score" },
          { at: 7.50, type: "oncoming" },
          { at: 8.20, type: "hole" },
          { at: 8.90, type: "score" },
          { at: 9.60, type: "hole" },
          { at: 10.30, type: "oncoming" },
          { at: 12.15, type: "hole" },
          { at: 12.80, type: "score" },
          { at: 13.70, type: "oncoming" },
        ]),
      });
      const P3_PATTERN_DEFS = Object.freeze([''',
    'P5 constants',
)

index = replace_once(
    index,
    '''          dancerInvincible: 0,
          dancerInvincibleUntil: 0,
          forceObstacleDuringInvincibleUntil: 0,
          invincibleObstaclePlanCount: 0,
          invincibleObstacleSpawned: 0,
          invincibleObstacleSpawnCount: 0,
          invinciblePreventedAccidents: 0,''',
    '''          dancerInvincible: 0,
          dancerInvincibleUntil: 0,
          forceObstacleDuringInvincibleUntil: 0,
          invincibleSessionId: 0,
          invincibleSessionCount: 0,
          invincibleObstaclePlanCount: 0,
          invincibleObstacleSpawned: 0,
          invincibleObstacleSpawnCount: 0,
          invincibleSessionPresentedObstacleCount: 0,
          invinciblePresentedObstacleCount: 0,
          invincibleRequestIndex: 0,
          invinciblePreventedAccidents: 0,
          invincibleLargeHoleBlockUntilKm: -9,
          invincibleLargeHoleViolationCount: 0,
          invincibleBackgroundDecayViolationCount: 0,
          invincibleBreakthroughFlash: 0,''',
    'invincible run state',
)

index = replace_once(
    index,
    '''          chase: 0,
          elapsed: 0,''',
    '''          chase: 0,
          chaseSessionId: 0,
          chaseSessionCount: 0,
          chaseCompletedSessionCount: 0,
          chaseSessionActive: false,
          chaseElapsedSec: 0,
          chasePhase: P5_CHASE_PHASE.IDLE,
          chaseEventStatus: [],
          chaseSessionGroundCount: 0,
          chaseSessionHoleCount: 0,
          chaseSessionScoreItemCount: 0,
          chaseSessionOncomingCount: 0,
          chaseGroundPresentedCount: 0,
          chaseHolePresentedCount: 0,
          chaseScoreItemPresentedCount: 0,
          chaseOncomingPresentedCount: 0,
          chaseCurrentDecisionBlankSec: 0,
          chaseSessionMaxDecisionBlankSec: 0,
          chaseMaxDecisionBlankSec: 0,
          chaseGraceHazardViolationCount: 0,
          chaseCountRangeViolationCount: 0,
          chaseReached2Km: false,
          chaseSessionStartDancerSpawnCount: 0,
          chaseLastSessionSummary: null,
          elapsed: 0,''',
    'chase run state',
)

index = replace_once(
    index,
    '''          nextChaseEventAt: 999,
          oncomingRetryAt: 0,''',
    '''          nextChaseEventAt: 999,
          nextInvincibleObstacleAt: 999,
          oncomingRetryAt: 0,''',
    'spawn invincible schedule',
)

index = replace_once(
    index,
    '''      function activateDancerInvincible() {
        run.dancerInvincibleUntil = nowMs() + 4000;
        run.dancerInvincible = 4;
        run.forceObstacleDuringInvincibleUntil = nowMs() + 4000;
        run.invincibleObstaclePlanCount = 2 + (Math.random() < 0.45 ? 1 : 0);
        run.invincibleObstacleSpawned = 0;
        spawn.nextObstacleAt = Math.min(spawn.nextObstacleAt, run.runMeters / 1000 + rand(0.012, 0.026));
      }
      function getDancerInvincibleRemainingSec() {
        return Math.max(0, ((run && run.dancerInvincibleUntil || 0) - nowMs()) / 1000);
      }
      function isDancerInvincible() { return getDancerInvincibleRemainingSec() > 0; }''',
    '''      function activateDancerInvincible() {
        run.invincibleSessionId = safeInt(run.invincibleSessionId) + 1;
        run.invincibleSessionCount = safeInt(run.invincibleSessionCount) + 1;
        run.dancerInvincibleUntil = 0;
        run.dancerInvincible = P5_CHASE.INVINCIBLE_DURATION_SEC;
        run.forceObstacleDuringInvincibleUntil = 0;
        run.invincibleObstaclePlanCount = 2 + (Math.random() < 0.45 ? 1 : 0);
        run.invincibleObstacleSpawned = 0;
        run.invincibleSessionPresentedObstacleCount = 0;
        run.invincibleRequestIndex = 0;
        spawn.nextInvincibleObstacleAt = run.elapsed + 0.35;
      }
      function getDancerInvincibleRemainingSec() {
        return Math.max(0, safeNumber(run && run.dancerInvincible));
      }
      function isDancerInvincible() { return getDancerInvincibleRemainingSec() > 0; }
      function updateDancerInvincible(dt) {
        run.invincibleBreakthroughFlash = Math.max(0, safeNumber(run.invincibleBreakthroughFlash) - dt);
        const before = getDancerInvincibleRemainingSec();
        if (before <= 0) return;
        run.dancerInvincible = Math.max(0, before - dt);
        if (before > 0 && run.dancerInvincible <= 0) {
          const kmNow = (run.maxRunMeters || run.runMeters || 0) / 1000;
          run.invincibleLargeHoleBlockUntilKm = Math.max(safeNumber(run.invincibleLargeHoleBlockUntilKm, -9), kmNow + P5_CHASE.LARGE_HOLE_BLOCK_KM);
          spawn.nextInvincibleObstacleAt = 999;
        }
      }
      function normalizeHoleKindForP5(kind, km) {
        if (kind === "LARGE" && (isDancerInvincible() || km < safeNumber(run.invincibleLargeHoleBlockUntilKm, -9))) return "MEDIUM";
        return kind;
      }''',
    'play-time invincible',
)

index = replace_once(
    index,
    '''        player.inv = Math.max(0, player.inv - dt);
        run.dancerInvincible = getDancerInvincibleRemainingSec();''',
    '''        player.inv = Math.max(0, player.inv - dt);
        updateDancerInvincible(dt);''',
    'invincible update',
)

index = replace_once(
    index,
    '''        const beforeChase = run.chase;
        run.chase = Math.max(0, run.chase - dt);
        if (beforeChase > 0 && run.chase <= 0) run.escapedFlash = ESCAPED_FLASH_SEC;''',
    '''        updateP5ChaseState(dt);''',
    'chase update',
)

p5_helpers = '''      function getP5ChaseElapsedSec() {
        if (!run || !run.chaseSessionActive) return 0;
        return Math.max(0, P5_CHASE.END_SEC - safeNumber(run.chase));
      }
      function getP5ChasePhase(elapsed = getP5ChaseElapsedSec()) {
        if (!run || !run.chaseSessionActive) return P5_CHASE_PHASE.IDLE;
        if (elapsed < P5_CHASE.GRACE_END_SEC) return P5_CHASE_PHASE.GRACE;
        if (elapsed < P5_CHASE.GROUND_REWARD_END_SEC) return P5_CHASE_PHASE.GROUND_REWARD;
        if (elapsed < P5_CHASE.MIXED_END_SEC) return P5_CHASE_PHASE.MIXED;
        return P5_CHASE_PHASE.FINALE;
      }
      function p5DecisionContentVisible() {
        const visible = (entity) => entity && entity.active !== false && entity.x < W && entity.x + safeNumber(entity.w, 1) > 0;
        return holes.some(visible) || obstacles.some(visible) || items.some(visible);
      }
      function cleanupP5ChaseRequests() {
        if (!spawn || !spawn.requests) return;
        for (const zone of [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE]) {
          spawn.requests[zone] = spawnRequestQueue(zone).filter((req) => !req.p5ChaseSessionId);
        }
      }
      function startP5ChaseSession(km) {
        cleanupP5ChaseRequests();
        if (spawn.activePattern && spawn.activePattern.status === "active") abortDecisionPattern("chase_started", km);
        cleanupOrphanedPatternRequests();
        run.chaseSessionId = safeInt(run.chaseSessionId) + 1;
        run.chaseSessionCount = safeInt(run.chaseSessionCount) + 1;
        run.chaseSessionActive = true;
        run.chase = P5_CHASE.END_SEC;
        run.chaseElapsedSec = 0;
        run.chasePhase = P5_CHASE_PHASE.GRACE;
        run.chaseEventStatus = P5_CHASE.EVENTS.map(() => "waiting");
        run.chaseSessionGroundCount = 0;
        run.chaseSessionHoleCount = 0;
        run.chaseSessionScoreItemCount = 0;
        run.chaseSessionOncomingCount = 0;
        run.chaseCurrentDecisionBlankSec = 0;
        run.chaseSessionMaxDecisionBlankSec = 0;
        run.chaseReached2Km = km >= 2;
        run.chaseSessionStartDancerSpawnCount = safeInt(run.dancerSpawnCount);
        spawn.chaseGraceUntil = run.elapsed + P5_CHASE.GRACE_END_SEC;
        spawn.nextChaseEventAt = 999;
      }
      function finishP5ChaseSession(km) {
        if (!run.chaseSessionActive) return;
        cleanupP5ChaseRequests();
        run.chaseCompletedSessionCount = safeInt(run.chaseCompletedSessionCount) + 1;
        const groundOk = run.chaseSessionGroundCount >= 5 && run.chaseSessionGroundCount <= 8;
        const holeOk = run.chaseSessionHoleCount >= 2 && run.chaseSessionHoleCount <= 4;
        const scoreOk = run.chaseSessionScoreItemCount >= 4 && run.chaseSessionScoreItemCount <= 7;
        const oncomingOk = run.chaseReached2Km
          ? run.chaseSessionOncomingCount >= 1 && run.chaseSessionOncomingCount <= 3
          : run.chaseSessionOncomingCount <= 3;
        const dancerOk = safeInt(run.dancerSpawnCount) === safeInt(run.chaseSessionStartDancerSpawnCount);
        if (!groundOk || !holeOk || !scoreOk || !oncomingOk || !dancerOk) run.chaseCountRangeViolationCount = safeInt(run.chaseCountRangeViolationCount) + 1;
        run.chaseLastSessionSummary = {
          id: run.chaseSessionId,
          ground: run.chaseSessionGroundCount,
          holes: run.chaseSessionHoleCount,
          scoreItems: run.chaseSessionScoreItemCount,
          oncoming: run.chaseSessionOncomingCount,
          reached2Km: Boolean(run.chaseReached2Km),
          maxDecisionBlankSec: safeNumber(run.chaseSessionMaxDecisionBlankSec),
          dancerAdded: safeInt(run.dancerSpawnCount) - safeInt(run.chaseSessionStartDancerSpawnCount),
        };
        run.chaseSessionActive = false;
        run.chasePhase = P5_CHASE_PHASE.IDLE;
        run.chaseElapsedSec = P5_CHASE.END_SEC;
        const d = getDifficultyByKm(km);
        spawn.nextObstacleAt = Math.max(spawn.nextObstacleAt, km + d.obs + 0.008);
        spawn.nextHoleAt = Math.max(spawn.nextHoleAt, km + d.holeGap + 0.010);
        const itemAt = km + d.item + 0.006;
        spawn.nextItemAt = Math.max(spawn.nextItemAt, itemAt);
        spawn.nextScoreItemAt = Math.max(spawn.nextScoreItemAt, itemAt);
        spawn.nextOncomingAt = Math.max(spawn.nextOncomingAt, km + nextOncomingInterval(km));
      }
      function updateP5ChaseState(dt) {
        const before = safeNumber(run.chase);
        if (before > 0 && run.chaseSessionActive) {
          const kmNow = (run.maxRunMeters || run.runMeters || 0) / 1000;
          run.chaseReached2Km = run.chaseReached2Km || kmNow >= 2;
          run.chaseElapsedSec = getP5ChaseElapsedSec();
          run.chasePhase = getP5ChasePhase(run.chaseElapsedSec);
          if (run.chaseElapsedSec >= P5_CHASE.GRACE_END_SEC) {
            if (p5DecisionContentVisible()) run.chaseCurrentDecisionBlankSec = 0;
            else run.chaseCurrentDecisionBlankSec = safeNumber(run.chaseCurrentDecisionBlankSec) + dt;
            run.chaseSessionMaxDecisionBlankSec = Math.max(safeNumber(run.chaseSessionMaxDecisionBlankSec), run.chaseCurrentDecisionBlankSec);
            run.chaseMaxDecisionBlankSec = Math.max(safeNumber(run.chaseMaxDecisionBlankSec), run.chaseSessionMaxDecisionBlankSec);
          }
          run.chase = Math.max(0, before - dt);
          run.chaseElapsedSec = getP5ChaseElapsedSec();
          run.chasePhase = getP5ChasePhase(run.chaseElapsedSec);
          if (before > 0 && run.chase <= 0) {
            finishP5ChaseSession(kmNow);
            run.escapedFlash = ESCAPED_FLASH_SEC;
          }
        } else run.chase = Math.max(0, before - dt);
      }
      function makeP5ChaseRequest(event, index, km) {
        let zone, kind, fallbackKind, payload;
        if (event.type === "ground") {
          zone = WORLD_ZONE.GROUND; kind = SPAWN_REQUEST_KIND.GROUND_OBSTACLE; fallbackKind = kind;
          payload = { dir: -1, emoji: index % 2 ? "🏃🏻" : "🚶", x: -44 };
        } else if (event.type === "hole") {
          zone = WORLD_ZONE.HOLE; kind = SPAWN_REQUEST_KIND.HOLE; fallbackKind = kind;
          payload = { kind: "SMALL", w: 30 };
        } else if (event.type === "score") {
          zone = WORLD_ZONE.AIR; kind = SPAWN_REQUEST_KIND.SCORE_ITEM; fallbackKind = kind;
          payload = { lane: index % 2 ? "mid" : "low", high: false, type: "💰", x: -36, challenge: false };
        } else if (event.type === "oncoming") {
          if (km < 2) return null;
          zone = WORLD_ZONE.GROUND; kind = SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE; fallbackKind = kind;
          payload = { dir: 1, emoji: "🚶", x: getOncomingSpawnX(km) };
        } else return null;
        const req = makeSpawnRequest(zone, kind, SPAWN_SOURCE.CHASE, km, `p5:${run.chaseSessionId}:${index}`, payload, fallbackKind);
        req.p5ChaseSessionId = run.chaseSessionId;
        req.p5ChaseEventIndex = index;
        req.p5ChaseEventType = event.type;
        req.maxTotalAttempts = 12;
        return req;
      }
      function collectP5ChaseRequests(km) {
        if (!run.chaseSessionActive || run.chase <= 0) return;
        const elapsed = getP5ChaseElapsedSec();
        let queued = 0;
        for (let i = 0; i < P5_CHASE.EVENTS.length && queued < 2; i++) {
          if (run.chaseEventStatus[i] !== "waiting") continue;
          const event = P5_CHASE.EVENTS[i];
          if (event.at > elapsed) continue;
          if (event.type === "oncoming" && km < 2) continue;
          const req = makeP5ChaseRequest(event, i, km);
          if (req && enqueueSpawnRequest(req)) {
            run.chaseEventStatus[i] = "queued";
            if (event.type === "oncoming") run.oncomingCandidateCount = safeInt(run.oncomingCandidateCount) + 1;
            queued++;
          }
        }
      }
      function recordP5ChaseRequestOutcome(req, success) {
        if (!req || !req.p5ChaseSessionId || req.p5ChaseSessionId !== run.chaseSessionId) return;
        const index = safeInt(req.p5ChaseEventIndex);
        if (index < run.chaseEventStatus.length) run.chaseEventStatus[index] = success ? "resolved" : "skipped";
      }
      function recordP5SpawnSuccess(entity, request, km) {
        if (!entity) return;
        if (isDancerInvincible() && entity.objectRole === OBJECT_ROLE.HAZARD && !entity.p5InvincibleCounted) {
          entity.p5InvincibleCounted = true;
          run.invincibleSessionPresentedObstacleCount = safeInt(run.invincibleSessionPresentedObstacleCount) + 1;
          run.invinciblePresentedObstacleCount = safeInt(run.invinciblePresentedObstacleCount) + 1;
        }
        if (!run.chaseSessionActive || run.chase <= 0 || entity.p5ChaseCounted) return;
        entity.p5ChaseCounted = true;
        entity.p5ChaseSessionId = run.chaseSessionId;
        const elapsed = getP5ChaseElapsedSec();
        const isHazard = entity.zone === WORLD_ZONE.HOLE || entity.objectRole === OBJECT_ROLE.HAZARD;
        if (elapsed < P5_CHASE.GRACE_END_SEC && isHazard) run.chaseGraceHazardViolationCount = safeInt(run.chaseGraceHazardViolationCount) + 1;
        if (entity.zone === WORLD_ZONE.HOLE) {
          run.chaseSessionHoleCount = safeInt(run.chaseSessionHoleCount) + 1;
          run.chaseHolePresentedCount = safeInt(run.chaseHolePresentedCount) + 1;
        } else if (entity.objectRole === OBJECT_ROLE.HAZARD && entity.zone !== WORLD_ZONE.AIR) {
          if (entity.movementType === MOVEMENT_TYPE.ONCOMING) {
            run.chaseSessionOncomingCount = safeInt(run.chaseSessionOncomingCount) + 1;
            run.chaseOncomingPresentedCount = safeInt(run.chaseOncomingPresentedCount) + 1;
          } else {
            run.chaseSessionGroundCount = safeInt(run.chaseSessionGroundCount) + 1;
            run.chaseGroundPresentedCount = safeInt(run.chaseGroundPresentedCount) + 1;
          }
        } else if (entity.objectRole === OBJECT_ROLE.REWARD) {
          run.chaseSessionScoreItemCount = safeInt(run.chaseSessionScoreItemCount) + 1;
          run.chaseScoreItemPresentedCount = safeInt(run.chaseScoreItemPresentedCount) + 1;
        }
      }
      function hasPendingInvincibleRequest() {
        return spawnRequestQueue(WORLD_ZONE.GROUND).some((req) => req.spawnSource === SPAWN_SOURCE.INVINCIBLE && req.status !== SPAWN_REQUEST_STATUS.RESOLVED && req.status !== SPAWN_REQUEST_STATUS.SKIPPED);
      }
'''

index = replace_once(
    index,
    '''      function resolveBetweenHoleObstacle(km, dir) {''',
    p5_helpers + '''      function resolveBetweenHoleObstacle(km, dir) {''',
    'P5 helper functions',
)

index = replace_once(
    index,
    '''        if (run.chase > 0 && km >= 2) return 0.55;''',
    '''        if (run.chase > 0) return 0;''',
    'chase between-hole ground only',
)

index = replace_once(
    index,
    '''        maybeAdoptDecisionPatternFromEntity(entity, request, km);''',
    '''        recordP5SpawnSuccess(entity, request, km);
        maybeAdoptDecisionPatternFromEntity(entity, request, km);''',
    'P5 spawn accounting',
)

index = replace_once(
    index,
    '''        if (req && req.spawnSource === SPAWN_SOURCE.PATTERN) return false;''',
    '''        if (req && req.p5ChaseSessionId) return false;
        if (req && req.spawnSource === SPAWN_SOURCE.PATTERN) return false;''',
    'P5 request reservation bypass',
)

index = replace_once(
    index,
    '''        collectDecisionPatternRequests(km);''',
    '''        collectDecisionPatternRequests(km);
        collectP5ChaseRequests(km);''',
    'collect P5 requests',
)

index = replace_once(
    index,
    '''        if (isDancerInvincible() && run.invincibleObstacleSpawned < run.invincibleObstaclePlanCount && km >= spawn.nextObstacleAt) {
          const key = "invincible:" + run.invincibleObstacleSpawned;
          enqueueSpawnRequestIfNew(WORLD_ZONE.GROUND, SPAWN_REQUEST_KIND.GROUND_OBSTACLE, SPAWN_SOURCE.INVINCIBLE, km, key, () => ({ dir: -1, emoji: OBS_TYPES[(Math.random()*OBS_TYPES.length)|0][0], x: -44 }), SPAWN_REQUEST_KIND.GROUND_OBSTACLE);
        }''',
    '''        if (!chase && isDancerInvincible() && run.invincibleSessionPresentedObstacleCount < run.invincibleObstaclePlanCount && run.elapsed >= spawn.nextInvincibleObstacleAt && !hasPendingInvincibleRequest()) {
          const key = `invincible:${run.invincibleSessionId}:${run.invincibleRequestIndex}`;
          enqueueSpawnRequestIfNew(
            WORLD_ZONE.GROUND,
            SPAWN_REQUEST_KIND.GROUND_OBSTACLE,
            SPAWN_SOURCE.INVINCIBLE,
            km,
            key,
            () => ({ dir: -1, emoji: run.invincibleRequestIndex % 2 ? "🏃🏻" : "🚶", x: -44 }),
            SPAWN_REQUEST_KIND.GROUND_OBSTACLE,
            () => {
              run.invincibleRequestIndex = safeInt(run.invincibleRequestIndex) + 1;
              spawn.nextInvincibleObstacleAt = run.elapsed + P5_CHASE.INVINCIBLE_REQUEST_GAP_SEC;
            }
          );
        }''',
    'invincible obstacle plan',
)

index = replace_once(
    index,
    '''        if (chase && chaseReady && !suppressNormalGround && !reserveOncoming && run.elapsed >= (spawn.nextChaseEventAt || 999)) {
          const key = "chase:" + spawn.nextChaseEventAt.toFixed(2);
          enqueueSpawnRequestIfNew(WORLD_ZONE.GROUND, SPAWN_REQUEST_KIND.GROUND_OBSTACLE, SPAWN_SOURCE.CHASE, km, key, () => ({ dir: -1, emoji: "🚶", x: -44 }), SPAWN_REQUEST_KIND.GROUND_OBSTACLE, () => { spawn.nextChaseEventAt = run.elapsed + rand(0.4, 0.8); });
        }
''',
    '',
    'remove legacy chase event',
)

for old, new, label in [
    ('        if (dueScoreItem) {', '        if (!chase && dueScoreItem) {', 'suppress normal score during chase'),
    ('        if (dueHole && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {', '        if (!chase && dueHole && !reservePattern && !isOncomingCriticallyOverdue(km) && !spawn.needObstacleBeforeNextHole && chaseReady) {', 'suppress normal hole during chase'),
    ('        if (dueObstacle && chaseReady && !suppressNormalGround && !reserveOncoming) {', '        if (!chase && dueObstacle && chaseReady && !suppressNormalGround && !reserveOncoming) {', 'suppress normal ground during chase'),
    ('        if ((oncomingDue || forceEarlyOncoming) && (!suppressNormalGround || forceEarlyOncoming)) {', '        if (!chase && (oncomingDue || forceEarlyOncoming) && (!suppressNormalGround || forceEarlyOncoming)) {', 'suppress normal oncoming during chase'),
    ('        if (km >= run.nextDancerAt && !reservePattern) {', '        if (!chase && km >= run.nextDancerAt && !reservePattern) {', 'suppress dancer during chase'),
]:
    index = replace_once(index, old, new, label)

index = replace_once(
    index,
    '''        if (req.spawnSource === SPAWN_SOURCE.CHASE) spawn.nextChaseEventAt = run.elapsed + rand(0.4, 0.8);''',
    '''        if (req.spawnSource === SPAWN_SOURCE.CHASE && !req.p5ChaseSessionId) spawn.nextChaseEventAt = run.elapsed + rand(0.4, 0.8);''',
    'legacy chase schedule guard',
)

index = replace_once(
    index,
    '''          recordDecisionPatternRequestOutcome(req, true, km, entity);
          return true;''',
    '''          recordDecisionPatternRequestOutcome(req, true, km, entity);
          recordP5ChaseRequestOutcome(req, true);
          return true;''',
    'P5 success outcome',
)

index = replace_once(
    index,
    '''            recordDecisionPatternRequestOutcome(req, false, km, null);
            if (req.spawnSource === SPAWN_SOURCE.BETWEEN_HOLES)''',
    '''            recordDecisionPatternRequestOutcome(req, false, km, null);
            recordP5ChaseRequestOutcome(req, false);
            if (req.spawnSource === SPAWN_SOURCE.BETWEEN_HOLES)''',
    'P5 skipped outcome',
)

index = replace_once(
    index,
    '''        let kind = opt.kind || d.holeKinds[(Math.random() * d.holeKinds.length) | 0];
        if (kind === "LARGE" && km < 5) kind = "MEDIUM";''',
    '''        let kind = opt.kind || d.holeKinds[(Math.random() * d.holeKinds.length) | 0];
        if (kind === "LARGE" && km < 5) kind = "MEDIUM";
        kind = normalizeHoleKindForP5(kind, km);''',
    'large hole block',
)

index = replace_once(
    index,
    '''        run.chase = CHASE_TIME;
        spawn.chaseGraceUntil = run.elapsed + 0.7;''',
    '''        startP5ChaseSession(run.runMeters / 1000);''',
    'start P5 chase',
)

index = replace_once(
    index,
    '''              run.invinciblePreventedAccidents++;
              floatText(o.x + 14, o.y - 8, "無敵", "#f4eaff");''',
    '''              run.invinciblePreventedAccidents++;
              run.invincibleBreakthroughFlash = 0.85;
              floatText(o.x + 14, o.y - 8, "無敵で突破!", "#f4eaff");''',
    'invincible breakthrough display',
)

index = replace_once(
    index,
    '''          chaseObstacleSpawnCount: run.chaseObstacleSpawnCount || 0,
          chaseHoleSpawnCount: run.chaseHoleSpawnCount || 0,
          chaseScoreItemSpawnCount: run.chaseScoreItemSpawnCount || 0,
          chaseOncomingSpawnCount: run.chaseOncomingSpawnCount || 0,
          invincibleObstacleSpawnCount: run.invincibleObstacleSpawnCount || 0,
          invinciblePreventedAccidents: run.invinciblePreventedAccidents || 0,''',
    '''          chaseObstacleSpawnCount: run.chaseObstacleSpawnCount || 0,
          chaseHoleSpawnCount: run.chaseHoleSpawnCount || 0,
          chaseScoreItemSpawnCount: run.chaseScoreItemSpawnCount || 0,
          chaseOncomingSpawnCount: run.chaseOncomingSpawnCount || 0,
          chaseSessionCount: safeInt(run.chaseSessionCount),
          chaseCompletedSessionCount: safeInt(run.chaseCompletedSessionCount),
          chaseGroundPresentedCount: safeInt(run.chaseGroundPresentedCount),
          chaseHolePresentedCount: safeInt(run.chaseHolePresentedCount),
          chaseScoreItemPresentedCount: safeInt(run.chaseScoreItemPresentedCount),
          chaseOncomingPresentedCount: safeInt(run.chaseOncomingPresentedCount),
          chaseMaxDecisionBlankSec: safeNumber(run.chaseMaxDecisionBlankSec),
          chaseGraceHazardViolationCount: safeInt(run.chaseGraceHazardViolationCount),
          chaseCountRangeViolationCount: safeInt(run.chaseCountRangeViolationCount),
          chaseLastSessionSummary: run.chaseLastSessionSummary,
          invincibleSessionCount: safeInt(run.invincibleSessionCount),
          invincibleObstacleSpawnCount: run.invincibleObstacleSpawnCount || 0,
          invinciblePresentedObstacleCount: safeInt(run.invinciblePresentedObstacleCount),
          invinciblePreventedAccidents: run.invinciblePreventedAccidents || 0,
          invincibleBackgroundDecayViolationCount: safeInt(run.invincibleBackgroundDecayViolationCount),
          invincibleLargeHoleViolationCount: safeInt(run.invincibleLargeHoleViolationCount),''',
    'P5 result snapshot',
)

INDEX.write_text(index)

for path in [
    SPEC,
    REPORT,
    ROOT / 'tests/release-comprehensive.js',
    ROOT / 'tests/effective-presentation-metrics.js',
    ROOT / 'tests/p2-density-regression.js',
    ROOT / 'tests/p3-pattern-regression.js',
    ROOT / 'tests/p4-air-obstacle-regression.js',
]:
    if path.exists():
        path.write_text(path.read_text().replace(OLD_VERSION, NEW_VERSION))

spec = SPEC.read_text()
if '## v21 P5 逃走・無敵専用構成' not in spec:
    spec += '''\n\n## v21 P5 逃走・無敵専用構成\n\n- 事故後15秒を`grace / ground_reward / mixed / finale`へ分割する。\n- 逃走中の通常P2予定、P3 pattern、P4 AIR、👯‍♀️新規生成を停止し、P5専用requestだけを使用する。\n- 逃走中の穴はSMALLのみ。穴後の必須障害物は地上方向へ固定する。\n- 👯‍♀️無敵4秒は固定stepの`dt`だけで減算し、`performance.now()`期限を使用しない。\n- 無敵中に障害物を2〜3回提示し、不足分だけ`spawnSource=invincible`で補う。\n- 無敵終了後0.14km以内はLARGE holeをMEDIUMへ格下げする。\n- 穴、TTC、スコア、ランキング、Supabase契約は変更しない。\n'''
SPEC.write_text(spec)

report = REPORT.read_text()
if '## v21 P5 逃走・無敵専用構成' not in report:
    report += '''\n\n## v21 P5 逃走・無敵専用構成\n\n- 15秒逃走を4フェーズへ分割。\n- 逃走専用の地上、SMALL hole、報酬、2km以降対向requestを追加。\n- 無敵4秒を実プレイ時間基準へ変更。\n- 無敵障害物2〜3回、終了後LARGE hole抑制、突破表示を追加。\n- P1〜P4、progressive、release、150km耐久を回帰ゲートとして維持する。\n'''
REPORT.write_text(report)

print('P5 chase and invincible implementation patch applied')
