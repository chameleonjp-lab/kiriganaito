#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const scriptMatch = html.match(/<script>([\s\S]*)<\/script>/);
if (!scriptMatch) {
  console.error("inline script not found");
  process.exit(1);
}
const script = scriptMatch[1];

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
      toggle(name) { if (classes.has(name)) classes.delete(name); else classes.add(name); element.className = [...classes].join(" "); },
      contains(name) { return classes.has(name); },
    },
    append(...nodes) { this.children.push(...nodes); },
    appendChild(node) { this.children.push(node); return node; },
    replaceChildren(...nodes) { this.children.splice(0, this.children.length, ...nodes); },
    addEventListener(name, fn) { this[`on${name}`] = fn; },
    setAttribute() {},
    getBoundingClientRect() { return { width: 320, height: 360 }; },
  };
  Object.defineProperty(element, "innerHTML", {
    get() { return this.children.map((child) => child.textContent || "").join(""); },
    set(value) { this.children.splice(0); this.textContent = String(value); },
  });
  return element;
}

function context() {
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
  elements.get("gameCanvas").getContext = () => new Proxy({
    createLinearGradient() { return { addColorStop() {} }; },
    createRadialGradient() { return { addColorStop() {} }; },
    measureText(text) { return { width: String(text).length * 10 }; },
  }, {
    get(target, property) { return property in target ? target[property] : () => {}; },
    set() { return true; },
  });
  const store = new Map();
  const errors = [];
  const warnings = [];
  global.window = global;
  global.addEventListener = () => {};
  global.setTimeout = () => 0;
  global.clearTimeout = () => {};
  global.document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, makeElement(id));
      return elements.get(id);
    },
    createElement(tag) { return makeElement(tag); },
    addEventListener() {},
    documentElement: { scrollWidth: 320, clientWidth: 320 },
    body: { scrollWidth: 320, clientWidth: 320 },
  };
  global.localStorage = {
    getItem(key) { return store.has(key) ? store.get(key) : null; },
    setItem(key, value) { store.set(key, String(value)); },
    removeItem(key) { store.delete(key); },
  };
  global.performance = { now: () => 0 };
  global.requestAnimationFrame = () => 0;
  global.cancelAnimationFrame = () => {};
  global.devicePixelRatio = 1;
  global.fetch = async () => ({ ok: false, status: 599, json: async () => ({ mock: true }) });
  global.console = {
    ...console,
    error: (...args) => errors.push(args.join(" ")),
    warn: (...args) => warnings.push(args.join(" ")),
  };
  return { elements, errors, warnings };
}

