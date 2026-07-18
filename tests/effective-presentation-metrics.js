#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.join(__dirname, "..");
const INDEX_PATH = path.join(ROOT, "index.html");
const OUTPUT_PATH = path.join(ROOT, "artifacts", "p1-effective-presentation-metrics.json");
const TARGET_METERS = 5000;
const SEEDS = [17001, 17002, 17003];
const RECOGNIZABLE_WIDTH_PX = 18;

function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 0x100000000;
  };
}

function makeElement(id) {
  const classNames = new Set();
  const element = {
    id,
    textContent: "",
    value: "",
    hidden: false,
    disabled: false,
    className: "",
    children: [],
    style: {},
    onclick: null,
    get childNodes() {
      return this.children;
    },
    classList: {
      add(name) {
        classNames.add(name);
        element.className = [...classNames].join(" ");
      },
      remove(name) {
        classNames.delete(name);
        element.className = [...classNames].join(" ");
      },
      toggle(name) {
        if (classNames.has(name)) classNames.delete(name);
        else classNames.add(name);
        element.className = [...classNames].join(" ");
      },
      contains(name) {
        return classNames.has(name);
      },
    },
    append(...nodes) {
      this.children.push(...nodes);
    },
    appendChild(node) {
      this.children.push(node);
      return node;
    },
    replaceChildren(...nodes) {
      this.children.splice(0, this.children.length, ...nodes);
    },
    addEventListener(name, handler) {
      this[`on${name}`] = handler;
    },
    setAttribute() {},
    getBoundingClientRect() {
      return { width: 320, height: 360 };
    },
  };
  Object.defineProperty(element, "innerHTML", {
    get() {
      return this.children.map((child) => child.textContent || "").join("");
    },
    set(value) {
      this.children.splice(0);
      this.textContent = String(value);
    },
  });
  return element;
}

function createSandbox(seed) {
  const ids = [
    "home", "rules", "name", "game", "result", "error", "gameCanvas",
    "startBtn", "jumpBtn", "retireBtn", "homeRanking", "resultRanking",
    "homeStats", "resultStats", "homeToast", "playerName", "nameError",
    "hudRun", "hudScore", "hudTime", "hudChase", "hudDanger",
    "hudChaseBox", "hudDangerBox", "playStatus", "resultReason",
    "resultComment", "resultScore", "resultBreakdown", "rankingStatus",
    "rankingRetryBtn", "clientVersionNote", "homeVersionNote",
    "resultVersionTop", "debug", "errorText", "homeBtn", "errorHomeBtn",
    "nameBtn", "rulesBtn", "rulesBackBtn", "readyBtn", "shareBtn",
    "againBtn", "resultHomeBtn", "otherGamesResult", "changeNameBtn",
    "homeShareBtn", "nameStartBtn", "nameBackBtn", "resultShareBtn",
    "retryBtn", "otherGamesHome",
  ];
  const elements = new Map(ids.map((id) => [id, makeElement(id)]));
  const drawCalls = [];
  elements.get("gameCanvas").getContext = () => new Proxy(
    {
      createLinearGradient() { return { addColorStop() {} }; },
      createRadialGradient() { return { addColorStop() {} }; },
      measureText(text) { return { width: String(text).length * 10 }; },
      fillText(text, x, y) { drawCalls.push({ text: String(text), x, y }); },
    },
    {
      get(target, property) {
        if (property in target) return target[property];
        return () => {};
      },
      set() { return true; },
    },
  );

  const storage = new Map();
  const networkRequests = [];
  const consoleErrors = [];
  const consoleWarnings = [];
  let nowMs = 0;
  const math = Object.create(Math);
  math.random = seededRandom(seed);

  const sandbox = {
    Math: math,
    Date,
    JSON,
    Object,
    Array,
    Number,
    String,
    Boolean,
    Set,
    Map,
    WeakSet,
    WeakMap,
    Promise,
    parseInt,
    parseFloat,
    isFinite,
    TextEncoder,
    TextDecoder,
    URL,
    URLSearchParams,
    Blob: global.Blob,
    navigator: {},
    location: { href: "https://example.invalid/kiriganaito/", search: "" },
    performance: { now: () => nowMs },
    __advanceNow(ms) { nowMs += ms; },
    requestAnimationFrame: () => 0,
    cancelAnimationFrame: () => {},
    setTimeout: () => 0,
    clearTimeout: () => {},
    devicePixelRatio: 1,
    addEventListener: () => {},
    localStorage: {
      getItem(key) { return storage.has(key) ? storage.get(key) : null; },
      setItem(key, value) { storage.set(key, String(value)); },
      removeItem(key) { storage.delete(key); },
    },
    fetch: async (url, options = {}) => {
      networkRequests.push({ url: String(url), body: options.body || "" });
      return { ok: false, status: 599, json: async () => ({ mocked: true }) };
    },
    console: {
      ...console,
      error: (...args) => consoleErrors.push(args.join(" ")),
      warn: (...args) => consoleWarnings.push(args.join(" ")),
    },
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  sandbox.document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, makeElement(id));
      return elements.get(id);
    },
    createElement(tag) { return makeElement(tag); },
    addEventListener() {},
    documentElement: { scrollWidth: 320, clientWidth: 320 },
    body: { scrollWidth: 320, clientWidth: 320 },
  };
  sandbox.__testState = {
    elements,
    drawCalls,
    storage,
    networkRequests,
    consoleErrors,
    consoleWarnings,
  };
  return sandbox;
}

