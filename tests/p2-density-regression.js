#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const ROOT = path.join(__dirname, "..");
const SOURCE = path.join(__dirname, "effective-presentation-metrics.js");
const TEMP = path.join(__dirname, ".p2-effective-presentation.tmp.js");
const OUTPUT = path.join(ROOT, "artifacts", "p2-density-regression.json");
const GENERATED_REPORT = path.join(ROOT, "artifacts", "p2-effective-presentation-30-seeds.json");
const SEEDS = Array.from({ length: 30 }, (_, index) => 18001 + index);

function fail(message) {
  console.error(message);
  process.exit(1);
}

if (!fs.existsSync(SOURCE)) fail(`missing source harness: ${SOURCE}`);

const original = fs.readFileSync(SOURCE, "utf8");
let expanded = original
  .replace(
    /const OUTPUT_PATH = path\.join\(ROOT, "artifacts", "p1-effective-presentation-metrics\.json"\);/,
    'const OUTPUT_PATH = path.join(ROOT, "artifacts", "p2-effective-presentation-30-seeds.json");',
  )
  .replace(
    /const SEEDS = \[[^\]]+\];/,
    `const SEEDS = ${JSON.stringify(SEEDS)};`,
  );

if (expanded === original) fail("failed to expand effective-presentation harness");
fs.writeFileSync(TEMP, expanded);

let child;
try {
  child = spawnSync(process.execPath, [TEMP], {
    cwd: ROOT,
    encoding: "utf8",
    timeout: 9 * 60 * 1000,
    maxBuffer: 16 * 1024 * 1024,
  });
} finally {
  try { fs.unlinkSync(TEMP); } catch (_) {}
}

if (!child || child.error) fail(`30-seed harness error: ${child && child.error ? child.error.message : "unknown"}`);
if (child.status !== 0) {
  console.error(child.stdout || "");
  console.error(child.stderr || "");
  fail(`30-seed harness exited ${child.status}`);
}
if (!fs.existsSync(GENERATED_REPORT)) fail("30-seed report was not generated");

const sourceReport = JSON.parse(fs.readFileSync(GENERATED_REPORT, "utf8"));
const failures = [];
const seedResults = [];

function gapsAfter(events, thresholdKm) {
  const filtered = (events || []).filter((value) => Number.isFinite(value) && value >= thresholdKm).sort((a, b) => a - b);
  const gaps = [];
  for (let i = 1; i < filtered.length; i += 1) gaps.push(filtered[i] - filtered[i - 1]);
  return {
    count: filtered.length,
    average: gaps.length ? gaps.reduce((sum, value) => sum + value, 0) / gaps.length : 0,
    maximum: gaps.length ? Math.max(...gaps) : 0,
  };
}

for (const run of sourceReport.runs || []) {
  const holeEvents = run.metrics && run.metrics.hole ? run.metrics.hole.presentationKm || [] : [];
  const oncomingEvents = run.metrics && run.metrics.oncoming ? run.metrics.oncoming.presentationKm || [] : [];
  const scoreEvents = run.metrics && run.metrics.scoreItem ? run.metrics.scoreItem.presentationKm || [] : [];
  const hole0to1 = holeEvents.filter((value) => value >= 0 && value < 1).length;
  const hole1to2 = holeEvents.filter((value) => value >= 1 && value < 2).length;
  const holeAfter2 = gapsAfter(holeEvents, 2);
  const earlyOncoming = oncomingEvents.filter((value) => value >= 0.8 && value < 2).length;
  const tooEarlyOncoming = oncomingEvents.filter((value) => value < 0.8).length;
  const scorePerKm = scoreEvents.length / 5;
  const missTargetPerKm = Number(run.presentedMissTargetCount || 0) / 5;

  const checks = {
    hole0to1: hole0to1 >= 4 && hole0to1 <= 6,
    hole1to2: hole1to2 >= 6 && hole1to2 <= 9,
    holeAfter2Average: holeAfter2.count >= 12 && holeAfter2.average >= 0.10 && holeAfter2.average <= 0.18,
    holeAfter2Maximum: holeAfter2.maximum > 0 && holeAfter2.maximum < 0.30,
    earlyOncoming: earlyOncoming >= 1,
    noTooEarlyOncoming: tooEarlyOncoming === 0,
    scoreItemRate: scorePerKm >= 6 && scorePerKm <= 10,
    missTargetRate: missTargetPerKm >= 0 && missTargetPerKm <= 2,
    maxSimultaneousHazards: run.maxSimultaneousStrongHazards <= 2,
    maxDecisionBlank: Number(run.maxDecisionBlankSecAfter500m) < 1.2,
    sourceInvariant: run.sourceInvariantOk === true,
    generatedRelation: run.generatedRelationOk === true,
    noDuplicatePresentation: Number(run.duplicatePresentationCount) === 0,
    noInvalidSource: Number(run.invalidSourceCount) === 0,
    noConsoleErrors: Array.isArray(run.consoleErrors) && run.consoleErrors.length === 0,
    noConsoleWarnings: Array.isArray(run.consoleWarnings) && run.consoleWarnings.length === 0,
  };

  for (const [name, passed] of Object.entries(checks)) {
    if (!passed) failures.push(`seed ${run.seed}: ${name}`);
  }

  seedResults.push({
    seed: run.seed,
    hole0to1,
    hole1to2,
    holeAfter2,
    earlyOncoming,
    tooEarlyOncoming,
    scoreItemCount: scoreEvents.length,
    scorePerKm,
    missTargetCount: Number(run.presentedMissTargetCount || 0),
    missTargetPerKm,
    maxDecisionBlankSecAfter500m: Number(run.maxDecisionBlankSecAfter500m),
    maxSimultaneousStrongHazards: run.maxSimultaneousStrongHazards,
    checks,
  });
}