const ctx = context();
const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "P3";
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;
  run.nextDancerAt = 0;
  spawn.patternBag = [];
  spawn.patternBagKey = "";
  run.patternHistory = [];
  run.patternCounts = {};
  run.patternCurrentConsecutiveSame = 0;
  run.patternMaxConsecutiveSame = 0;

  const definitionErrors = validateDecisionPatternDefinitions();
  const learning = availableDecisionPatterns(0.5).map((def) => def.name);
  const advanced = availableDecisionPatterns(2.5).map((def) => def.name);
  const selections = [];
  const selectionCounts = {};
  let tripleRepeatCount = 0;
  for (let i = 0; i < 10000; i++) {
    const selected = selectNextDecisionPattern(2.5, true);
    const name = selected && selected.name;
    selections.push(name);
    selectionCounts[name] = (selectionCounts[name] || 0) + 1;
    if (i >= 2 && selections[i - 1] === name && selections[i - 2] === name) tripleRepeatCount += 1;
  }
  const maxSelectionShare = Math.max(...Object.values(selectionCounts)) / selections.length;
  const selectionMaxConsecutive = run.patternMaxConsecutiveSame;

  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;
  run.runMeters = 2500;
  run.maxRunMeters = 2500;
  run.lastNonZeroRunMeters = 2500;
  run.nextDancerAt = 99;
  run.earlyOncomingSpawned = true;
  spawn.nextHoleAt = 99;
  spawn.nextObstacleAt = 99;
  spawn.nextScoreItemAt = 99;
  spawn.nextItemAt = 99;
  spawn.nextOncomingAt = 99;
  spawn.nextPatternAt = 99;
  const runtimeDef = decisionPatternByName("G_A_H");
  const runtimeStarted = startDecisionPattern(runtimeDef, 2.5);
  const seenSteps = new Set();
  let frames = 0;
  while (mode === MODE.PLAYING && frames < 5000 && run.patternCompletedCount < 1 && run.patternAbortedCount < 1) {
    update(FIXED_STEP);
    for (const entity of [...holes, ...obstacles, ...items]) {
      if (entity.patternName === "G_A_H") seenSteps.add(entity.patternStepIndex);
    }
    frames += 1;
  }
  global.__p3 = {
    version: CLIENT_VERSION,
    definitionErrors,
    learning,
    advanced,
    selectionCounts,
    tripleRepeatCount,
    maxSelectionShare,
    selectionMaxConsecutive,
    runtimeStarted,
    runtimeFrames: frames,
    runtimeCompleted: run.patternCompletedCount,
    runtimeAborted: run.patternAbortedCount,
    runtimeStepResolved: run.patternStepResolvedCount,
    runtimeSeenSteps: [...seenSteps].sort(),
    runtimePatternResolvedCount: run.spawnPatternResolvedCount,
    runtimeQueueOverflow: run.spawnQueueOverflowCount,
    runtimeMandatoryTimeout: run.spawnMandatoryTimeoutCount,
    runtimeConsecutiveHoleViolation: run.consecutiveHoleViolationCount,
  };
})();`;

try {
  Function(script + appended)();
} catch (error) {
  ctx.errors.push(error && error.stack ? error.stack : String(error));
}

const result = global.__p3 || {};
let p1 = null;
let p2 = null;
try { p1 = JSON.parse(fs.readFileSync(path.join(ROOT, "artifacts", "p1-effective-presentation-metrics.json"), "utf8")); } catch {}
try { p2 = JSON.parse(fs.readFileSync(path.join(ROOT, "artifacts", "p2-density-regression.json"), "utf8")); } catch {}

const failures = [];
if (result.version !== "kiriganaito-2026-07-21-v24-ui-finish") failures.push("CLIENT_VERSION is not v24");
if ((result.definitionErrors || []).length) failures.push(`definition safety errors: ${(result.definitionErrors || []).join(" | ")}`);
if ((result.learning || []).length !== 4) failures.push("learning pattern count is not 4");
if (!["G_S_H", "H_S_G", "G_A", "H_A"].every((name) => (result.learning || []).includes(name))) failures.push("learning pool contains wrong patterns");
if (!["O_S_H", "H_S_O", "G_A_H", "P_G_G"].every((name) => (result.advanced || []).includes(name))) failures.push("advanced patterns not unlocked");
if (result.tripleRepeatCount !== 0) failures.push("same pattern repeated three times");
if (!(result.maxSelectionShare <= 0.25)) failures.push(`single pattern share exceeds 25%: ${result.maxSelectionShare}`);
if (!(result.selectionMaxConsecutive <= 2)) failures.push("selection max consecutive exceeds 2");
if (!result.runtimeStarted) failures.push("target runtime pattern did not start");
if (result.runtimeCompleted !== 1) failures.push("target runtime pattern did not complete");
if (result.runtimeAborted !== 0) failures.push("target runtime pattern aborted");
if (result.runtimeStepResolved !== 3) failures.push(`target runtime resolved ${result.runtimeStepResolved} steps`);
if ((result.runtimeSeenSteps || []).length !== 3) failures.push("pattern entity metadata did not cover all steps");
if (result.runtimePatternResolvedCount !== 3) failures.push("spawnPatternResolvedCount mismatch");
if (result.runtimeQueueOverflow !== 0) failures.push("runtime queue overflow");
if (result.runtimeMandatoryTimeout !== 0) failures.push("runtime mandatory timeout");
if (result.runtimeConsecutiveHoleViolation !== 0) failures.push("runtime consecutive hole violation");
if (ctx.errors.length) failures.push(`console errors: ${ctx.errors.join(" | ")}`);
if (ctx.warnings.length) failures.push(`console warnings: ${ctx.warnings.join(" | ")}`);
if (!p1 || !p1.passed) failures.push("P1 measurement artifact missing or failed");
if (!p2 || !p2.passed) failures.push("P2 density artifact missing or failed");
if (p1 && Array.isArray(p1.runs)) {
  if (!p1.runs.every((run) => run.patternStats && run.patternStats.started >= 1)) failures.push("natural P1 runs did not start patterns");
  if (!p1.runs.every((run) => run.patternStats.maxConsecutiveSame <= 2)) failures.push("natural P1 run repeated a pattern three times");
  if (!p1.runs.some((run) => Number(run.sourceCounts && run.sourceCounts.pattern || 0) > 0)) failures.push("no naturally presented pattern entity");
}

const report = {
  generatedAt: new Date().toISOString(),
  purpose: "P3 decision pattern regression",
  result,
  p1PatternRuns: p1 && p1.runs ? p1.runs.map((run) => ({
    seed: run.seed,
    patternPresented: Number(run.sourceCounts && run.sourceCounts.pattern || 0),
    patternStats: run.patternStats,
  })) : [],
  p2Passed: Boolean(p2 && p2.passed),
  failures,
  passed: failures.length === 0,
};

const output = path.join(ROOT, "artifacts", "p3-pattern-regression.json");
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: report.passed, failures, result }, null, 2));
process.exit(report.passed ? 0 : 1);
