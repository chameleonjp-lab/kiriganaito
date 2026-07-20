#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.join(__dirname, "..");
const INDEX_PATH = path.join(ROOT, "index.html");
const OUTPUT_PATH = path.join(ROOT, "artifacts", "p5-chase-invincible-regression.json");
const EXPECTED_VERSION = "kiriganaito-2026-07-21-v24-ui-finish";
const CHASE_SEEDS = [21001, 21002, 21003, 21004, 21005];

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
  const listeners = new Map();

  const sandbox = {
    Math: math, Date, JSON, Object, Array, Number, String, Boolean, Set, Map, WeakSet, WeakMap, Promise,
    parseInt, parseFloat, isFinite, TextEncoder, TextDecoder, URL, URLSearchParams, Blob: global.Blob,
    navigator: {}, location: { href: "https://example.invalid/kiriganaito/", search: "" },
    performance: { now: () => nowMs },
    __advanceNow(ms) { nowMs += ms; },
    requestAnimationFrame: () => 0, cancelAnimationFrame: () => {}, setTimeout: () => 0, clearTimeout: () => {},
    devicePixelRatio: 1,
    addEventListener(name, handler) { listeners.set(name, handler); },
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
    hidden: false,
    visibilityState: "visible",
    getElementById(id) { if (!elements.has(id)) elements.set(id, makeElement(id)); return elements.get(id); },
    createElement(tag) { return makeElement(tag); },
    addEventListener(name, handler) { listeners.set(`document:${name}`, handler); },
    documentElement: { scrollWidth: 320, clientWidth: 320 },
    body: { scrollWidth: 320, clientWidth: 320 },
  };
  sandbox.__state = { elements, drawCalls, storage, networkRequests, consoleErrors, consoleWarnings, listeners };
  return sandbox;
}

function runScript(appScript, seed, appended) {
  const sandbox = createSandbox(seed);
  vm.createContext(sandbox);
  try {
    vm.runInContext(`${appScript}\n${appended}`, sandbox, { timeout: 90000 });
  } catch (error) {
    sandbox.__state.consoleErrors.push(error && error.stack ? error.stack : String(error));
  }
  return sandbox;
}

