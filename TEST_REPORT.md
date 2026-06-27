# kiriganaito v5 emergency test report

Date: 2026-06-27
Version: `kiriganaito-2026-06-27-v5-result-root-density`

## Summary

- old-version residual strings were searched and removed from implementation, tests, reports, and artifacts.
- `CLIENT_VERSION`, HTML meta, home version display, and result version display are unified to v5.
- Result `0.00km` diagnosis is now visible on the result screen via run/result snapshot diagnostics and `zeroReason`.
- The result score root cause in the local harness was not a ranking payload issue: `resultSnapshot.score`, `el.resultScore.textContent`, and mocked `p_score` matched. The v5 guard keeps the maximum/last non-zero run distance for finish-time rendering so a stale initial `0.00km` can be detected.
- Density was increased by independent hole/obstacle/score-item schedules, a 10x-style score-item cadence, higher object caps, chase grace plus dense chase scheduling, and forced 3km+ oncoming candidates.
- Supabase/RPC payload shape was not changed; tests use mocks and perform no production score submission.

## Commands

- PASS: `node tests/progressive-autoplay.js`
- PASS/WARN: `node tests/release-comprehensive.js` (final verdict WARN only because Playwright is unavailable in this environment; no console errors/warnings; Supabase mocked.)
- FAIL: `node tests/endurance-150km.js` did not reach 150km after the density increase; best run ended at 14.24km with score 21.46km after police capture. Artifact retained for follow-up balancing.
- PASS: repository-wide removed-version string search returned 0 matches.
- PASS: repository-wide forbidden children assignment/search returned 0 matches.

## Key observed values

- 5s retire score: non-zero (`0.20km` in release harness sample).
- 10s retire score: non-zero (`0.39km` in release harness sample).
- 5s hole finish score: non-zero (`0.20km` in release harness sample).
- 10s hole finish score: non-zero (`0.39km` in release harness sample).
- Result score and ranking `p_score` matched in release harness.
- `zeroReason` displayed `normal_non_zero` for non-zero results and remains available for penalty clamp / bug diagnostics.
- Score item spawns are visibly higher in tests (e.g. 10s harness sample showed 14 score items).
- Endurance run confirmed 3km+ oncoming spawns and max speed multiplier `1.350倍`.

## Follow-up requiring real device/public page

- Verify the published page is no longer serving cached old HTML.
- Confirm result screen is updated after long real-device play and does not remain at initial `0.00km`.
- Visually inspect whether increased density remains fair on touch devices.
