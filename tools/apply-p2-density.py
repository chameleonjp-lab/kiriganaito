from pathlib import Path

index_path = Path("index.html")
index = index_path.read_text()

for old in (
    "kiriganaito-2026-07-11-v14-world-zones",
    "kiriganaito-2026-07-12-v16-spawn-director-correctness",
):
    index = index.replace(old, "kiriganaito-2026-07-18-v18-effective-density")

anchor = '      function spawnRequestQueue(zone) { return spawn.requests && spawn.requests[zone] ? spawn.requests[zone] : []; }'
helpers = '''      const P2_DENSITY = Object.freeze({
        SCORE_ITEM_OVERDUE_KM: 0.10,
        ONCOMING_OVERDUE_KM: 0.10,
      });
      function spawnRequestQueue(zone) { return spawn.requests && spawn.requests[zone] ? spawn.requests[zone] : []; }
      function hasPendingSpawnRequestKind(kind) {
        const zones = [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE];
        for (let z = 0; z < zones.length; z++) {
          const q = spawnRequestQueue(zones[z]);
          for (let i = 0; i < q.length; i++) {
            const req = q[i];
            if (req.kind === kind && req.status !== SPAWN_REQUEST_STATUS.RESOLVED && req.status !== SPAWN_REQUEST_STATUS.SKIPPED) return true;
          }
        }
        return false;
      }
      function isHoleReservationActive(km) {
        return !spawn.needObstacleBeforeNextHole && (km >= spawn.nextHoleAt || hasPendingSpawnRequestKind(SPAWN_REQUEST_KIND.HOLE));
      }
      function isScoreItemReservationActive(km) {
        const dueAt = spawn.nextScoreItemAt ?? spawn.nextItemAt;
        return !spawn.needObstacleBeforeNextHole && !isHoleReservationActive(km) && km - dueAt >= P2_DENSITY.SCORE_ITEM_OVERDUE_KM;
      }
      function isOncomingReservationActive(km) {
        return km >= 0.8 && !spawn.needObstacleBeforeNextHole && !isHoleReservationActive(km) && !isScoreItemReservationActive(km) && km - spawn.nextOncomingAt >= P2_DENSITY.ONCOMING_OVERDUE_KM;
      }
      function isNonMandatoryGroundRequest(req) {
        if (!req || req.zone !== WORLD_ZONE.GROUND) return false;
        if (req.spawnSource !== SPAWN_SOURCE.NORMAL && req.spawnSource !== SPAWN_SOURCE.CHASE) return false;
        return req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE || req.kind === SPAWN_REQUEST_KIND.ONCOMING_OBSTACLE;
      }
      function shouldDeferSpawnRequest(req, km) {
        if (!isNonMandatoryGroundRequest(req)) return false;
        if (spawn.needObstacleBeforeNextHole) return true;
        if (isHoleReservationActive(km)) return true;
        if (isScoreItemReservationActive(km)) return true;
        return isOncomingReservationActive(km) && req.kind === SPAWN_REQUEST_KIND.GROUND_OBSTACLE;
      }'''
if anchor not in index:
    raise SystemExit("spawnRequestQueue anchor missing")
index = index.replace(anchor, helpers, 1)

replacements = [
    (
        '        const forceEarlyOncoming = (earlyOncomingDue || (km >= 2 && !run.earlyOncomingSpawned));\n        if (isDancerInvincible()',
        '        const forceEarlyOncoming = (earlyOncomingDue || (km >= 2 && !run.earlyOncomingSpawned));\n        const reserveHole = isHoleReservationActive(km);\n        const reserveScoreItem = isScoreItemReservationActive(km);\n        const reserveOncoming = isOncomingReservationActive(km);\n        const suppressNormalGround = spawn.needObstacleBeforeNextHole || reserveHole || reserveScoreItem;\n        if (isDancerInvincible()',
        "collect head",
    ),
    (
        '        if (chase && chaseReady && run.elapsed >= (spawn.nextChaseEventAt || 999)) {',
        '        if (chase && chaseReady && !suppressNormalGround && !reserveOncoming && run.elapsed >= (spawn.nextChaseEventAt || 999)) {',
        "chase",
    ),
    (
        '        if (dueObstacle && chaseReady) {',
        '        if (dueObstacle && chaseReady && !suppressNormalGround && !reserveOncoming) {',
        "obstacle",
    ),
    (
        '        if (oncomingDue || forceEarlyOncoming) {',
        '        if ((oncomingDue || forceEarlyOncoming) && (!suppressNormalGround || forceEarlyOncoming)) {',
        "oncoming",
    ),
    (
        '          const r = q[i]; if (r.nextAttemptKm > km || r.status === SPAWN_REQUEST_STATUS.RESOLVED || r.status === SPAWN_REQUEST_STATUS.SKIPPED) continue;\n          if (best < 0',
        '          const r = q[i]; if (r.nextAttemptKm > km || r.status === SPAWN_REQUEST_STATUS.RESOLVED || r.status === SPAWN_REQUEST_STATUS.SKIPPED) continue;\n          if (shouldDeferSpawnRequest(r, km)) continue;\n          if (best < 0',
        "select",
    ),
]
for old, new, name in replacements:
    if old not in index:
        raise SystemExit(f"{name} anchor missing")
    index = index.replace(old, new, 1)
