#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.join(__dirname, "..");
const INDEX_PATH = path.join(ROOT, "index.html");
const OUTPUT_PATH = path.join(ROOT, "artifacts", "p4-air-obstacle-regression.json");
const EXPECTED_VERSION = "kiriganaito-2026-07-20-v20-air-obstacle";
const NATURAL_SEEDS = [20001, 20002, 20003, 20004, 20005];
const TARGET_METERS = 7000;

function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 0x100000000;
  };
}

function makeElement(id) {
  const classes = new Set();
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
    get childNodes() { return this.children; },
    classList: {
      add(name) { classes.add(name); element.className = [...classes].join(" "); },
      remove(name) { classes.delete(name); element.className = [...classes].join(" "); },
      toggle(name) { classes.has(name) ? classes.delete(name) : classes.add(name); element.className = [...classes].join(" "); },
      contains(name) { return classes.has(name); },
    },
    append(...nodes) { this.children.push(...nodes); },
    appendChild(node) { this.children.push(node); return node; },
    replaceChildren(...nodes) { this.children.splice(0, this.children.length, ...nodes); },
    addEventListener(name, handler) { this[`on${name}`] = handler; },
    setAttribute() {},
    getBoundingClientRect() { return { width: 320, height: 360 }; },
  };
  Object.defineProperty(element, "innerHTML", {
    get() { return this.children.map((child) => child.textContent || "").join(""); },
    set(value) { this.children.splice(0); this.textContent = String(value); },
  });
  return element;
}

function createSandbox(seed) {
  const ids = [
    "home", "rules", "name", "game", "result", "error", "gameCanvas", "startBtn", "jumpBtn", "retireBtn",
    "homeRanking", "resultRanking", "homeStats", "resultStats", "homeToast", "playerName", "nameError",
    "hudRun", "hudScore", "hudTime", "hudChase", "hudDanger", "hudChaseBox", "hudDangerBox", "playStatus",
    "resultReason", "resultComment", "resultScore", "resultBreakdown", "rankingStatus", "rankingRetryBtn",
    "clientVersionNote", "homeVersionNote", "resultVersionTop", "debug", "errorText", "homeBtn", "errorHomeBtn",
    "nameBtn", "rulesBtn", "rulesBackBtn", "readyBtn", "shareBtn", "againBtn", "resultHomeBtn",
    "otherGamesResult", "changeNameBtn", "homeShareBtn", "nameStartBtn", "nameBackBtn", "resultShareBtn",
    "retryBtn", "otherGamesHome",
  ];
  const elements = new Map(ids.map((id) => [id, makeElement(id)]));
  const drawCalls = [];
  elements.get("gameCanvas").getContext = () => new Proxy({
    createLinearGradient() { return { addColorStop() {} }; },
    createRadialGradient() { return { addColorStop() {} }; },
    measureText(text) { return { width: String(text).length * 10 }; },
    fillText(text, x, y) { drawCalls.push({ text: String(text), x, y }); },
  }, {
    get(target, property) { if (property in target) return target[property]; return () => {}; },
    set() { return true; },
  });

  const storage = new Map();
  const networkRequests = [];
  const consoleErrors = [];
  const consoleWarnings = [];
  let nowMs = 0;
  const math = Object.create(Math);
  math.random = seededRandom(seed);

  const sandbox = {
    Math: math, Date, JSON, Object, Array, Number, String, Boolean, Set, Map, WeakSet, WeakMap, Promise,
    parseInt, parseFloat, isFinite, TextEncoder, TextDecoder, URL, URLSearchParams, Blob: global.Blob,
    navigator: {}, location: { href: "https://example.invalid/kiriganaito/", search: "" },
    performance: { now: () => nowMs },
    __advanceNow(ms) { nowMs += ms; },
    requestAnimationFrame: () => 0, cancelAnimationFrame: () => {}, setTimeout: () => 0, clearTimeout: () => {},
    devicePixelRatio: 1, addEventListener: () => {},
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
    getElementById(id) { if (!elements.has(id)) elements.set(id, makeElement(id)); return elements.get(id); },
    createElement(tag) { return makeElement(tag); },
    addEventListener() {},
    documentElement: { scrollWidth: 320, clientWidth: 320 },
    body: { scrollWidth: 320, clientWidth: 320 },
  };
  sandbox.__state = { elements, drawCalls, storage, networkRequests, consoleErrors, consoleWarnings };
  return sandbox;
}

