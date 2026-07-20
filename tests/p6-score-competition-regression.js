#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const gameScript = html.match(/<script>([\s\S]*)<\/script>/)[1];
const EXPECTED_VERSION = "kiriganaito-2026-07-21-v24-ui-finish";
const REFERENCE_BEFORE_MAX_FULL_COLLECTION_SPREAD_METERS = 620;
const MAX_FULL_COLLECTION_SPREAD_METERS = 310;
const targetCycle = [500, 1000, 1500, 2000, 3000];
const pickupRates = [0, 0.25, 0.5, 0.75, 1];
const samples = 200;

function mulberry32(a) {
  return function () {
    let t = (a += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeEl(id) {
  const el = {
    id,
    textContent: "",
    value: "",
    hidden: false,
    className: "",
    children: [],
    style: {},
    onclick: null,
    get childNodes() {
      return this.children;
    },
    classList: { add() {}, remove() {}, toggle() {} },
    append(...xs) {
      this.children.push(...xs);
    },
    appendChild(x) {
      this.children.push(x);
      return x;
    },
    addEventListener() {},
    setAttribute() {},
    getBoundingClientRect() {
      return { width: 390, height: 430 };
    },
  };
  Object.defineProperty(el, "innerHTML", {
    get() {
      return this.children.map((child) => child.textContent || "").join("");
    },
    set(value) {
      this.children.splice(0);
      this.textContent = String(value);
    },
  });
  return el;
}

function createContext(seed) {
  const ids = [
    "home",
    "rules",
    "name",
    "game",
    "result",
    "error",
    "gameCanvas",
    "startBtn",
    "jumpBtn",
    "retireBtn",
    "homeRanking",
    "resultRanking",
    "homeStats",
    "resultStats",
    "homeToast",
    "playerName",
    "nameError",
    "hudRun",
    "hudScore",
    "hudTime",
    "hudChase",
    "hudDanger",
    "hudChaseBox",
    "hudDangerBox",
    "playStatus",
    "resultReason",
    "resultComment",
    "resultScore",
    "resultBreakdown",
    "rankingStatus",
    "rankingRetryBtn",
    "clientVersionNote",
    "homeVersionNote",
    "resultVersionTop",
    "debug",
    "errorText",
    "homeBtn",
    "errorHomeBtn",
    "nameBtn",
    "rulesBtn",
    "rulesBackBtn",
    "readyBtn",
    "otherGamesResult",
    "changeNameBtn",
    "homeShareBtn",
    "nameStartBtn",
    "nameBackBtn",
    "resultShareBtn",
    "retryBtn",
    "otherGamesHome",
  ];
  const elements = new Map(ids.map((id) => [id, makeEl(id)]));
  elements.get("gameCanvas").getContext = () =>
    new Proxy(
      {
        createLinearGradient() {
          return { addColorStop() {} };
        },
        createRadialGradient() {
          return { addColorStop() {} };
        },
        measureText(text) {
          return { width: String(text).length * 10 };
        },
      },
      {
        get(target, property) {
          return property in target ? target[property] : () => {};
        },
        set() {
          return true;
        },
      },
    );
  const storage = new Map([["kiriganaitoName", "P6"]]);
  const errors = [];
  const warnings = [];
  global.window = global;
  global.addEventListener = () => {};
  global.setTimeout = () => 0;
  global.document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, makeEl(id));
      return elements.get(id);
    },
    createElement: (tag) => makeEl(tag),
    addEventListener() {},
    documentElement: { scrollWidth: 390, clientWidth: 390 },
    body: { scrollWidth: 390, clientWidth: 390 },
  };
  global.localStorage = {
    getItem: (key) => (storage.has(key) ? storage.get(key) : null),
    setItem: (key, value) => storage.set(key, String(value)),
    removeItem: (key) => storage.delete(key),
  };
  global.performance = { now: () => 0 };
  global.requestAnimationFrame = () => 0;
  global.cancelAnimationFrame = () => {};
  global.devicePixelRatio = 1;
  global.fetch = async () => ({ ok: true, json: async () => [] });
  global.console = {
    ...console,
    error: (...args) => errors.push(args.join(" ")),
    warn: (...args) => warnings.push(args.join(" ")),
  };
  Math.random = mulberry32(seed);
  return { errors, warnings };
}

