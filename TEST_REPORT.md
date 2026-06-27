# kiriganaito v6 emergency test report

Date: 2026-06-27
Version: `kiriganaito-2026-06-28-v6-score-competition`

## Summary
- Updated CLIENT_VERSION, HTML meta, home display, and result display to v6.
- Replaced subtract-to-zero scoring with capped penalty scoring: penalties can reduce only up to 50% of gross distance.
- Result score, `resultSnapshot.score`, and mocked Supabase `p_score` are aligned as integer meters.
- Reduced miss-penalty growth by making 💰 penalty-free and limiting 🔩/⚙️ miss penalties to challenge items.
- Changed 👯‍♀️ invincibility to `performance.now()` real-time 4 seconds and added forced obstacle opportunities during invincibility.
- Added guaranteed 3km+ oncoming candidates with retry intervals and result diagnostics.
- Increased score-item variety, empty-road diagnostics, chase density counters, and 1km speed multiplier reporting.
- Supabase/RPC payload shape was not changed; tests mock fetch and perform no production score submission.

## Test results
- PASS: `node tests/progressive-autoplay.js`
  - 1km reached in natural harness; 5km/10km/30km/150km not reached by the simple autopilot after density increase.
  - console errors: 0, warnings: 0.
- PASS: `node tests/release-comprehensive.js`
  - Final verdict: WARN only because Playwright is unavailable in the environment.
  - Result scores are non-zero after real running, penalty cap prevents zero clamp, and result score matches `p_score`.
  - Supabase production submission: false.
- PASS: `node tests/endurance-150km.js`
  - 150km verification completed with score 436.87km and version `kiriganaito-2026-06-28-v6-score-competition`.
  - 3km+ oncoming spawns recorded; max speed multiplier reached 1.350倍.
- PASS: forbidden old version strings were checked with the required grep commands and returned no matches.

## Manual device checks recommended
- Confirm on a smartphone that 3km+ oncoming obstacles are visually recognizable as moving toward 🚚.
- Confirm 👯‍♀️ shows roughly 4 real seconds and obstacle hits during that window are prevented while holes still end the run.
- Confirm item routes feel varied rather than equal-interval jumps.