function chaseScenario(appScript, seed, startKm) {
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "P5-CHASE-${seed}";
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;
  run.runMeters = ${startKm} * 1000;
  run.maxRunMeters = run.runMeters;
  run.lastNonZeroRunMeters = run.runMeters;
  run.danger = 1;
  holes = [];
  obstacles = [];
  items = [];
  particles = [];
  spawn.requests = { ground: [], air: [], hole: [] };
  spawn.needObstacleBeforeNextHole = false;
  spawn.activePattern = null;
  spawn.lastHoleAt = -9;
  spawn.lastObstacleAt = -9;
  spawn.lastOncomingAt = -9;
  spawn.lastScoreItemAt = -9;
  spawn.nextHoleAt = ${startKm} + 9;
  spawn.nextObstacleAt = ${startKm} + 9;
  spawn.nextOncomingAt = ${startKm} + 9;
  spawn.nextScoreItemAt = ${startKm} + 9;
  spawn.nextItemAt = ${startKm} + 9;
  run.nextDancerAt = ${startKm} + 9;
  startP5ChaseSession(${startKm});

  const seen = new Set();
  const visibleCounts = { ground: 0, holes: 0, scoreItems: 0, oncoming: 0, powerups: 0 };
  let graceP5Hazards = 0;
  let frames = 0;
  let chaseEndElapsed = null;
  let maxVisibleHazards = 0;

  function recognizable(entity) {
    if (!entity || entity.active === false) return false;
    const width = Math.max(1, Number(entity.w) || 1);
    return entity.x + Math.min(width, 18) >= 0 && entity.x < W;
  }
  function countEntity(entity) {
    if (!entity || seen.has(entity) || !recognizable(entity)) return;
    if (entity.p5ChaseSessionId !== run.chaseSessionId) return;
    seen.add(entity);
    if (entity.zone === WORLD_ZONE.HOLE) visibleCounts.holes++;
    else if (entity.objectRole === OBJECT_ROLE.POWERUP) visibleCounts.powerups++;
    else if (entity.objectRole === OBJECT_ROLE.REWARD) visibleCounts.scoreItems++;
    else if (entity.movementType === MOVEMENT_TYPE.ONCOMING) visibleCounts.oncoming++;
    else if (entity.objectRole === OBJECT_ROLE.HAZARD && entity.zone === WORLD_ZONE.GROUND) visibleCounts.ground++;
    if (getP5ChaseElapsedSec() < 1 && (entity.zone === WORLD_ZONE.HOLE || entity.objectRole === OBJECT_ROLE.HAZARD)) graceP5Hazards++;
  }

  while (mode === MODE.PLAYING && (run.chaseSessionActive || run.chase > 0) && frames < 3000) {
    __advanceNow(FIXED_STEP * 1000);
    update(FIXED_STEP);
    for (const entity of holes) countEntity(entity);
    for (const entity of obstacles) countEntity(entity);
    for (const entity of items) countEntity(entity);
    const visibleHazards = holes.filter(recognizable).length + obstacles.filter((entity) => recognizable(entity) && entity.objectRole === OBJECT_ROLE.HAZARD).length;
    maxVisibleHazards = Math.max(maxVisibleHazards, visibleHazards);
    frames++;
    if (!run.chaseSessionActive && run.chase <= 0) chaseEndElapsed = frames * FIXED_STEP;
  }

  globalThis.__p5Chase = {
    seed: ${seed},
    startKm: ${startKm},
    clientVersion: CLIENT_VERSION,
    frames,
    chaseEndElapsed,
    chaseRemaining: run.chase,
    chaseSessionActive: run.chaseSessionActive,
    completedSessions: run.chaseCompletedSessionCount,
    phase: run.chasePhase,
    visibleCounts,
    sessionSummary: run.chaseLastSessionSummary,
    sessionGroundCount: run.chaseSessionGroundCount,
    sessionHoleCount: run.chaseSessionHoleCount,
    sessionScoreItemCount: run.chaseSessionScoreItemCount,
    sessionOncomingCount: run.chaseSessionOncomingCount,
    maxDecisionBlankSec: run.chaseSessionMaxDecisionBlankSec,
    graceP5Hazards,
    graceViolationCounter: run.chaseGraceHazardViolationCount,
    countRangeViolationCounter: run.chaseCountRangeViolationCount,
    unavoidableOncomingCount: run.unavoidableOncomingCount,
    consecutiveHoleViolationCount: run.consecutiveHoleViolationCount,
    dancerAdded: run.dancerSpawnCount - run.chaseSessionStartDancerSpawnCount,
    maxVisibleHazards,
    remainingP5Requests: [WORLD_ZONE.GROUND, WORLD_ZONE.AIR, WORLD_ZONE.HOLE].reduce((sum, zone) => sum + spawnRequestQueue(zone).filter((req) => req.p5ChaseSessionId).length, 0),
  };
})();`;
  const sandbox = runScript(appScript, seed, appended);
  return {
    ...sandbox.__p5Chase,
    consoleErrors: sandbox.__state.consoleErrors,
    consoleWarnings: sandbox.__state.consoleWarnings,
    networkRequests: sandbox.__state.networkRequests,
  };
}

function invincibleTimingScenario(appScript, seed, startKm) {
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "P5-INV-TIME";
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;
  run.runMeters = ${startKm} * 1000;
  run.maxRunMeters = run.runMeters;
  run.lastNonZeroRunMeters = run.runMeters;
  activateDancerInvincible();
  const initial = getDancerInvincibleRemainingSec();
  __advanceNow(30000);
  const afterWallClockOnly = getDancerInvincibleRemainingSec();
  for (let i = 0; i < 120; i++) updateDancerInvincible(FIXED_STEP);
  const afterTwoPlayedSeconds = getDancerInvincibleRemainingSec();
  run.runMeters = 25 * 1000;
  run.maxRunMeters = run.runMeters;
  for (let i = 0; i < 120; i++) updateDancerInvincible(FIXED_STEP);
  const afterFourPlayedSeconds = getDancerInvincibleRemainingSec();
  for (let i = 0; i < 240; i++) updateDancerInvincible(FIXED_STEP);
  const afterEightPlayedSeconds = getDancerInvincibleRemainingSec();
  const blockUntil = run.invincibleLargeHoleBlockUntilKm;
  const currentKm = run.runMeters / 1000;
  const blockedKind = normalizeHoleKindForP5("LARGE", currentKm);
  const releasedKind = normalizeHoleKindForP5("LARGE", blockUntil + 0.001);
  globalThis.__p5InvTiming = {
    clientVersion: CLIENT_VERSION,
    initial,
    afterWallClockOnly,
    afterTwoPlayedSeconds,
    afterFourPlayedSeconds,
    afterEightPlayedSeconds,
    blockUntil,
    currentKm,
    blockedKind,
    releasedKind,
    sessionCount: run.invincibleSessionCount,
    backgroundViolationCount: run.invincibleBackgroundDecayViolationCount,
  };
})();`;
  const sandbox = runScript(appScript, seed, appended);
  return {
    ...sandbox.__p5InvTiming,
    consoleErrors: sandbox.__state.consoleErrors,
    consoleWarnings: sandbox.__state.consoleWarnings,
  };
}