function generateWorld(seed, targetMeters) {
  const context = createContext(seed);
  const appended = `;(() => {
    fetchBestRanking = async () => ({ ok: true, rows: [], error: "" });
    fetchPlayStats = async () => ({ ok: true, stats: { play_count: 0, player_count: 0 }, error: "" });
    sendScoreAfterResult = async () => ({ ok: true });
    el.playerName.value = "P6";
    startGame();
    checkCollisions = () => {};
    checkHoleFall = () => false;
    const generated = [];
    const seen = new Set();
    const target = ${targetMeters};
    for (let step = 0; step < 12000 && mode === MODE.PLAYING && run.runMeters < target; step++) {
      update(FIXED_STEP);
      for (const item of items) {
        if (seen.has(item)) continue;
        seen.add(item);
        if (item.kind === "score") {
          generated.push({
            emoji: item.emoji,
            value: Number(item.value) || 0,
            missPenalty: Number(item.missPenalty) || 0,
          });
        }
      }
    }
    global.__p6World = {
      runMeters: Math.round(run.runMeters),
      generated,
      version: CLIENT_VERSION,
      balanceIndex: run.scoreItemBalanceIndex,
      balanceAvailableMeters: run.scoreItemBalanceAvailableMeters,
      balanceTypeCounts: run.scoreItemBalanceTypeCounts,
      balanceViolationCount: run.scoreItemBalanceViolationCount,
    };
  })();`;
  try {
    Function(gameScript + appended)();
  } catch (error) {
    context.errors.push(error.stack || String(error));
  }
  return { ...global.__p6World, errors: context.errors, warnings: context.warnings };
}

function accidentPenalty(targetMeters, accidentCount) {
  if (accidentCount <= 0) return 0;
  if (targetMeters < 1000) return accidentCount * 100;
  return 100 + Math.max(0, accidentCount - 1) * 200;
}

function scoreCurrent(runMeters, bonusMeters, accidentMeters, missMeters) {
  const gross = runMeters + bonusMeters;
  const rawPenalty = accidentMeters + missMeters;
  return Math.max(0, gross - Math.min(rawPenalty, Math.round(gross * 0.5)));
}

const worlds = [];
for (let index = 0; index < samples; index++) {
  const targetMeters = targetCycle[index % targetCycle.length];
  worlds.push({
    seed: 260000 + index,
    targetMeters,
    ...generateWorld(260000 + index, targetMeters),
  });
}

const records = [];
for (const world of worlds) {
  for (let profile = 0; profile < pickupRates.length; profile++) {
    const pickupRate = pickupRates[profile];
    const decision = mulberry32(world.seed * 37 + profile * 1009);
    const accidentCount = [2, 1, 1, 0, 0][profile];
    let bonusMeters = 0;
    let missMeters = 0;
    let collected = 0;
    for (const item of world.generated) {
      if (decision() < pickupRate) {
        bonusMeters += item.value;
        collected++;
      } else {
        missMeters += item.missPenalty;
      }
    }
    const accidentMeters = accidentPenalty(world.runMeters, accidentCount);
    records.push({
      seed: world.seed,
      targetMeters: world.targetMeters,
      runMeters: world.runMeters,
      profile,
      pickupRate,
      generatedItems: world.generated.length,
      collected,
      bonusMeters,
      accidentCount,
      accidentMeters,
      missMeters,
      currentScore: scoreCurrent(
        world.runMeters,
        bonusMeters,
        accidentMeters,
        missMeters,
      ),
      distanceScore: world.runMeters,
    });
  }
}

const sortDesc = (key) =>
  [...records].sort(
    (left, right) => right[key] - left[key] || right.runMeters - left.runMeters,
  );
const currentRank = sortDesc("currentScore");
const distanceRank = sortDesc("distanceScore");
const distanceTop100 = new Set(
  distanceRank.slice(0, 100).map((row) => `${row.seed}:${row.profile}`),
);
const currentTop100 = currentRank.slice(0, 100);
const top100Overlap = currentTop100.filter((row) =>
  distanceTop100.has(`${row.seed}:${row.profile}`),
).length;

let comparablePairs = 0;
let shorterOutranksLonger = 0;
for (let left = 0; left < records.length; left++) {
  for (let right = left + 1; right < records.length; right++) {
    const a = records[left];
    const b = records[right];
    if (Math.abs(a.runMeters - b.runMeters) < 100) continue;
    comparablePairs++;
    const shorter = a.runMeters < b.runMeters ? a : b;
    const longer = a.runMeters < b.runMeters ? b : a;
    if (shorter.currentScore > longer.currentScore) shorterOutranksLonger++;
  }
}

