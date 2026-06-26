# TEST_REPORT

Generated: 2026-06-26T21:02:00Z

## Summary

- `node tests/progressive-autoplay.js`: PASS. Supabase is mocked; console error/warning is 0. Natural autopilot reached 1km, max run 1715m, max corrected score 1315m. 5km+ remains an autopilot limitation after the intentional hole/obstacle density increase and requires real-device tuning.
- `node tests/release-comprehensive.js`: PASS with WARN verdict only because Playwright/mobile screenshots are unavailable in this environment. Supabase production submission is blocked/mocked; console error/warning is 0.
- `node tests/endurance-150km.js`: WARN/FAIL by optional endurance target because the simple autopilot did not reach 150km after the density increase. It ended by falling into a hole at 8710m, but result score was non-zero, result breakdown had non-zero run distance, and `p_score` matched the snapshot score.

## Critical regression checks

| Check | Result | Notes |
| --- | --- | --- |
| Result score is not always 0.00km after 5s retire | PASS | `resultScoreCheck.retire5NonZero=true` |
| Result score is not always 0.00km after 10s retire | PASS | `resultScoreCheck.retireNonZero=true` |
| Result score is not always 0.00km after 5s hole fall | PASS | `resultScoreCheck.hole5NonZero=true` |
| Result score is not always 0.00km after 10s hole fall | PASS | `resultScoreCheck.holeNonZero=true` |
| `run.elapsed > 1` with zero result score is detected | PASS | `resultScoreCheck.elapsedScoreGuard=true` |
| Result score does not reset to 0.00km after result display | PASS | `resultScoreCheck.resultScorePersists=true` |
| Negative corrected score clamps to zero | PASS | `resultScoreCheck.clampOnlyWhenNegative=true` |
| `resultScore` and `p_score` match | PASS | `resultScoreCheck.resultScoreMatchesPScore=true` |
| Result breakdown run distance is non-zero | PASS | `resultScoreCheck.breakdownRunNonZero=true` |
| CLIENT_VERSION updated for cache verification | PASS | `densityTuningCheck.clientVersionUpdated=true` |
| Final run distance guard exists | PASS | `densityTuningCheck.finalRunGuard=true` |
| Hole density increased toward about 2x | PASS | `densityTuningCheck.holeApproxDouble=true` |
| Obstacle density increased toward about 3x | PASS | `densityTuningCheck.obstacleApproxTriple=true` |
| 👯‍♀️ spawn frequency reduced about half | PASS | `densityTuningCheck.dancerHalf=true` |
| Hole contact prevention | PASS | `holeSpacingCheck.noTouch=true` |
| Small-hole landing ground | PASS | `holeSpacingCheck.smallLandingGround=true` |
| Medium/large back-to-back prevention | PASS | `holeSpacingCheck.noMediumLargeBackToBack=true` |
| Large hole followed by oncoming prevention | PASS | `holeSpacingCheck.noLargeThenOncoming=true` |
| 👯‍♀️ 4 second invincibility consistency | PASS | `specConsistencyCheck.dancerEffect=true` |
| Removed walker fixed reward set absence | PASS | `densityTuningCheck.noWalkerCoin=true` |
| Supabase production send | PASS | Mocked only; no real production score submission. |

## Artifacts

- `artifacts/progressive-autoplay-report.json`
- `artifacts/progressive-autoplay-summary.txt`
- `artifacts/release-test-report.json`
- `artifacts/release-test-summary.txt`
- `artifacts/endurance-150km-result.json`
- `artifacts/endurance-150km-screenshot.txt`

## Remaining concerns

- The Node autopilot still over-jumps some holes (`hole_timing_early`) and is not a replacement for real-device play testing.
- Because speed and density were intentionally increased, real-device checks should verify perceived fairness, especially 0.50〜3.00km and chase mode.
- Optional 150km endurance remains beyond the simple autopilot after the density increase; this is recorded as an environment/autopilot limitation rather than a result-score regression.
