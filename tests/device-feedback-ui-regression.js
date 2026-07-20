#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.join(__dirname, "..");
const INDEX_PATH = path.join(ROOT, "index.html");
const OUTPUT_PATH = path.join(ROOT, "artifacts", "device-feedback-ui-regression.json");
const EXPECTED_VERSION = "kiriganaito-2026-07-21-v24-ui-finish";
const CONCEPT = "落とした積荷と落ちてるお金を拾い集めよう";

function makeElement(id) {
  const classes = new Set();
  const element = {
    id,
    textContent: "",
    value: "",
    hidden: false,
    disabled: false,
    open: false,
    className: "",
    children: [],
    style: {},
    dataset: {},
    onclick: null,
    get childNodes() { return this.children; },
    classList: {
      add(name) { classes.add(name); element.className = [...classes].join(" "); },
      remove(name) { classes.delete(name); element.className = [...classes].join(" "); },
      toggle(name, force) {
        if (force === true) classes.add(name);
        else if (force === false) classes.delete(name);
        else if (classes.has(name)) classes.delete(name);
        else classes.add(name);
        element.className = [...classes].join(" ");
      },
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

function createSandbox() {
  const ids = [
    "home", "rules", "name", "game", "result", "error", "gameCanvas", "startBtn", "jumpBtn", "retireBtn",
    "homeRanking", "resultRanking", "homeStats", "resultStats", "homeToast", "playerName", "nameError",
    "hudRun", "hudScore", "hudTime", "hudChase", "hudDanger", "hudChaseBox", "hudDangerBox", "playStatus",
    "resultReason", "resultComment", "resultScore", "resultBreakdown", "rankingStatus", "rankingRetryBtn",
    "clientVersionNote", "homeVersionNote", "resultVersionTop", "debug", "errorText", "homeBtn", "errorHomeBtn",
    "rulesBtn", "rulesBackBtn", "changeNameBtn", "homeShareBtn", "nameStartBtn", "nameBackBtn", "resultShareBtn",
    "retryBtn", "otherGamesHome", "otherGamesResult", "homeRankingDetails", "resultRankingDetails",
  ];
  const elements = new Map(ids.map((id) => [id, makeElement(id)]));
  const drawCalls = [];
  const contextTarget = {
    font: "",
    createLinearGradient() { return { addColorStop() {} }; },
    createRadialGradient() { return { addColorStop() {} }; },
    measureText(text) { return { width: String(text).length * 10 }; },
    fillText(text, x, y) { drawCalls.push({ text: String(text), x, y, font: this.font }); },
  };
  elements.get("gameCanvas").getContext = () => new Proxy(contextTarget, {
    get(target, property) { if (property in target) return target[property]; return () => {}; },
    set(target, property, value) { target[property] = value; return true; },
  });

  const storage = new Map();
  const consoleErrors = [];
  const consoleWarnings = [];
  let nowMs = 0;
  const sandbox = {
    Math, Date, JSON, Object, Array, Number, String, Boolean, Set, Map, WeakSet, WeakMap, Promise,
    parseInt, parseFloat, isFinite, TextEncoder, TextDecoder, URL, URLSearchParams, Blob: global.Blob,
    navigator: {}, location: { href: "https://example.invalid/kiriganaito/", search: "" },
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
    fetch: async () => ({ ok: false, status: 599, json: async () => ({ mocked: true }) }),
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
    addEventListener() {},
    documentElement: { scrollWidth: 320, clientWidth: 320 },
    body: { scrollWidth: 320, clientWidth: 320 },
  };
  sandbox.__state = { elements, drawCalls, consoleErrors, consoleWarnings };
  return sandbox;
}

function staticChecks(html) {
  const homeDetails = html.match(/<details\s+id="homeRankingDetails"([^>]*)>/);
  const resultDetails = html.match(/<details\s+id="resultRankingDetails"([^>]*)>/);
  const truckBlock = html.match(/ctx\.font\s*=\s*"(\d+)px serif";[\s\S]{0,260}?ctx\.fillText\("🚚"/);
  return {
    conceptCount: html.split(CONCEPT).length - 1,
    homeDetailsFound: Boolean(homeDetails),
    homeDetailsOpen: Boolean(homeDetails && /\bopen\b/.test(homeDetails[1])),
    resultDetailsFound: Boolean(resultDetails),
    resultDetailsOpen: Boolean(resultDetails && /\bopen\b/.test(resultDetails[1])),
    startLabel: /id="startBtn"[^>]*>ゲーム開始</.test(html),
    rulesLabel: /id="rulesBtn"[^>]*>ルール説明</.test(html),
    shareLabel: /id="homeShareBtn"[^>]*>ゲームをシェア</.test(html),
    ruleFacts: {
      money: html.includes("💰 お金：+0.10km"),
      bolt: html.includes("🔩 落とした積荷：+0.03km。取り逃がすと-0.05km"),
      gear: html.includes("⚙️ 落とした積荷：+0.07km。取り逃がすと-0.05km"),
      earlyPenalty: html.includes("1km未満で-0.10km"),
      laterPenalty: html.includes("1km以降で-0.20km"),
      airNoJump: html.includes("吊り下げバー：ジャンプせず、地上にいれば安全"),
      chase: html.includes("事故後15秒は逃走モード"),
      invincibleEight: html.includes("実際にプレイしている時間で8秒間"),
      holeStillFatal: html.includes("穴：落ちると即終了。👯‍♀️無敵中でも防げません"),
    },
    truckFontPx: truckBlock ? Number(truckBlock[1]) : null,
    versionInMeta: html.includes(`name="x-client-version" content="${EXPECTED_VERSION}"`),
  };
}

function runtimeChecks(script) {
  const sandbox = createSandbox();
  vm.createContext(sandbox);
  const appended = `
;(() => {
  fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
  fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
  sendScoreAfterResult = async () => ({ ok: true });
  el.playerName.value = "DEVICE";
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;

  const groundBefore = [getGroundY(-200), getGroundY(0), getGroundY(200)];
  run.visualScroll = 123456;
  const groundAfter = [getGroundY(-200), getGroundY(0), getGroundY(200)];

  const playerPhysics = { w: player.w, h: player.h };
  activateDancerInvincible();
  const invincibleInitial = getDancerInvincibleRemainingSec();
  __advanceNow(30000);
  const afterWallClockOnly = getDancerInvincibleRemainingSec();
  for (let i = 0; i < 240; i++) updateDancerInvincible(FIXED_STEP);
  const afterFourPlayedSeconds = getDancerInvincibleRemainingSec();
  for (let i = 0; i < 240; i++) updateDancerInvincible(FIXED_STEP);
  const afterEightPlayedSeconds = getDancerInvincibleRemainingSec();

  globalThis.__deviceChecks = {
    clientVersion: CLIENT_VERSION,
    groundY,
    groundBefore,
    groundAfter,
    playerPhysics,
    invincibleInitial,
    afterWallClockOnly,
    afterFourPlayedSeconds,
    afterEightPlayedSeconds,
    homeRankingOpenDefault: $("homeRankingDetails").open,
    resultRankingOpenDefault: $("resultRankingDetails").open,
  };
})();`;
  try {
    vm.runInContext(`${script}\n${appended}`, sandbox, { timeout: 60000 });
  } catch (error) {
    sandbox.__state.consoleErrors.push(error && error.stack ? error.stack : String(error));
  }
  return {
    ...sandbox.__deviceChecks,
    consoleErrors: sandbox.__state.consoleErrors,
    consoleWarnings: sandbox.__state.consoleWarnings,
  };
}

function validate(staticResult, runtimeResult) {
  const failures = [];
  if (staticResult.conceptCount < 3) failures.push(`concept count: ${staticResult.conceptCount}`);
  if (!staticResult.homeDetailsFound || staticResult.homeDetailsOpen) failures.push("home ranking is not closed details");
  if (!staticResult.resultDetailsFound || staticResult.resultDetailsOpen) failures.push("result ranking is not closed details");
  if (!staticResult.startLabel || !staticResult.rulesLabel || !staticResult.shareLabel) failures.push("home action labels mismatch");
  for (const [name, passed] of Object.entries(staticResult.ruleFacts)) if (!passed) failures.push(`missing rule fact: ${name}`);
  if (staticResult.truckFontPx !== 36) failures.push(`truck font size: ${staticResult.truckFontPx}`);
  if (!staticResult.versionInMeta) failures.push("version meta mismatch");
  if (!runtimeResult || runtimeResult.clientVersion !== EXPECTED_VERSION) failures.push("runtime version mismatch");
  if (!runtimeResult || runtimeResult.playerPhysics.w !== 42 || runtimeResult.playerPhysics.h !== 34) failures.push(`player physics changed: ${JSON.stringify(runtimeResult && runtimeResult.playerPhysics)}`);
  if (!runtimeResult || runtimeResult.groundBefore.some((value) => Math.abs(value - runtimeResult.groundY) > 1e-9)) failures.push(`ground is not flat before scroll: ${JSON.stringify(runtimeResult && runtimeResult.groundBefore)}`);
  if (!runtimeResult || runtimeResult.groundAfter.some((value) => Math.abs(value - runtimeResult.groundY) > 1e-9)) failures.push(`ground changes with scroll: ${JSON.stringify(runtimeResult && runtimeResult.groundAfter)}`);
  if (!runtimeResult || Math.abs(runtimeResult.invincibleInitial - 8) > 1e-9) failures.push(`invincible initial: ${runtimeResult && runtimeResult.invincibleInitial}`);
  if (!runtimeResult || Math.abs(runtimeResult.afterWallClockOnly - 8) > 1e-9) failures.push(`wall-clock decay: ${runtimeResult && runtimeResult.afterWallClockOnly}`);
  if (!runtimeResult || Math.abs(runtimeResult.afterFourPlayedSeconds - 4) > 1e-6) failures.push(`four played seconds: ${runtimeResult && runtimeResult.afterFourPlayedSeconds}`);
  if (!runtimeResult || runtimeResult.afterEightPlayedSeconds > 1e-6) failures.push(`eight played seconds: ${runtimeResult && runtimeResult.afterEightPlayedSeconds}`);
  if (runtimeResult && (runtimeResult.homeRankingOpenDefault || runtimeResult.resultRankingOpenDefault)) failures.push("ranking details opened at runtime startup");
  if (runtimeResult && runtimeResult.consoleErrors.length) failures.push(`console errors: ${runtimeResult.consoleErrors.join(" | ")}`);
  if (runtimeResult && runtimeResult.consoleWarnings.length) failures.push(`console warnings: ${runtimeResult.consoleWarnings.join(" | ")}`);
  return failures;
}

if (!fs.existsSync(INDEX_PATH)) {
  console.error(`index.html not found: ${INDEX_PATH}`);
  process.exit(1);
}
const html = fs.readFileSync(INDEX_PATH, "utf8");
const scriptMatch = html.match(/<script>([\s\S]*)<\/script>/);
if (!scriptMatch) {
  console.error("inline script not found");
  process.exit(1);
}
const staticResult = staticChecks(html);
const runtimeResult = runtimeChecks(scriptMatch[1]);
const failures = validate(staticResult, runtimeResult);
const report = {
  generatedAt: new Date().toISOString(),
  clientVersion: EXPECTED_VERSION,
  purpose: "Device feedback UI, flat ground, closed ranking, 8-second invincibility and truck render regression",
  static: staticResult,
  runtime: runtimeResult,
  failures,
  passed: failures.length === 0,
};
fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
fs.writeFileSync(OUTPUT_PATH, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: report.passed, static: staticResult, runtime: runtimeResult, failures }, null, 2));
process.exit(report.passed ? 0 : 1);