if (seedResults.length !== 30) failures.push(`expected 30 runs, received ${seedResults.length}`);

const aggregate = {
  seedCount: seedResults.length,
  hole0to1: {
    min: Math.min(...seedResults.map((run) => run.hole0to1)),
    max: Math.max(...seedResults.map((run) => run.hole0to1)),
    average: seedResults.reduce((sum, run) => sum + run.hole0to1, 0) / seedResults.length,
  },
  hole1to2: {
    min: Math.min(...seedResults.map((run) => run.hole1to2)),
    max: Math.max(...seedResults.map((run) => run.hole1to2)),
    average: seedResults.reduce((sum, run) => sum + run.hole1to2, 0) / seedResults.length,
  },
  holeAfter2AverageGapKm: {
    min: Math.min(...seedResults.map((run) => run.holeAfter2.average)),
    max: Math.max(...seedResults.map((run) => run.holeAfter2.average)),
    average: seedResults.reduce((sum, run) => sum + run.holeAfter2.average, 0) / seedResults.length,
  },
  holeAfter2MaxGapKm: Math.max(...seedResults.map((run) => run.holeAfter2.maximum)),
  scoreItemsPerKm: {
    min: Math.min(...seedResults.map((run) => run.scorePerKm)),
    max: Math.max(...seedResults.map((run) => run.scorePerKm)),
    average: seedResults.reduce((sum, run) => sum + run.scorePerKm, 0) / seedResults.length,
  },
  missTargetsPerKm: {
    min: Math.min(...seedResults.map((run) => run.missTargetPerKm)),
    max: Math.max(...seedResults.map((run) => run.missTargetPerKm)),
    average: seedResults.reduce((sum, run) => sum + run.missTargetPerKm, 0) / seedResults.length,
  },
  maxDecisionBlankSecAfter500m: Math.max(...seedResults.map((run) => run.maxDecisionBlankSecAfter500m)),
  maxSimultaneousStrongHazards: Math.max(...seedResults.map((run) => run.maxSimultaneousStrongHazards)),
};

const report = {
  generatedAt: new Date().toISOString(),
  purpose: "P2 effective density regression across 30 fixed seeds",
  sourceHarnessPassed: sourceReport.passed === true,
  targets: {
    hole0to1: "4-6",
    hole1to2: "6-9",
    holeAfter2AverageGapKm: "0.10-0.18",
    holeAfter2MaxGapKm: "<0.30",
    scoreItemsPerKm: "6-10",
    missTargetsPerKm: "0-2",
    oncomingBefore08Km: 0,
    oncomingBy2Km: ">=1",
    maxDecisionBlankSecAfter500m: "<1.2",
    maxSimultaneousStrongHazards: "<=2",
  },
  aggregate,
  seedResults,
  failures,
  passed: sourceReport.passed === true && failures.length === 0,
};

fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
fs.writeFileSync(OUTPUT, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: report.passed, aggregate, failureCount: failures.length, failures: failures.slice(0, 40) }, null, 2));
process.exit(report.passed ? 0 : 1);