function runScript(appScript, seed, appended) {
  const sandbox = createSandbox(seed);
  vm.createContext(sandbox);
  try {
    vm.runInContext(`${appScript}\n${appended}`, sandbox, { timeout: 60000 });
  } catch (error) {
    sandbox.__state.consoleErrors.push(error && error.stack ? error.stack : String(error));
  }
  return sandbox;
}

function directChecks(appScript) {
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });

  function resetAt(km) {
    el.playerName.value = "P4";
    startGame();
    checkHoleFall = () => false;
    run.runMeters = km * 1000;
    run.maxRunMeters = run.runMeters;
    run.lastNonZeroRunMeters = run.runMeters;
    holes = [];
    obstacles = [];
    items = [];
    spawn.lastHoleAt = -9;
    spawn.lastObstacleAt = -9;
    spawn.lastOncomingAt = -9;
    spawn.needObstacleBeforeNextHole = false;
    spawn.activePattern = null;
    run.chase = 0;
    run.dancerInvincibleUntil = 0;
    player.inv = 0;
    player.onGround = true;
    player.y = groundY - player.h;
  }

  resetAt(2.5);
  const metadataSpawn = spawnAirObstaclePattern(2.5, { x: player.x - 8 });
  const metadataEntity = obstacles[0];
  const clearance = airObstacleGroundClearancePx(metadataEntity);
  const metadataErrors = validateWorldEntityMetadata(metadataEntity);
  const groundBeforeDanger = run.danger;
  checkCollisions();
  const groundSafe = run.danger === groundBeforeDanger && metadataEntity.active !== false;

  resetAt(2.5);
  const jumpSpawn = spawnAirObstaclePattern(2.5, { x: player.x - 8 });
  const jumpEntity = obstacles[0];
  player.onGround = false;
  player.y = groundY - 88;
  player.vy = -20;
  const jumpBeforeDanger = run.danger;
  checkCollisions();
  const jumpContact = run.danger === jumpBeforeDanger + 1 && jumpEntity.active === false && run.airObstacleContactCount === 1;

  resetAt(1.99);
  const before2Blocked = spawnAirObstaclePattern(1.99, { x: -76 }) === false;

  resetAt(2.5);
  run.chase = 10;
  const chaseBlocked = spawnAirObstaclePattern(2.5, { x: -76 }) === false;

  resetAt(2.5);
  run.dancerInvincibleUntil = performance.now() + 4000;
  const invincibleBlocked = spawnAirObstaclePattern(2.5, { x: -76 }) === false;

  let geometryFailures = 0;
  let minimumClearance = Infinity;
  for (let i = 0; i < 1000; i++) {
    groundY = 250 + (i % 201);
    player.h = 34;
    player.y = groundY - player.h;
    const entity = { y: groundY - P4_AIR.Y_OFFSET, h: P4_AIR.HEIGHT };
    const value = airObstacleGroundClearancePx(entity);
    minimumClearance = Math.min(minimumClearance, value);
    if (value < P4_AIR.MIN_GROUND_CLEARANCE_PX) geometryFailures++;
  }

  resetAt(2.5);
  holes.push({ x: -80, prevX: -80, y: groundY - 6, w: 30, h: 80, active: true, zone: WORLD_ZONE.HOLE, movementType: MOVEMENT_TYPE.WORLD_SCROLL, objectRole: OBJECT_ROLE.TERRAIN, heightBand: HEIGHT_BAND.GROUND, spawnSource: SPAWN_SOURCE.NORMAL });
  const holeConflictBlocked = canSpawnAirObstacle(2.5) === false;

  resetAt(2.5);
  obstacles.push({ x: -60, y: groundY - 32, w: 32, h: 32, active: true, direction: -1, speed: 1, emoji: "🚶", zone: WORLD_ZONE.GROUND, movementType: MOVEMENT_TYPE.WORLD_SCROLL, objectRole: OBJECT_ROLE.HAZARD, heightBand: HEIGHT_BAND.GROUND, spawnSource: SPAWN_SOURCE.NORMAL });
  const groundConflictBlocked = canSpawnAirObstacle(2.5) === false;

  globalThis.__p4Direct = {
    clientVersion: CLIENT_VERSION,
    metadataSpawn,
    metadata: metadataEntity && {
      zone: metadataEntity.zone,
      movementType: metadataEntity.movementType,
      objectRole: metadataEntity.objectRole,
      heightBand: metadataEntity.heightBand,
      spawnSource: metadataEntity.spawnSource,
      airKind: metadataEntity.airKind,
    },
    metadataErrors,
    clearance,
    groundSafe,
    jumpSpawn,
    jumpContact,
    before2Blocked,
    chaseBlocked,
    invincibleBlocked,
    geometryFailures,
    minimumClearance,
    holeConflictBlocked,
    groundConflictBlocked,
  };
})();`;
  const sandbox = runScript(appScript, 20000, appended);
  return { ...sandbox.__p4Direct, consoleErrors: sandbox.__state.consoleErrors, consoleWarnings: sandbox.__state.consoleWarnings };
}

function naturalRun(appScript, seed) {
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "AIR-${seed}";
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;
  let visibleAir = 0;
  const counted = new Set();
  let maxSimultaneousGroundAndAir = 0;
  let frames = 0;
  while (mode === MODE.PLAYING && run.runMeters < ${TARGET_METERS} && frames < 260000) {
    __advanceNow(FIXED_STEP * 1000);
    update(FIXED_STEP);
    let airVisibleNow = 0;
    let groundVisibleNow = 0;
    for (const entity of obstacles) {
      if (entity.active === false || !(entity.x < W && entity.x + entity.w > 0)) continue;
      if (entity.zone === WORLD_ZONE.AIR) {
        airVisibleNow++;
        if (!counted.has(entity)) { counted.add(entity); visibleAir++; }
      } else groundVisibleNow++;
    }
    for (const hole of holes) if (hole.x < W && hole.x + hole.w > 0) groundVisibleNow++;
    if (airVisibleNow > 0 && groundVisibleNow > 0) maxSimultaneousGroundAndAir = Math.max(maxSimultaneousGroundAndAir, airVisibleNow + groundVisibleNow);
    frames++;
  }
  globalThis.__p4Natural = {
    seed: ${seed},
    reachedMeters: run.runMeters,
    airObstacleSpawnCount: run.airObstacleSpawnCount,
    airObstacleBefore2kmCount: run.airObstacleBefore2kmCount,
    airObstacleChaseSpawnCount: run.airObstacleChaseSpawnCount,
    airObstacleFullBlockViolationCount: run.airObstacleFullBlockViolationCount,
    airObstacleFirstSpawnKm: run.airObstacleFirstSpawnKm,
    visibleAir,
    maxSimultaneousGroundAndAir,
    queueOverflow: run.spawnQueueOverflowCount,
    mandatoryTimeout: run.spawnMandatoryTimeoutCount,
    unavoidableOncomingCount: run.unavoidableOncomingCount,
    consecutiveHoleViolationCount: run.consecutiveHoleViolationCount,
    patternAbortedCount: run.patternAbortedCount,
    reachedTarget: run.runMeters >= ${TARGET_METERS},
  };
})();`;
  const sandbox = runScript(appScript, seed, appended);
  return { ...sandbox.__p4Natural, consoleErrors: sandbox.__state.consoleErrors, consoleWarnings: sandbox.__state.consoleWarnings };
}