function runSeed(script, seed) {
  const sandbox = createSandbox(seed);
  vm.createContext(sandbox);
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "P1-" + ${seed};
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;

  const categoryNames = ["hole", "groundObstacle", "oncoming", "scoreItem", "powerup"];
  const sourceNames = Object.keys(SPAWN_SOURCE).map((key) => SPAWN_SOURCE[key]);
  const metrics = {};
  const sourceCounts = {};
  const categorySourceCounts = {};
  for (const name of categoryNames) {
    metrics[name] = {
      count: 0,
      lastKm: null,
      lastSec: null,
      totalGapKm: 0,
      maxGapKm: 0,
      totalGapSec: 0,
      maxGapSec: 0,
      gapSamples: 0,
      presentationKm: [],
      bandCounts: { km0to1: 0, km1to2: 0, km2plus: 0 },
    };
    categorySourceCounts[name] = {};
    for (const source of sourceNames) categorySourceCounts[name][source] = 0;
  }
  for (const source of sourceNames) sourceCounts[source] = 0;

  let presentedTotal = 0;
  let invalidSourceCount = 0;
  let duplicatePresentationCount = 0;
  let measurementStarted = false;
  let lastAnyKm = 0.5;
  let lastAnySec = 0;
  let maxBlankKmAfter500m = 0;
  let maxBlankSecAfter500m = 0;
  let maxDecisionBlankSecAfter500m = 0;
  let currentDecisionBlankSec = 0;
  let presentedMissTargetCount = 0;
  let maxSimultaneousStrongHazards = 0;

  function isRecognizable(entity) {
    if (!entity || entity.active === false) return false;
    const width = Math.max(1, Number(entity.w) || 1);
    const visibleRequirement = Math.min(width, ${RECOGNIZABLE_WIDTH_PX});
    return entity.x + visibleRequirement >= 0 && entity.x < W;
  }

  function recordPresented(type, entity) {
    if (entity.presented) {
      duplicatePresentationCount += 1;
      return;
    }
    entity.presented = true;
    entity.presentedKm = run.runMeters / 1000;
    entity.presentedSec = run.elapsed;
    const metric = metrics[type];
    metric.count += 1;
    metric.presentationKm.push(entity.presentedKm);
    if (entity.presentedKm < 1) metric.bandCounts.km0to1 += 1;
    else if (entity.presentedKm < 2) metric.bandCounts.km1to2 += 1;
    else metric.bandCounts.km2plus += 1;
    if (type === "scoreItem" && Number(entity.missPenalty || 0) > 0) presentedMissTargetCount += 1;
    if (metric.lastKm !== null) {
      const gapKm = Math.max(0, entity.presentedKm - metric.lastKm);
      const gapSec = Math.max(0, entity.presentedSec - metric.lastSec);
      metric.totalGapKm += gapKm;
      metric.totalGapSec += gapSec;
      metric.maxGapKm = Math.max(metric.maxGapKm, gapKm);
      metric.maxGapSec = Math.max(metric.maxGapSec, gapSec);
      metric.gapSamples += 1;
    }
    metric.lastKm = entity.presentedKm;
    metric.lastSec = entity.presentedSec;

    const source = sourceNames.includes(entity.spawnSource) ? entity.spawnSource : null;
    if (source) {
      sourceCounts[source] += 1;
      categorySourceCounts[type][source] += 1;
    } else {
      invalidSourceCount += 1;
    }

    presentedTotal += 1;
    if (measurementStarted) {
      maxBlankKmAfter500m = Math.max(maxBlankKmAfter500m, entity.presentedKm - lastAnyKm);
      maxBlankSecAfter500m = Math.max(maxBlankSecAfter500m, entity.presentedSec - lastAnySec);
      lastAnyKm = entity.presentedKm;
      lastAnySec = entity.presentedSec;
    }
  }

  function scanEntities() {
    if (!measurementStarted && run.runMeters >= 500) {
      measurementStarted = true;
      lastAnyKm = run.runMeters / 1000;
      lastAnySec = run.elapsed;
      currentDecisionBlankSec = 0;
    }

    for (let i = 0; i < holes.length; i++) {
      const entity = holes[i];
      if (!entity.presented && isRecognizable(entity)) recordPresented("hole", entity);
    }
    for (let i = 0; i < obstacles.length; i++) {
      const entity = obstacles[i];
      if (!entity.presented && isRecognizable(entity)) {
        recordPresented(entity.movementType === MOVEMENT_TYPE.ONCOMING ? "oncoming" : "groundObstacle", entity);
      }
    }
    for (let i = 0; i < items.length; i++) {
      const entity = items[i];
      if (!entity.presented && isRecognizable(entity)) {
        recordPresented(entity.objectRole === OBJECT_ROLE.POWERUP ? "powerup" : "scoreItem", entity);
      }
    }

    let simultaneousHazards = 0;
    for (let i = 0; i < holes.length; i++) {
      const entity = holes[i];
      if (entity.x < W && entity.x + (entity.w || 0) > 0) simultaneousHazards += 1;
    }
    for (let i = 0; i < obstacles.length; i++) {
      const entity = obstacles[i];
      if (entity.active !== false && entity.x < W && entity.x + (entity.w || 0) > 0) simultaneousHazards += 1;
    }
    maxSimultaneousStrongHazards = Math.max(maxSimultaneousStrongHazards, simultaneousHazards);

    const visibleContent =
      holes.some((entity) => entity.x < W && entity.x + (entity.w || 0) > 0) ||
      obstacles.some((entity) => entity.active !== false && entity.x < W && entity.x + (entity.w || 0) > 0) ||
      items.some((entity) => entity.active !== false && entity.x < W && entity.x + (entity.w || 0) > 0);
    if (measurementStarted) {
      const currentKm = run.runMeters / 1000;
      maxBlankKmAfter500m = Math.max(maxBlankKmAfter500m, currentKm - lastAnyKm);
      maxBlankSecAfter500m = Math.max(maxBlankSecAfter500m, run.elapsed - lastAnySec);
      currentDecisionBlankSec = visibleContent ? 0 : currentDecisionBlankSec + FIXED_STEP;
      maxDecisionBlankSecAfter500m = Math.max(maxDecisionBlankSecAfter500m, currentDecisionBlankSec);
    }
  }

  const maxFrames = 240000;
  let frames = 0;
  while (mode === MODE.PLAYING && run.runMeters < ${TARGET_METERS} && frames < maxFrames) {
    __advanceNow(FIXED_STEP * 1000);
    update(FIXED_STEP);
    scanEntities();
    frames += 1;
  }

  for (const name of categoryNames) {
    const metric = metrics[name];
    metric.avgGapKm = metric.gapSamples ? metric.totalGapKm / metric.gapSamples : 0;
    metric.avgGapSec = metric.gapSamples ? metric.totalGapSec / metric.gapSamples : 0;
    delete metric.lastKm;
    delete metric.lastSec;
  }

  const generated = {
    hole: safeInt(run.holeSpawnCount),
    groundObstacle: Math.max(0, safeInt(run.obstacleSpawnCount) - safeInt(run.oncomingSpawnCount)),
    oncoming: safeInt(run.oncomingSpawnCount),
    scoreItem: safeInt(run.scoreItemSpawnCount),
    powerup: safeInt(run.invincibleItemSpawnCount),
  };
  const presented = {
    hole: metrics.hole.count,
    groundObstacle: metrics.groundObstacle.count,
    oncoming: metrics.oncoming.count,
    scoreItem: metrics.scoreItem.count,
    powerup: metrics.powerup.count,
  };
  const sourceTotal = Object.values(sourceCounts).reduce((sum, value) => sum + value, 0);
  const generatedRelationOk = categoryNames.every((name) => presented[name] <= generated[name]);

  globalThis.__p1Report = {
    seed: ${seed},
    clientVersion: CLIENT_VERSION,
    targetMeters: ${TARGET_METERS},
    reachedMeters: run.runMeters,
    elapsedSec: run.elapsed,
    frames,
    recognizableWidthPx: ${RECOGNIZABLE_WIDTH_PX},
    generated,
    presented,
    metrics,
    sourceCounts,
    categorySourceCounts,
    presentedTotal,
    sourceTotal,
    invalidSourceCount,
    duplicatePresentationCount,
    maxBlankKmAfter500m,
    maxBlankSecAfter500m,
    maxDecisionBlankSecAfter500m,
    presentedMissTargetCount,
    maxSimultaneousStrongHazards,
    patternStats: {
      started: safeInt(run.patternStartedCount),
      completed: safeInt(run.patternCompletedCount),
      aborted: safeInt(run.patternAbortedCount),
      stepResolved: safeInt(run.patternStepResolvedCount),
      stepSkipped: safeInt(run.patternStepSkippedCount),
      maxConsecutiveSame: safeInt(run.patternMaxConsecutiveSame),
      counts: Object.assign({}, run.patternCounts || {}),
      activePatternName: spawn.activePattern ? spawn.activePattern.name : "",
    },
    generatedRelationOk,
    sourceInvariantOk: sourceTotal === presentedTotal,
    reachedTarget: run.runMeters >= ${TARGET_METERS},
  };
})();`;

  try {
    vm.runInContext(script + appended, sandbox, { timeout: 45000 });
  } catch (error) {
    sandbox.__testState.consoleErrors.push(error && error.stack ? error.stack : String(error));
  }

  return {
    ...sandbox.__p1Report,
    consoleErrors: sandbox.__testState.consoleErrors,
    consoleWarnings: sandbox.__testState.consoleWarnings,
    networkRequests: sandbox.__testState.networkRequests,
  };
}

function runSourceScenarioCoverage(script, seed) {
  const sandbox = createSandbox(seed);
  vm.createContext(sandbox);
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });

  function visible(entity) {
    if (!entity || entity.active === false) return false;
    const width = Math.max(1, Number(entity.w) || 1);
    return entity.x + Math.min(width, ${RECOGNIZABLE_WIDTH_PX}) >= 0 && entity.x < W;
  }

  function countPresentedBySource(source) {
    let count = 0;
    const groups = [holes, obstacles, items];
    for (let g = 0; g < groups.length; g++) {
      for (let i = 0; i < groups[g].length; i++) {
        const entity = groups[g][i];
        if (entity.spawnSource === source && visible(entity) && !entity.__scenarioCounted) {
          entity.__scenarioCounted = true;
          count += 1;
        }
      }
    }
    return count;
  }

  function advanceScenario(maxFrames, source, setup) {
    el.playerName.value = "P1-SOURCE";
    startGame();
    checkCollisions = () => {};
    checkHoleFall = () => false;
    setup();
    let frames = 0;
    let presented = 0;
    while (mode === MODE.PLAYING && frames < maxFrames) {
      __advanceNow(FIXED_STEP * 1000);
      update(FIXED_STEP);
      presented += countPresentedBySource(source);
      if (presented > 0 && source !== SPAWN_SOURCE.INVINCIBLE) break;
      frames += 1;
    }
    return { source, presented, frames, runMeters: run.runMeters };
  }

  const earlyOncoming = advanceScenario(1800, SPAWN_SOURCE.EARLY_ONCOMING, () => {
    run.runMeters = 1500;
    run.maxRunMeters = 1500;
    run.lastNonZeroRunMeters = 1500;
    run.earlyOncomingSpawned = false;
    run.earlyOncomingForceAt = 1.5;
    spawn.nextOncomingAt = 99;
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
  });

  const chase = advanceScenario(1800, SPAWN_SOURCE.CHASE, () => {
    run.runMeters = 2500;
    run.maxRunMeters = 2500;
    run.lastNonZeroRunMeters = 2500;
    run.chase = 15;
    run.elapsed = 2;
    spawn.chaseGraceUntil = 0;
    spawn.nextChaseEventAt = 0;
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
  });

  const invincible = advanceScenario(600, SPAWN_SOURCE.INVINCIBLE, () => {
    run.runMeters = 2500;
    run.maxRunMeters = 2500;
    run.lastNonZeroRunMeters = 2500;
    run.dancerInvincibleUntil = performance.now() + 4000;
    run.forceObstacleDuringInvincibleUntil = performance.now() + 4000;
    run.invincibleObstaclePlanCount = 3;
    run.invincibleObstacleSpawned = 0;
    spawn.nextObstacleAt = 2.5;
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
  });

  globalThis.__p1SourceCoverage = {
    earlyOncoming,
    chase,
    invincible,
    passed: earlyOncoming.presented > 0 && chase.presented > 0 && invincible.presented > 0,
  };
})();`;
  try {
    vm.runInContext(script + appended, sandbox, { timeout: 45000 });
  } catch (error) {
    sandbox.__testState.consoleErrors.push(error && error.stack ? error.stack : String(error));
  }
  return {
    ...sandbox.__p1SourceCoverage,
    consoleErrors: sandbox.__testState.consoleErrors,
    consoleWarnings: sandbox.__testState.consoleWarnings,
  };
}

