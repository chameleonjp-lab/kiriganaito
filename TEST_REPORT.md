# TEST_REPORT

Generated: 2026-06-26T15:31:18Z

## Summary

- `node tests/progressive-autoplay.js`: PASS. Supabase is mocked; console error/warning is 0. Natural autopilot reached 1km, max run 2057m, max corrected score 1657m. 5km+ remains an autopilot limitation and requires real-device tuning.
- `node tests/release-comprehensive.js`: PASS with WARN verdict only because Playwright/mobile screenshots are unavailable in this environment. Supabase production submission is blocked/mocked; console error/warning is 0.
- `node tests/endurance-150km.js`: WARN/FAIL by design because the simple autopilot did not reach 150km after the density/speed increase. It ended by falling into a hole at 3978m, but result score was non-zero and `p_score` matched the snapshot score.

## Critical regression checks

| Check | Result | Notes |
| --- | --- | --- |
| Result score is not always 0.00km after 10s retire | PASS | `resultScoreCheck.retireNonZero=true` |
| Result score is not always 0.00km after 10s hole fall | PASS | `resultScoreCheck.holeNonZero=true` |
| Negative corrected score clamps to zero | PASS | `resultScoreCheck.clampOnlyWhenNegative=true` |
| `resultScore` and `p_score` match | PASS | `resultScoreCheck.resultScoreMatchesPScore=true` |
| Result breakdown run distance is non-zero | PASS | `resultScoreCheck.breakdownRunNonZero=true` |
| Hole contact prevention | PASS | `holeSpacingCheck.noTouch=true` |
| Small-hole landing ground | PASS | `holeSpacingCheck.smallLandingGround=true` |
| Medium/large back-to-back prevention | PASS | `holeSpacingCheck.noMediumLargeBackToBack=true` |
| Large hole followed by oncoming prevention | PASS | `holeSpacingCheck.noLargeThenOncoming=true` |
| 👯‍♀️ 4 second invincibility consistency | PASS | `specConsistencyCheck.dancerEffect=true` |
| 🚶→💰 fixed set absence | PASS | The removed fixed reward set remains absent from implementation; SPEC only states removal. |
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