function validateDirect(check) {
  const failures = [];
  if (check.clientVersion !== EXPECTED_VERSION) failures.push("client version mismatch");
  if (!check.metadataSpawn) failures.push("direct air obstacle spawn failed");
  if (check.metadataErrors && check.metadataErrors.length) failures.push(`metadata errors: ${check.metadataErrors.join(" | ")}`);
  const meta = check.metadata || {};
  if (meta.zone !== "air" || meta.movementType !== "world_scroll" || meta.objectRole !== "hazard" || meta.heightBand !== "mid" || meta.spawnSource !== "normal") failures.push("metadata classification mismatch");
  if (meta.airKind !== "hanging_bar") failures.push("airKind mismatch");
  if (!(check.clearance >= 12)) failures.push(`ground clearance too small: ${check.clearance}`);
  if (!check.groundSafe) failures.push("ground state collided with air obstacle");
  if (!check.jumpContact) failures.push("jump state did not collide with air obstacle");
  if (!check.before2Blocked) failures.push("air obstacle spawned before 2km");
  if (!check.chaseBlocked) failures.push("air obstacle spawned during chase");
  if (!check.invincibleBlocked) failures.push("air obstacle spawned during invincible mode");
  if (check.geometryFailures !== 0) failures.push(`1000 geometry placements failed: ${check.geometryFailures}`);
  if (!check.holeConflictBlocked) failures.push("hole conflict was not blocked");
  if (!check.groundConflictBlocked) failures.push("ground hazard conflict was not blocked");
  if (check.consoleErrors.length) failures.push(`direct console errors: ${check.consoleErrors.join(" | ")}`);
  if (check.consoleWarnings.length) failures.push(`direct console warnings: ${check.consoleWarnings.join(" | ")}`);
  return failures;
}