function validateRun(run) {
  const failures = [];
  if (!run) return ["report missing"];
  if (!run.reachedTarget) failures.push("target distance not reached");
  if (!run.generatedRelationOk) failures.push("presented count exceeds generated count");
  if (!run.sourceInvariantOk) failures.push("spawnSource total does not equal presented total");
  if (run.invalidSourceCount !== 0) failures.push("invalid spawnSource observed");
  if (run.duplicatePresentationCount !== 0) failures.push("entity presented more than once");
  if (run.consoleErrors.length) failures.push(`console errors: ${run.consoleErrors.join(" | ")}`);
  if (run.consoleWarnings.length) failures.push(`console warnings: ${run.consoleWarnings.join(" | ")}`);
  for (const [name, metric] of Object.entries(run.metrics || {})) {
    for (const key of ["count", "totalGapKm", "maxGapKm", "totalGapSec", "maxGapSec", "avgGapKm", "avgGapSec"]) {
      if (!Number.isFinite(metric[key])) failures.push(`${name}.${key} is not finite`);
    }
  }
  return failures;
}

function aggregate(runs) {
  const categoryNames = ["hole", "groundObstacle", "oncoming", "scoreItem", "powerup"];
  const totals = {};
  for (const category of categoryNames) {
    totals[category] = {
      generated: runs.reduce((sum, run) => sum + run.generated[category], 0),
      presented: runs.reduce((sum, run) => sum + run.presented[category], 0),
      maxGapKm: Math.max(...runs.map((run) => run.metrics[category].maxGapKm)),
      maxGapSec: Math.max(...runs.map((run) => run.metrics[category].maxGapSec)),
    };
    totals[category].presentationRate = totals[category].generated
      ? totals[category].presented / totals[category].generated
      : 0;
  }
  return {
    seedCount: runs.length,
    targetMetersPerSeed: TARGET_METERS,
    totals,
    maxBlankKmAfter500m: Math.max(...runs.map((run) => run.maxBlankKmAfter500m)),
    maxBlankSecAfter500m: Math.max(...runs.map((run) => run.maxBlankSecAfter500m)),
    maxSimultaneousStrongHazards: Math.max(...runs.map((run) => run.maxSimultaneousStrongHazards)),
  };
}

