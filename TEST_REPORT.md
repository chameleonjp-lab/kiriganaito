# kiriganaito test report

Generated: 2026-06-27
Version: `kiriganaito-2026-06-27-v4-score-density`

## Public HTML investigation

- Public URL checked with browser fetch: `https://chameleonjp.codeberg.page/kiriganaito/` responded with the game page and the initial result score HTML still contains `0.00km`, which is expected before JS result rendering.
- Local shell `curl`/`urllib` direct fetch was blocked by the environment proxy (`CONNECT tunnel failed, response 403`), so byte-for-byte comparison with the public HTML could not be completed from this container.
- Static local checks confirm the new version string and no `.children = []` assignment in production `index.html`.

## Root cause and fix focus

- Root cause separation: the public symptom can be caused either by a runtime result snapshot race/reset or by legitimate score clamping after penalties. The fix freezes `resultSnapshot` at the start of `finishGame()` and renders/sends only that snapshot.
- Legitimate `0.00km` remains possible when penalties exceed actual distance, but the result breakdown now always shows actual distance and penalties.

## Commands

- ✅ `node tests/progressive-autoplay.js` — pass, console errors/warnings 0. Natural autoplay reached 906m in the densified build; higher targets remain human-play/balance verification items.
- ✅ `node tests/release-comprehensive.js` — pass with WARN verdict only because Playwright/mobile screenshots are unavailable in this environment; Supabase is mocked and no production score is sent.
- ❌ `node tests/endurance-150km.js` — failed to reach 150km naturally after the density increase; it ended at 5.86km by警戒度3. Console errors/warnings 0 and Supabase score submission remained mocked.

## Notable results

- 5s/10s retire and 5s/10s hole-result score checks are non-zero.
- Result score equals mocked `p_score`.
- Result breakdown includes actual run distance, penalties, counters, and version.
- 加点アイテム出現数 increased in short result harnesses (3 items at 5s, 6 items at 10s) while無敵アイテム出現数 stayed 0 in those runs.
- Endurance run showed 90 score-item spawns and 0 invincible-item spawns before ending at 5.86km.