function validateNatural(run) {
  const failures = [];
  if (!run.reachedTarget) failures.push("target distance not reached");
  if (run.airObstacleSpawnCount < 2 || run.airObstacleSpawnCount > 8) failures.push(`air obstacle count outside low-frequency range: ${run.airObstacleSpawnCount}`);
  if (run.visibleAir !== run.airObstacleSpawnCount) failures.push(`visible/spawn mismatch: ${run.visibleAir}/${run.airObstacleSpawnCount}`);
  if (run.airObstacleBefore2kmCount !== 0) failures.push("air obstacle before 2km");
  if (run.airObstacleChaseSpawnCount !== 0) failures.push("air obstacle spawned during chase");
  if (run.airObstacleFullBlockViolationCount !== 0) failures.push("full-block violation recorded");
  if (!(run.airObstacleFirstSpawnKm >= 2)) failures.push(`first spawn before 2km: ${run.airObstacleFirstSpawnKm}`);
  if (run.maxSimultaneousGroundAndAir !== 0) failures.push(`visible ground+air overlap: ${run.maxSimultaneousGroundAndAir}`);
  if (run.queueOverflow !== 0) failures.push(`queue overflow: ${run.queueOverflow}`);
  if (run.mandatoryTimeout !== 0) failures.push(`mandatory timeout: ${run.mandatoryTimeout}`);
  if (run.unavoidableOncomingCount !== 0) failures.push(`unavoidable oncoming: ${run.unavoidableOncomingCount}`);
  if (run.consecutiveHoleViolationCount !== 0) failures.push(`consecutive hole violation: ${run.consecutiveHoleViolationCount}`);
  if (run.consoleErrors.length) failures.push(`console errors: ${run.consoleErrors.join(" | ")}`);
  if (run.consoleWarnings.length) failures.push(`console warnings: ${run.consoleWarnings.join(" | ")}`);
  return failures;
}

if (!fs.existsSync(INDEX_PATH)) {
  console.error(`index.html not found: ${INDEX_PATH}`);
  process.exit(1);
}
const html = fs.readFileSync(INDEX_PATH, "utf8");
const match = html.match(/<script>([\s\S]*)<\/script>/);
if (!match) {
  console.error("inline script not found");
  process.exit(1);
}
const appScript = match[1];
const direct = directChecks(appScript);
const naturalRuns = NATURAL_SEEDS.map((seed) => naturalRun(appScript, seed));
const failures = validateDirect(direct);
for (const run of naturalRuns) {
  for (const failure of validateNatural(run)) failures.push(`seed ${run.seed}: ${failure}`);
}
const report = {
  generatedAt: new Date().toISOString(),
  clientVersion: EXPECTED_VERSION,
  purpose: "P4 first airborne obstacle and jump/no-jump decision regression",
  direct,
  naturalSeeds: NATURAL_SEEDS,
  naturalRuns,
  aggregate: {
    minSpawnCount: Math.min(...naturalRuns.map((run) => run.airObstacleSpawnCount)),
    maxSpawnCount: Math.max(...naturalRuns.map((run) => run.airObstacleSpawnCount)),
    totalSpawnCount: naturalRuns.reduce((sum, run) => sum + run.airObstacleSpawnCount, 0),
    maximumGroundAirOverlap: Math.max(...naturalRuns.map((run) => run.maxSimultaneousGroundAndAir)),
  },
  failures,
  passed: failures.length === 0,
};
fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
fs.writeFileSync(OUTPUT_PATH, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: report.passed, aggregate: report.aggregate, failures }, null, 2));
process.exit(report.passed ? 0 : 1);
