# TEST_REPORT

Generated: 2026-06-26T22:25:26Z

## Summary

- `node tests/progressive-autoplay.js`: PASS. Supabase is mocked; console error/warning is 0. Natural autopilot reached 1km, max run 1563m, max corrected score 1363m. 5km+ remains an autopilot limitation after the intentional density increase and requires real-device tuning.
- `node tests/release-comprehensive.js`: PASS with WARN verdict only because Playwright/mobile screenshots are unavailable in this environment. Supabase production submission is blocked/mocked; console error/warning is 0.
- `node tests/endurance-150km.js`: WARN/FAIL by optional endurance target because the simple autopilot did not reach 150km. It ended at 8794m by 穴に落ちました, but result score was non-zero, result breakdown had non-zero run distance, counters, and `p_score` matched the snapshot score.

## Critical regression checks

| Check | Result | Notes |
| --- | --- | --- |
| Latest CLIENT_VERSION present | PASS | `kiriganaito-2026-06-27-v3-public-fix` found in HTML/meta/result/home strings |
| `index.html` has no `.children = []` assignment | PASS | `staticCheck.noChildrenArrayAssign=true` |
| Result version displayed | PASS | Result breakdown includes version and top/bottom result notes are set |
| Home version displayed | PASS | `homeVersionNote` exists in HTML |
| Result score is not always 0.00km after 5s retire | PASS | `resultScoreCheck.retire5NonZero=true` |
| Result score is not always 0.00km after 10s retire | PASS | `resultScoreCheck.retireNonZero=true` |
| Result score is not always 0.00km after 5s hole fall | PASS | `resultScoreCheck.hole5NonZero=true` |
| Result score is not always 0.00km after 10s hole fall | PASS | `resultScoreCheck.holeNonZero=true` |
| `run.elapsed > 1` with zero result score is detected | PASS | `resultScoreCheck.elapsedScoreGuard=true` |
| Result score does not reset to 0.00km after result display | PASS | `resultScoreCheck.resultScorePersists=true` |
| Negative corrected score clamps to zero | PASS | `resultScoreCheck.clampOnlyWhenNegative=true` |
| `resultScore` and `p_score` match | PASS | `resultScoreCheck.resultScoreMatchesPScore=true` |
| Result breakdown run distance is non-zero | PASS | `resultScoreCheck.breakdownRunNonZero=true` |
| Result breakdown includes counters | PASS | Hole/obstacle/oncoming/dancer/item spawn counters are included |
| Early accident penalty relief | PASS | `specConsistencyCheck.accidentPenalty=true`; 1.00km未満は -0.10km |
| Hole density increased | PASS | `densityTuningCheck.holeApproxDouble=true` |
| Obstacle density increased | PASS | `densityTuningCheck.obstacleApproxTriple=true` |
| Oncoming unlock at 3km | PASS | SPEC and logic gate oncoming with `km >= 3`; endurance observed 2個 actual oncoming spawns |
| 👯‍♀️ spawn frequency reduced further | PASS | `densityTuningCheck.dancerHalf=true`; 1.50km cooldown gate |
| Hole contact prevention | PASS | `holeSpacingCheck.noTouch=true` |
| Supabase production send | PASS | Mocked only; no real production score submission. |

## Artifacts

- `artifacts/progressive-autoplay-report.json`
- `artifacts/progressive-autoplay-summary.txt`
- `artifacts/release-test-report.json`
- `artifacts/release-test-summary.txt`
- `artifacts/endurance-150km-result.json`
- `artifacts/endurance-150km-screenshot.txt`

## Public page check

- The public Codeberg Pages URL was reachable through the browsing fetch and rendered without the new version string, so it appears to still be serving old HTML before this commit. Local `curl`/`urllib` from the container hit a 403 tunnel error, and this checkout has no configured Git remote, so the agent could not push to GitHub/Codeberg from this environment.

## Remaining concerns

- The Node autopilot still over-jumps some holes (`hole_timing_early`) and is not a replacement for real-device play testing.
- Real-device checks should verify perceived fairness, especially 0.50〜3.00km, 3km oncoming visibility, and chase mode.
- Optional 150km endurance remains beyond the simple autopilot after the density increase; this is recorded as an autopilot limitation rather than a result-score regression.