if (!fs.existsSync(INDEX_PATH)) {
  console.error(`index.html not found: ${INDEX_PATH}`);
  process.exit(1);
}

const html = fs.readFileSync(INDEX_PATH, "utf8");
const scriptMatch = html.match(/<script>([\s\S]*)<\/script>/);
if (!scriptMatch) {
  console.error("inline script not found in index.html");
  process.exit(1);
}

const runs = SEEDS.map((seed) => runSeed(scriptMatch[1], seed));
const sourceScenarioCoverage = runSourceScenarioCoverage(scriptMatch[1], 17999);
const failures = runs.flatMap((run) => validateRun(run).map((message) => `seed ${run.seed}: ${message}`));
if (!sourceScenarioCoverage.passed) failures.push("scenario source coverage failed");
if (sourceScenarioCoverage.consoleErrors.length) failures.push(`scenario console errors: ${sourceScenarioCoverage.consoleErrors.join(" | ")}`);
if (sourceScenarioCoverage.consoleWarnings.length) failures.push(`scenario console warnings: ${sourceScenarioCoverage.consoleWarnings.join(" | ")}`);
const report = {
  generatedAt: new Date().toISOString(),
  purpose: "P1 effective presentation measurement without gameplay changes",
  definition: {
    presented: "An entity is counted once when at least min(width, 18px) has entered the visible canvas and its left edge is still before the canvas right edge.",
    blankAfter500m: "Maximum distance/time after 0.5km with no newly presented hole, obstacle, item, or powerup.",
    strongHazard: "A visible hole or active ground/oncoming obstacle intersecting the canvas.",
  },
  seeds: SEEDS,
  runs,
  sourceScenarioCoverage,
  aggregate: aggregate(runs),
  failures,
  passed: failures.length === 0,
};

fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
fs.writeFileSync(OUTPUT_PATH, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: report.passed, aggregate: report.aggregate, failures }, null, 2));
process.exit(report.passed ? 0 : 1);