index_path.write_text(index)

metrics_path = Path("tests/effective-presentation-metrics.js")
metrics = metrics_path.read_text()
metric_replacements = [
    (
        '      gapSamples: 0,\n    };',
        '      gapSamples: 0,\n      presentationKm: [],\n      bandCounts: { km0to1: 0, km1to2: 0, km2plus: 0 },\n    };',
        "metric init",
    ),
    (
        '  let maxBlankSecAfter500m = 0;\n  let maxSimultaneousStrongHazards = 0;',
        '  let maxBlankSecAfter500m = 0;\n  let maxDecisionBlankSecAfter500m = 0;\n  let lastDecisionSec = 0;\n  let presentedMissTargetCount = 0;\n  let maxSimultaneousStrongHazards = 0;',
        "metric vars",
    ),
    (
        '    metric.count += 1;\n    if (metric.lastKm !== null) {',
        '    metric.count += 1;\n    metric.presentationKm.push(entity.presentedKm);\n    if (entity.presentedKm < 1) metric.bandCounts.km0to1 += 1;\n    else if (entity.presentedKm < 2) metric.bandCounts.km1to2 += 1;\n    else metric.bandCounts.km2plus += 1;\n    if (type === "scoreItem" && Number(entity.missPenalty || 0) > 0) presentedMissTargetCount += 1;\n    if (measurementStarted) {\n      maxDecisionBlankSecAfter500m = Math.max(maxDecisionBlankSecAfter500m, entity.presentedSec - lastDecisionSec);\n      lastDecisionSec = entity.presentedSec;\n    }\n    if (metric.lastKm !== null) {',
        "record",
    ),
    (
        '      lastAnyKm = run.runMeters / 1000;\n      lastAnySec = run.elapsed;\n    }',
        '      lastAnyKm = run.runMeters / 1000;\n      lastAnySec = run.elapsed;\n      lastDecisionSec = run.elapsed;\n    }',
        "measurement start",
    ),
    (
        '      maxBlankSecAfter500m = Math.max(maxBlankSecAfter500m, run.elapsed - lastAnySec);\n    }\n  }',
        '      maxBlankSecAfter500m = Math.max(maxBlankSecAfter500m, run.elapsed - lastAnySec);\n      maxDecisionBlankSecAfter500m = Math.max(maxDecisionBlankSecAfter500m, run.elapsed - lastDecisionSec);\n    }\n  }',
        "blank tail",
    ),
    (
        '    maxBlankKmAfter500m,\n    maxBlankSecAfter500m,\n    maxSimultaneousStrongHazards,',
        '    maxBlankKmAfter500m,\n    maxBlankSecAfter500m,\n    maxDecisionBlankSecAfter500m,\n    presentedMissTargetCount,\n    maxSimultaneousStrongHazards,',
        "report fields",
    ),
]
for old, new, name in metric_replacements:
    if old not in metrics:
        raise SystemExit(f"{name} anchor missing")
    metrics = metrics.replace(old, new, 1)
metrics_path.write_text(metrics)

spec_path = Path("SPEC.md")
spec = spec_path.read_text()
spec += '''

## v18 P2 実効出現密度契約（現行）

- 現行 CLIENT_VERSION は `kiriganaito-2026-07-18-v18-effective-density`。
- 穴予定が期限へ達した時は、通常地上障害物と通常対向障害物を一時保留し、既存の穴安全距離を満たすための予約区間を作る。
- 穴生成後は `between_holes` の必須障害物を優先し、それが解決するまで通常地上予定を保留する。
- 加点アイテムが予定から0.10km以上遅れた場合は、穴予約を優先した上でアイテム安全区間を作る。
- 通常対向障害物が予定から0.10km以上遅れた場合は、通常地上障害物だけを一時保留する。
- `between_holes`、`early_oncoming`、`invincible` は通常予約より優先する。
- 穴幅、障害物速度、TTC最低条件、ジャンプ、当たり判定、点数、UI、ランキング、Supabaseは変更しない。
- P1の実効出現計測を継続し、30固定seedのP2密度ゲートで偏りを検査する。
'''
spec_path.write_text(spec)

report_path = Path("TEST_REPORT.md")
report = report_path.read_text()
report += '''

## v18 P2 実効出現密度再調整

- 基準: P1固定seedでは穴16個/15km、最大穴間隔1.312km、加点アイテム最大間隔1.332km。
- 対応: 穴、穴間必須障害物、期限超過アイテム、期限超過対向障害物の予約優先順位を追加。
- 安全値は変更せず、通常地上予定を一時保留して既存安全距離を成立させる。
- `tests/p2-density-regression.js` に30固定seedの合格条件を追加。
- 自動検査結果は `artifacts/p2-density-regression.json` に記録する。
'''
report_path.write_text(report)