const sameRuleGroups = new Map();
for (const record of records) {
  const key = `${record.targetMeters}:${record.profile}`;
  if (!sameRuleGroups.has(key)) sameRuleGroups.set(key, []);
  sameRuleGroups.get(key).push(record.currentScore);
}
const sameRuleSpreads = [...sameRuleGroups.entries()].map(([key, values]) => ({
  key,
  min: Math.min(...values),
  max: Math.max(...values),
  spread: Math.max(...values) - Math.min(...values),
}));
const fullCollectionSpreads = sameRuleSpreads.filter((group) =>
  group.key.endsWith(":4"),
);
let largestReversal = null;
for (const shorter of records) {
  for (const longer of records) {
    const distanceGap = longer.runMeters - shorter.runMeters;
    if (distanceGap <= 0 || shorter.currentScore <= longer.currentScore) continue;
    if (!largestReversal || distanceGap > largestReversal.distanceGap) {
      largestReversal = {
        distanceGap,
        shorter,
        longer,
      };
    }
  }
}

function percentile(values, fraction) {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * fraction))];
}

const bonusRatios = records.map((row) =>
  row.runMeters > 0 ? row.bonusMeters / row.runMeters : 0,
);
const completeCycles = worlds
  .filter((world) => world.generated.length >= 20)
  .map((world) => {
    const firstCycle = world.generated.slice(0, 20);
    const counts = { "💰": 0, "🔩": 0, "⚙️": 0 };
    for (const item of firstCycle) counts[item.emoji] = (counts[item.emoji] || 0) + 1;
    return {
      seed: world.seed,
      counts,
      valueMeters: firstCycle.reduce((sum, item) => sum + item.value, 0),
    };
  });
const fullCollectionMaxSpread = Math.max(
  ...fullCollectionSpreads.map((group) => group.spread),
);
const randomnessSpreadReductionRate =
  1 -
  fullCollectionMaxSpread /
    REFERENCE_BEFORE_MAX_FULL_COLLECTION_SPREAD_METERS;