function invinciblePresentationScenario(appScript, seed) {
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "P5-INV-PRESENT";
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;
  run.runMeters = 2500;
  run.maxRunMeters = 2500;
  run.lastNonZeroRunMeters = 2500;
  holes = [];
  obstacles = [];
  items = [];
  particles = [];
  spawn.requests = { ground: [], air: [], hole: [] };
  spawn.needObstacleBeforeNextHole = false;
  spawn.activePattern = null;
  spawn.lastHoleAt = -9;
  spawn.lastObstacleAt = -9;
  spawn.lastOncomingAt = -9;
  spawn.nextHoleAt = 99;
  spawn.nextObstacleAt = 99;
  spawn.nextOncomingAt = 99;
  spawn.nextScoreItemAt = 99;
  spawn.nextItemAt = 99;
  run.nextDancerAt = 99;
  activateDancerInvincible();
  const planned = run.invincibleObstaclePlanCount;
  const seen = new Set();
  let visibleInvincibleObstacles = 0;
  let frames = 0;
  while (mode === MODE.PLAYING && (isDancerInvincible() || hasPendingInvincibleRequest()) && frames < 1500) {
    __advanceNow(FIXED_STEP * 1000);
    update(FIXED_STEP);
    for (const entity of obstacles) {
      if (entity.p5InvincibleSessionId !== run.invincibleSessionId || seen.has(entity)) continue;
      const width = Math.max(1, Number(entity.w) || 1);
      if (entity.active !== false && entity.x + Math.min(width, 18) >= 0 && entity.x < W) {
        seen.add(entity);
        visibleInvincibleObstacles++;
      }
    }
    frames++;
  }
  globalThis.__p5InvPresentation = {
    planned,
    visibleInvincibleObstacles,
    sessionPresented: run.invincibleSessionPresentedObstacleCount,
    totalPresented: run.invinciblePresentedObstacleCount,
    invincibleRemaining: getDancerInvincibleRemainingSec(),
    pendingRequest: hasPendingInvincibleRequest(),
    frames,
    largeHoleBlockUntilKm: run.invincibleLargeHoleBlockUntilKm,
  };
})();`;
  const sandbox = runScript(appScript, seed, appended);
  return {
    ...sandbox.__p5InvPresentation,
    consoleErrors: sandbox.__state.consoleErrors,
    consoleWarnings: sandbox.__state.consoleWarnings,
  };
}

function invincibleCollisionScenario(appScript, seed) {
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "P5-INV-COLLISION";
  startGame();
  checkHoleFall = () => false;
  run.runMeters = 2500;
  run.maxRunMeters = 2500;
  activateDancerInvincible();
  obstacles = [{
    x: player.x,
    y: groundY - 32,
    emoji: "🚶",
    speed: 1,
    direction: -1,
    w: 32,
    h: 32,
    active: true,
    zone: WORLD_ZONE.GROUND,
    movementType: MOVEMENT_TYPE.WORLD_SCROLL,
    objectRole: OBJECT_ROLE.HAZARD,
    heightBand: HEIGHT_BAND.GROUND,
    spawnSource: SPAWN_SOURCE.NORMAL,
  }];
  const beforeDanger = run.danger;
  const beforePrevented = run.invinciblePreventedAccidents;
  checkCollisions();
  const obstacleActiveAfter = obstacles[0] && obstacles[0].active;
  const breakthroughTexts = particles.filter((particle) => particle.text === "無敵で突破!").length;
  globalThis.__p5InvCollision = {
    dangerUnchanged: run.danger === beforeDanger,
    preventedDelta: run.invinciblePreventedAccidents - beforePrevented,
    obstacleActiveAfter,
    breakthroughTexts,
    breakthroughFlash: run.invincibleBreakthroughFlash,
  };
})();`;
  const sandbox = runScript(appScript, seed, appended);
  return {
    ...sandbox.__p5InvCollision,
    consoleErrors: sandbox.__state.consoleErrors,
    consoleWarnings: sandbox.__state.consoleWarnings,
  };
}

