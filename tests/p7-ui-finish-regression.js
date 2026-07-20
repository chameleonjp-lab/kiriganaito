#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.join(__dirname, "..");
const INDEX_PATH = path.join(ROOT, "index.html");
const OUTPUT_PATH = path.join(ROOT, "artifacts", "p7-ui-finish-regression.json");
const EXPECTED_VERSION = "kiriganaito-2026-07-21-v24-ui-finish";

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
    "resultReason", "resultComment", "resultScore", "resultRun", "resultItems", "resultPickupRate", "resultAccidents",
    "resultDetails", "resultBreakdown", "rankingStatus", "rankingRetryBtn", "clientVersionNote", "homeVersionNote",
    "resultVersionTop", "debug", "errorText", "homeBtn", "errorHomeBtn", "rulesBtn", "rulesBackBtn",
    "changeNameBtn", "homeShareBtn", "nameStartBtn", "nameBackBtn", "resultShareBtn", "retryBtn",
    "otherGamesHome", "otherGamesResult", "homeRankingDetails", "resultRankingDetails",
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
    get(target, property) { return property in target ? target[property] : () => {}; },
    set(target, property, value) { target[property] = value; return true; },
  });

  const storage = new Map([["kiriganaitoName", "P7"]]);
  const consoleErrors = [];
  const consoleWarnings = [];
  const scrollCalls = [];
  const sandbox = {
    Math, Date, JSON, Object, Array, Number, String, Boolean, Set, Map, WeakSet, WeakMap, Promise,
    parseInt, parseFloat, isFinite, TextEncoder, TextDecoder, URL, URLSearchParams, Blob: global.Blob,
    navigator: {}, location: { href: "https://example.invalid/kiriganaito/", search: "" },
    performance: { now: () => 0 },
    requestAnimationFrame: () => 0,
    cancelAnimationFrame: () => {},
    setTimeout: () => 0,
    clearTimeout: () => {},
    devicePixelRatio: 1,
    addEventListener: () => {},
    scrollTo: (...args) => scrollCalls.push(args),
    localStorage: {
      getItem(key) { return storage.has(key) ? storage.get(key) : null; },
      setItem(key, value) { storage.set(key, String(value)); },
      removeItem(key) { storage.delete(key); },
    },
    fetch: async () => ({ ok: true, status: 200, json: async () => [] }),
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
  sandbox.__state = { elements, drawCalls, consoleErrors, consoleWarnings, scrollCalls };
  return sandbox;
}