const staticContract = {
  version: html.includes(`CLIENT_VERSION = "${EXPECTED_VERSION}"`),
  hudUsesRecordLabel: />記録<b id="hudScore"/.test(html),
  resultUsesFinalRecordLabel:
    html.includes('class="resultScoreLabel">最終記録</p>') &&
    html.includes('["最終記録", km(snapshot.score)]'),
  rulesExplainFormula: html.includes(
    "最終記録は「実走行距離 + アイテム加算 − 事故・取り逃がしペナルティ」です。",
  ),
  shareSeparatesFinalAndRun:
    html.includes("最終記録：${km(resultSnapshot.score)}") &&
    html.includes("実走行距離：${km(resultSnapshot.runMeters)}"),
  formulaKeepsFiftyPercentPenaltyCap:
    html.includes("const penaltyCapMeters = Math.round(grossMeters * 0.5)") &&
    html.includes("const appliedPenaltyMeters = Math.min(rawPenaltyMeters, penaltyCapMeters)") &&
    html.includes("const scoreMeters = Math.max(0, grossMeters - appliedPenaltyMeters)"),
  rankingPayloadUsesSnapshotScore:
    html.includes("sendScoreAfterResult(resultSnapshot)") &&
    html.includes("result.totalScore ?? result.score") &&
    html.includes("p_score: payload.score"),
  balancedCycleDeclared:
    html.includes("const SCORE_ITEM_BALANCE_SEQUENCE") &&
    html.includes("const SCORE_ITEM_BALANCE_CYCLE_VALUE = 1700"),
};
const failures = [];
if ((worlds[0] && worlds[0].version) !== EXPECTED_VERSION) {
  failures.push(`CLIENT_VERSION mismatch: ${worlds[0] && worlds[0].version}`);
}
if (records.length !== 1000) failures.push(`play equivalents: ${records.length}`);
const worldErrors = worlds.reduce((sum, world) => sum + world.errors.length, 0);
const worldWarnings = worlds.reduce((sum, world) => sum + world.warnings.length, 0);
const balanceViolations = worlds.reduce(
  (sum, world) => sum + world.balanceViolationCount,
  0,
);
const mismatchedGeneratedValueCount = worlds.filter(
  (world) =>
    world.generated.reduce((sum, item) => sum + item.value, 0) !==
    world.balanceAvailableMeters,
).length;
if (worldErrors) failures.push(`world generation errors: ${worldErrors}`);
if (worldWarnings) failures.push(`world generation warnings: ${worldWarnings}`);
if (balanceViolations) failures.push(`balance violations: ${balanceViolations}`);
if (mismatchedGeneratedValueCount) {
  failures.push(`generated value mismatches: ${mismatchedGeneratedValueCount}`);
}
if (!completeCycles.length) failures.push("no complete 20-item cycle observed");
for (const cycle of completeCycles) {
  if (
    cycle.counts["💰"] !== 14 ||
    cycle.counts["🔩"] !== 3 ||
    cycle.counts["⚙️"] !== 3 ||
    cycle.valueMeters !== 1700
  ) {
    failures.push(`unbalanced cycle at seed ${cycle.seed}: ${JSON.stringify(cycle)}`);
    break;
  }
}
if (worlds.some((world) => world.generated.some((item) => item.emoji === "💰" && item.missPenalty !== 0))) {
  failures.push("money item has a miss penalty");
}
if (fullCollectionMaxSpread > MAX_FULL_COLLECTION_SPREAD_METERS) {
  failures.push(
    `full-collection same-distance spread ${fullCollectionMaxSpread}m exceeds ${MAX_FULL_COLLECTION_SPREAD_METERS}m`,
  );
}
if (randomnessSpreadReductionRate < 0.5) {
  failures.push(
    `randomness spread reduction ${(randomnessSpreadReductionRate * 100).toFixed(1)}% is below 50%`,
  );
}
for (const [name, passed] of Object.entries(staticContract)) {
  if (!passed) failures.push(`static contract failed: ${name}`);
}
const report = {
  generatedAt: new Date().toISOString(),
  version: worlds[0] && worlds[0].version,
  method: {
    generatedWorlds: worlds.length,
    playEquivalents: records.length,
    targetMeters: targetCycle,
    pickupRates,
    notes:
      "Actual main game generation was run with hazards disabled. Five deterministic collection profiles were applied to each generated world. This is a scoring stress test, not a prediction of human behavior.",
  },
  worldGeneration: {
    errors: worldErrors,
    warnings: worldWarnings,
    itemCountMin: Math.min(...worlds.map((world) => world.generated.length)),
    itemCountMax: Math.max(...worlds.map((world) => world.generated.length)),
    itemCountAverage:
      worlds.reduce((sum, world) => sum + world.generated.length, 0) /
      worlds.length,
    balanceViolations,
    mismatchedGeneratedValueCount,
    completeCycleCount: completeCycles.length,
    completeCycleContract: {
      itemCount: 20,
      typeCounts: { "💰": 14, "🔩": 3, "⚙️": 3 },
      valueMeters: 1700,
      allObservedCyclesPassed: completeCycles.every(
        (cycle) =>
          cycle.counts["💰"] === 14 &&
          cycle.counts["🔩"] === 3 &&
          cycle.counts["⚙️"] === 3 &&
          cycle.valueMeters === 1700,
      ),
    },
  },
  comparison: {
    top100Overlap,
    top100Changed: 100 - top100Overlap,
    currentTop100AverageRunMeters:
      currentTop100.reduce((sum, row) => sum + row.runMeters, 0) / 100,
    distanceTop100AverageRunMeters:
      distanceRank.slice(0, 100).reduce((sum, row) => sum + row.runMeters, 0) /
      100,
    currentTop100AveragePickupRate:
      currentTop100.reduce((sum, row) => sum + row.pickupRate, 0) / 100,
    comparablePairs,
    shorterOutranksLonger,
    shorterOutranksLongerRate:
      comparablePairs > 0 ? shorterOutranksLonger / comparablePairs : 0,
    bonusToDistanceRatio: {
      median: percentile(bonusRatios, 0.5),
      p90: percentile(bonusRatios, 0.9),
      max: Math.max(...bonusRatios),
    },
    sameDistanceAndProfileScoreSpread: {
      median: percentile(
        sameRuleSpreads.map((group) => group.spread),
        0.5,
      ),
      p90: percentile(
        sameRuleSpreads.map((group) => group.spread),
        0.9,
      ),
      max: Math.max(...sameRuleSpreads.map((group) => group.spread)),
    },
    fullCollectionSameDistanceScoreSpread: {
      median: percentile(
        fullCollectionSpreads.map((group) => group.spread),
        0.5,
      ),
      max: Math.max(...fullCollectionSpreads.map((group) => group.spread)),
      groups: fullCollectionSpreads,
    },
    randomnessSpreadGate: {
      referenceBeforeMaxMeters:
        REFERENCE_BEFORE_MAX_FULL_COLLECTION_SPREAD_METERS,
      currentMaxMeters: fullCollectionMaxSpread,
      maximumAllowedMeters: MAX_FULL_COLLECTION_SPREAD_METERS,
      reductionRate: randomnessSpreadReductionRate,
    },
    largestDistanceReversal: largestReversal,
  },
  staticContract,
  examples: currentRank
    .filter((row) => row.runMeters < 3000)
    .slice(0, 5),
  failures,
  passed: failures.length === 0,
};

fs.mkdirSync(path.join(root, "artifacts"), { recursive: true });
fs.writeFileSync(
  path.join(root, "artifacts", "p6-score-competition-regression.json"),
  JSON.stringify(report, null, 2),
);
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exit(1);