function invincibleHoleScenario(appScript, seed) {
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "P5-INV-HOLE";
  startGame();
  run.runMeters = 2500;
  run.maxRunMeters = 2500;
  activateDancerInvincible();
  const holeX = player.x - 10;
  holes = [{
    x: holeX,
    prevX: holeX,
    y: groundY - 6,
    w: player.w + 20,
    h: H - groundY + 14,
    kind: "SMALL",
    active: true,
    zone: WORLD_ZONE.HOLE,
    movementType: MOVEMENT_TYPE.WORLD_SCROLL,
    objectRole: OBJECT_ROLE.TERRAIN,
    heightBand: HEIGHT_BAND.GROUND,
    spawnSource: SPAWN_SOURCE.NORMAL,
  }];
  player.y = groundY - player.h;
  player.vy = 0;
  player.onGround = true;
  const fell = checkHoleFall();
  globalThis.__p5InvHole = {
    fell,
    mode,
    reason: run.finishReason,
    invincibleRemaining: getDancerInvincibleRemainingSec(),
  };
})();`;
  const sandbox = runScript(appScript, seed, appended);
  return {
    ...sandbox.__p5InvHole,
    consoleErrors: sandbox.__state.consoleErrors,
    consoleWarnings: sandbox.__state.consoleWarnings,
  };
}

function validateChase(run) {
  const failures = [];
  if (!run) return ["missing chase report"];
  if (run.clientVersion !== EXPECTED_VERSION) failures.push("client version mismatch");
  if (!(run.chaseEndElapsed >= 14.98 && run.chaseEndElapsed <= 15.05)) failures.push(`chase duration mismatch: ${run.chaseEndElapsed}`);
  if (run.chaseRemaining !== 0 || run.chaseSessionActive) failures.push("chase did not complete cleanly");
  if (run.completedSessions !== 1) failures.push(`completed session count: ${run.completedSessions}`);
  if (run.phase !== "idle") failures.push(`final phase: ${run.phase}`);
  if (run.graceP5Hazards !== 0 || run.graceViolationCounter !== 0) failures.push(`grace hazard violation: ${run.graceP5Hazards}/${run.graceViolationCounter}`);
  if (run.visibleCounts.ground < 5 || run.visibleCounts.ground > 8) failures.push(`visible ground outside range: ${run.visibleCounts.ground}`);
  if (run.visibleCounts.holes < 2 || run.visibleCounts.holes > 4) failures.push(`visible holes outside range: ${run.visibleCounts.holes}`);
  if (run.visibleCounts.scoreItems < 4 || run.visibleCounts.scoreItems > 7) failures.push(`visible score items outside range: ${run.visibleCounts.scoreItems}`);
  if (run.startKm >= 2) {
    if (run.visibleCounts.oncoming < 1 || run.visibleCounts.oncoming > 3) failures.push(`visible oncoming outside range: ${run.visibleCounts.oncoming}`);
  } else if (run.visibleCounts.oncoming !== 0) failures.push(`oncoming below 2km: ${run.visibleCounts.oncoming}`);
  if (run.visibleCounts.powerups !== 0 || run.dancerAdded !== 0) failures.push(`powerup added during chase: ${run.visibleCounts.powerups}/${run.dancerAdded}`);
  if (!(run.maxDecisionBlankSec <= 0.70 + 1e-9)) failures.push(`decision blank too long: ${run.maxDecisionBlankSec}`);
  if (run.countRangeViolationCounter !== 0) failures.push(`count range violation: ${run.countRangeViolationCounter}`);
  if (run.unavoidableOncomingCount !== 0) failures.push(`unavoidable oncoming: ${run.unavoidableOncomingCount}`);
  if (run.consecutiveHoleViolationCount !== 0) failures.push(`consecutive hole violation: ${run.consecutiveHoleViolationCount}`);
  if (run.remainingP5Requests !== 0) failures.push(`orphan P5 requests: ${run.remainingP5Requests}`);
  if (run.consoleErrors.length) failures.push(`console errors: ${run.consoleErrors.join(" | ")}`);
  if (run.consoleWarnings.length) failures.push(`console warnings: ${run.consoleWarnings.join(" | ")}`);
  return failures;
}

function validateInvincibleTiming(run) {
  const failures = [];
  if (run.clientVersion !== EXPECTED_VERSION) failures.push("timing client version mismatch");
  if (Math.abs(run.initial - 8) > 1e-9) failures.push(`initial duration: ${run.initial}`);
  if (Math.abs(run.afterWallClockOnly - 8) > 1e-9) failures.push(`wall-clock decay: ${run.afterWallClockOnly}`);
  if (Math.abs(run.afterTwoPlayedSeconds - 6) > 1e-6) failures.push(`two-second duration: ${run.afterTwoPlayedSeconds}`);
  if (Math.abs(run.afterFourPlayedSeconds - 4) > 1e-6) failures.push(`four-second duration: ${run.afterFourPlayedSeconds}`);
  if (run.afterEightPlayedSeconds > 1e-6) failures.push(`eight-second duration: ${run.afterEightPlayedSeconds}`);
  if (!(run.blockUntil > run.currentKm)) failures.push(`large-hole block not set: ${run.blockUntil}/${run.currentKm}`);
  if (run.blockedKind !== "MEDIUM") failures.push(`large hole not blocked: ${run.blockedKind}`);
  if (run.releasedKind !== "LARGE") failures.push(`large hole not released: ${run.releasedKind}`);
  if (run.sessionCount !== 1) failures.push(`invincible session count: ${run.sessionCount}`);
  if (run.backgroundViolationCount !== 0) failures.push(`background violation count: ${run.backgroundViolationCount}`);
  if (run.consoleErrors.length) failures.push(`timing console errors: ${run.consoleErrors.join(" | ")}`);
  if (run.consoleWarnings.length) failures.push(`timing console warnings: ${run.consoleWarnings.join(" | ")}`);
  return failures;
}

function validateInvinciblePresentation(run) {
  const failures = [];
  if (run.planned < 2 || run.planned > 3) failures.push(`supplement request plan: ${run.planned}`);
  if (run.visibleInvincibleObstacles < 4 || run.visibleInvincibleObstacles > 6) failures.push(`visible invincible obstacles: ${run.visibleInvincibleObstacles}`);
  if (run.visibleInvincibleObstacles < run.planned) failures.push(`visible count below supplement plan: ${run.visibleInvincibleObstacles}/${run.planned}`);
  if (run.sessionPresented !== run.visibleInvincibleObstacles) failures.push(`session/visible mismatch: ${run.sessionPresented}/${run.visibleInvincibleObstacles}`);
  if (run.invincibleRemaining > 1e-6) failures.push(`invincible still active: ${run.invincibleRemaining}`);
  if (run.pendingRequest) failures.push("pending invincible request remains");
  if (run.consoleErrors.length) failures.push(`presentation console errors: ${run.consoleErrors.join(" | ")}`);
  if (run.consoleWarnings.length) failures.push(`presentation console warnings: ${run.consoleWarnings.join(" | ")}`);
  return failures;
}

function validateCollision(run) {
  const failures = [];
  if (!run.dangerUnchanged) failures.push("danger changed during invincible collision");
  if (run.preventedDelta !== 1) failures.push(`prevented accident delta: ${run.preventedDelta}`);
  if (run.obstacleActiveAfter !== false) failures.push("obstacle remained active after breakthrough");
  if (run.breakthroughTexts !== 1) failures.push(`breakthrough text count: ${run.breakthroughTexts}`);
  if (!(run.breakthroughFlash > 0)) failures.push("breakthrough flash not set");
  if (run.consoleErrors.length) failures.push(`collision console errors: ${run.consoleErrors.join(" | ")}`);
  if (run.consoleWarnings.length) failures.push(`collision console warnings: ${run.consoleWarnings.join(" | ")}`);
  return failures;
}

function validateHole(run) {
  const failures = [];
  if (!run.fell) failures.push("invincible hole did not trigger fall");
  if (run.mode !== "RESULT") failures.push(`hole mode: ${run.mode}`);
  if (run.reason !== "穴に落ちました") failures.push(`hole reason: ${run.reason}`);
  if (!(run.invincibleRemaining > 0)) failures.push("invincibility unexpectedly ended before hole result");
  if (run.consoleErrors.length) failures.push(`hole console errors: ${run.consoleErrors.join(" | ")}`);
  if (run.consoleWarnings.length) failures.push(`hole console warnings: ${run.consoleWarnings.join(" | ")}`);
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
const chaseRuns = CHASE_SEEDS.map((seed) => chaseScenario(appScript, seed, 2.5));
const pre2kmChase = chaseScenario(appScript, 21999, 1.2);
const invincibleTiming = invincibleTimingScenario(appScript, 22001, 2.5);
const invinciblePresentation = invinciblePresentationScenario(appScript, 22002);
const invincibleCollision = invincibleCollisionScenario(appScript, 22003);
const invincibleHole = invincibleHoleScenario(appScript, 22004);
const failures = [];
for (const run of chaseRuns) for (const failure of validateChase(run)) failures.push(`seed ${run.seed}: ${failure}`);
for (const failure of validateChase(pre2kmChase)) failures.push(`pre2km: ${failure}`);
for (const failure of validateInvincibleTiming(invincibleTiming)) failures.push(`invincible timing: ${failure}`);
for (const failure of validateInvinciblePresentation(invinciblePresentation)) failures.push(`invincible presentation: ${failure}`);
for (const failure of validateCollision(invincibleCollision)) failures.push(`invincible collision: ${failure}`);
for (const failure of validateHole(invincibleHole)) failures.push(`invincible hole: ${failure}`);
const realSupabaseRequests = [...chaseRuns, pre2kmChase]
  .flatMap((run) => run.networkRequests || [])
  .filter((request) => request.url.includes("submit_score"));
if (realSupabaseRequests.length) failures.push(`real Supabase submissions: ${realSupabaseRequests.length}`);

const report = {
  generatedAt: new Date().toISOString(),
  clientVersion: EXPECTED_VERSION,
  purpose: "P5 chase phases and played-time invincibility regression",
  chaseSeeds: CHASE_SEEDS,
  chaseRuns,
  pre2kmChase,
  invincibleTiming,
  invinciblePresentation,
  invincibleCollision,
  invincibleHole,
  aggregate: {
    minGround: Math.min(...chaseRuns.map((run) => run.visibleCounts.ground)),
    maxGround: Math.max(...chaseRuns.map((run) => run.visibleCounts.ground)),
    minHoles: Math.min(...chaseRuns.map((run) => run.visibleCounts.holes)),
    maxHoles: Math.max(...chaseRuns.map((run) => run.visibleCounts.holes)),
    minScoreItems: Math.min(...chaseRuns.map((run) => run.visibleCounts.scoreItems)),
    maxScoreItems: Math.max(...chaseRuns.map((run) => run.visibleCounts.scoreItems)),
    minOncoming: Math.min(...chaseRuns.map((run) => run.visibleCounts.oncoming)),
    maxOncoming: Math.max(...chaseRuns.map((run) => run.visibleCounts.oncoming)),
    maxDecisionBlankSec: Math.max(...chaseRuns.map((run) => run.maxDecisionBlankSec)),
  },
  failures,
  passed: failures.length === 0,
};
fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
fs.writeFileSync(OUTPUT_PATH, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: report.passed, aggregate: report.aggregate, failures }, null, 2));
process.exit(report.passed ? 0 : 1);