function staticChecks(html) {
  const resultDetailsTag = html.match(/<details\s+id="resultDetails"([^>]*)>/);
  const shareIndex = html.indexOf('id="resultShareBtn"');
  const retryIndex = html.indexOf('id="retryBtn"');
  const detailsIndex = html.indexOf('id="resultDetails"');
  return {
    versionInMeta: html.includes(`name="x-client-version" content="${EXPECTED_VERSION}"`),
    quickGuide: ["タップ</b>1段ジャンプ", "穴</b>落ちると終了", "吊りバー</b>跳ばずに通過"].every((text) => html.includes(text)),
    summaryIds: ["resultRun", "resultItems", "resultPickupRate", "resultAccidents"].every((id) => html.includes(`id="${id}"`)),
    resultDetailsClosed: Boolean(resultDetailsTag && !/\bopen\b/.test(resultDetailsTag[1])),
    primaryActionsBeforeDetails: shareIndex > 0 && retryIndex > shareIndex && detailsIndex > retryIndex,
    horizontalOverflowGuard: /html,\s*\n\s*body[\s\S]{0,180}?overflow-x:\s*hidden/.test(html),
    shortViewportRule: /@media\s*\(max-height:\s*640px\)/.test(html) && /height:\s*min\(48dvh,\s*290px\)/.test(html),
    gameFlexShrinkGuard: /\.gameWrap\s*\{[\s\S]{0,180}?min-height:\s*0/.test(html),
    dangerLabels: {
      hole: html.includes('drawCanvasLabel("穴"'),
      air: html.includes('drawCanvasLabel("跳ばない"'),
      oncoming: html.includes('drawCanvasLabel("→ 対向"'),
      chase: html.includes('drawCanvasLabel("🚨 逃走中"'),
    },
    chaseUsesEdgeStrips: html.includes("ctx.fillRect(0, 0, 6, groundY)") && html.includes("ctx.fillRect(W - 6, 0, 6, groundY)"),
    noDatasetAssignment: !html.includes("d.dataset ="),
    resetDetailsOnFinish: html.includes("el.resultDetails.open = false"),
    scrollReset: html.includes("window.scrollTo(0, 0)"),
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
  flushPendingScores = async () => ({ ok: true });
  el.playerName.value = "P7";
  startGame();
  checkCollisions = () => {};
  checkHoleFall = () => false;

  holes = [{ x: 34, prevX: 34, y: groundY, w: 58, h: 80, active: true }];
  obstacles = [
    { x: 112, y: groundY - 78, w: 72, h: 22, zone: WORLD_ZONE.AIR, direction: -1, emoji: "", active: true },
    { x: 206, y: groundY - 32, w: 32, h: 32, zone: WORLD_ZONE.GROUND, direction: 1, emoji: "🚶", active: true },
  ];
  draw();
  const dangerTexts = [...new Set(globalThis.__state.drawCalls.map((call) => call.text))];

  run.runMeters = 1234;
  run.maxRunMeters = 1234;
  run.lastNonZeroRunMeters = 1234;
  run.bonusMeters = 200;
  run.penaltyMeters = 100;
  run.missPenaltyMeters = 50;
  run.items = 2;
  run.scoreItemSpawnCount = 4;
  run.accidents = 1;
  run.elapsed = 12;
  el.resultDetails.open = true;
  $("resultRankingDetails").open = true;
  finishGame("リタイア");

  const diagnosticRows = el.resultBreakdown.childNodes.filter((node) => node.dataset && node.dataset.diagnostic === "1");
  const diagnosticsInitiallyHidden = diagnosticRows.length > 0 && diagnosticRows.every((node) => node.hidden);
  const toggle = el.resultBreakdown.childNodes.find((node) => node.className === "secondary diagnosticsToggle");
  if (toggle && toggle.onclick) toggle.onclick();

  globalThis.__p7Checks = {
    clientVersion: CLIENT_VERSION,
    dangerTexts,
    score: resultSnapshot.score,
    resultScore: el.resultScore.textContent,
    resultRun: el.resultRun.textContent,
    resultItems: el.resultItems.textContent,
    resultPickupRate: el.resultPickupRate.textContent,
    resultAccidents: el.resultAccidents.textContent,
    resultReason: el.resultReason.textContent,
    resultDetailsClosed: !el.resultDetails.open,
    rankingDetailsClosed: !$("resultRankingDetails").open,
    diagnosticsCount: diagnosticRows.length,
    diagnosticsInitiallyHidden,
    diagnosticsVisibleAfterToggle: diagnosticRows.length > 0 && diagnosticRows.every((node) => !node.hidden),
    toggleLabelAfterOpen: toggle ? toggle.textContent : "",
    resultScrollReset: globalThis.__state.scrollCalls.some((args) => args[0] === 0 && args[1] === 0),
  };
})();`;
  try {
    vm.runInContext(`${script}\n${appended}`, sandbox, { timeout: 60000 });
  } catch (error) {
    sandbox.__state.consoleErrors.push(error && error.stack ? error.stack : String(error));
  }
  return {
    ...sandbox.__p7Checks,
    consoleErrors: sandbox.__state.consoleErrors,
    consoleWarnings: sandbox.__state.consoleWarnings,
  };
}

function validate(staticResult, runtimeResult) {
  const failures = [];
  for (const [name, passed] of Object.entries(staticResult)) {
    if (name === "dangerLabels") continue;
    if (!passed) failures.push(`static check failed: ${name}`);
  }
  for (const [name, passed] of Object.entries(staticResult.dangerLabels)) if (!passed) failures.push(`missing danger label: ${name}`);
  if (!runtimeResult || runtimeResult.clientVersion !== EXPECTED_VERSION) failures.push("runtime version mismatch");
  for (const text of ["穴", "跳ばない", "→ 対向"]) if (!runtimeResult || !runtimeResult.dangerTexts.includes(text)) failures.push(`danger text not drawn: ${text}`);
  if (!runtimeResult || runtimeResult.score !== 1284 || runtimeResult.resultScore !== "1.28km") failures.push(`result score mismatch: ${JSON.stringify(runtimeResult && { score: runtimeResult.score, text: runtimeResult.resultScore })}`);
  if (!runtimeResult || runtimeResult.resultRun !== "1.23km") failures.push(`result run mismatch: ${runtimeResult && runtimeResult.resultRun}`);
  if (!runtimeResult || runtimeResult.resultItems !== "2 / 4個") failures.push(`result items mismatch: ${runtimeResult && runtimeResult.resultItems}`);
  if (!runtimeResult || runtimeResult.resultPickupRate !== "50.0%") failures.push(`pickup rate mismatch: ${runtimeResult && runtimeResult.resultPickupRate}`);
  if (!runtimeResult || runtimeResult.resultAccidents !== "1回") failures.push(`accident result mismatch: ${runtimeResult && runtimeResult.resultAccidents}`);
  if (!runtimeResult || !runtimeResult.resultReason.includes("リタイア")) failures.push("finish reason missing");
  if (!runtimeResult || !runtimeResult.resultDetailsClosed || !runtimeResult.rankingDetailsClosed) failures.push("result details did not reset closed");
  if (!runtimeResult || runtimeResult.diagnosticsCount < 10 || !runtimeResult.diagnosticsInitiallyHidden) failures.push("diagnostics are not hidden by default");
  if (!runtimeResult || !runtimeResult.diagnosticsVisibleAfterToggle || runtimeResult.toggleLabelAfterOpen !== "詳細診断を隠す") failures.push("diagnostics toggle failed");
  if (!runtimeResult || !runtimeResult.resultScrollReset) failures.push("result scroll was not reset");
  if (runtimeResult && runtimeResult.consoleErrors.length) failures.push(`console errors: ${runtimeResult.consoleErrors.join(" | ")}`);
  if (runtimeResult && runtimeResult.consoleWarnings.length) failures.push(`console warnings: ${runtimeResult.consoleWarnings.join(" | ")}`);
  return failures;
}

const html = fs.readFileSync(INDEX_PATH, "utf8");
const scriptMatch = html.match(/<script>([\s\S]*)<\/script>/);
if (!scriptMatch) throw new Error("inline script not found");
const staticResult = staticChecks(html);
const runtimeResult = runtimeChecks(scriptMatch[1]);
const failures = validate(staticResult, runtimeResult);
const report = {
  generatedAt: new Date().toISOString(),
  clientVersion: EXPECTED_VERSION,
  purpose: "P7 result hierarchy, compact phone layout and color-independent danger cues",
  static: staticResult,
  runtime: runtimeResult,
  failures,
  passed: failures.length === 0,
};
fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
fs.writeFileSync(OUTPUT_PATH, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
process.exit(report.passed ? 0 : 1);
