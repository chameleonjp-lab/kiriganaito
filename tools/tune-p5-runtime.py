from pathlib import Path

path = Path('index.html')
text = path.read_text()

old_events = '''        EVENTS: Object.freeze([
          { at: 1.05, type: "score" },
          { at: 1.65, type: "ground" },
          { at: 2.30, type: "score" },
          { at: 2.95, type: "ground" },
          { at: 3.60, type: "score" },
          { at: 4.25, type: "ground" },
          { at: 4.90, type: "score" },
          { at: 5.55, type: "ground" },
          { at: 6.20, type: "hole" },
          { at: 6.85, type: "score" },
          { at: 7.50, type: "oncoming" },
          { at: 8.20, type: "hole" },
          { at: 8.90, type: "score" },
          { at: 9.60, type: "hole" },
          { at: 10.30, type: "oncoming" },
          { at: 12.15, type: "hole" },
          { at: 12.80, type: "score" },
          { at: 13.70, type: "oncoming" },
        ]),'''
new_events = '''        EVENTS: Object.freeze([
          { at: 1.05, type: "score" },
          { at: 1.25, type: "ground" },
          { at: 2.40, type: "score" },
          { at: 3.20, type: "ground" },
          { at: 4.00, type: "score" },
          { at: 5.15, type: "ground" },
          { at: 6.00, type: "score" },
          { at: 6.85, type: "hole" },
          { at: 7.80, type: "score" },
          { at: 9.50, type: "score" },
          { at: 10.15, type: "ground" },
          { at: 10.95, type: "oncoming" },
          { at: 11.80, type: "score" },
          { at: 12.70, type: "hole" },
        ]),'''

old_score_payload = '''          payload = { lane: index % 2 ? "mid" : "low", high: false, type: "💰", x: -36, challenge: false };'''
new_score_payload = '''          payload = { lane: "high", high: true, type: "💰", x: -36, challenge: false, placed: true, speedMult: 0.70 };'''

old_request_tail = '''        req.p5ChaseEventType = event.type;
        req.maxTotalAttempts = 12;
        return req;'''
new_request_tail = '''        req.p5ChaseEventType = event.type;
        req.maxTotalAttempts = 12;
        if (event.type === "score") req.patternAllowsItemPlacement = true;
        return req;'''

old_item_motion = '''          placed: Boolean(t.placed || isDancer),
          speedMult: isDancer ? DANCER_PLACE_SCROLL_MULT : 1,'''
new_item_motion = '''          placed: Boolean(opt.placed || t.placed || isDancer),
          speedMult: Number.isFinite(opt.speedMult) ? opt.speedMult : (isDancer ? DANCER_PLACE_SCROLL_MULT : 1),'''

old_invincible_decay = '''        run.dancerInvincible = Math.max(0, before - dt);
        if (before > 0 && run.dancerInvincible <= 0) {'''
new_invincible_decay = '''        const next = before - dt;
        run.dancerInvincible = next <= 1e-9 ? 0 : next;
        if (before > 0 && run.dancerInvincible <= 0) {'''

old_invincible_payload = '''            () => ({ dir: -1, emoji: run.invincibleRequestIndex % 2 ? "🏃🏻" : "🚶", x: -44 }),'''
new_invincible_payload = '''            () => ({ dir: -1, emoji: run.invincibleRequestIndex % 2 ? "🏃🏻" : "🚶", x: -18 }),'''

for old, new, label in [
    (old_events, new_events, 'P5 event plan'),
    (old_score_payload, new_score_payload, 'P5 score payload'),
    (old_request_tail, new_request_tail, 'P5 score placement permission'),
    (old_item_motion, new_item_motion, 'P5 score movement'),
    (old_invincible_decay, new_invincible_decay, 'invincible epsilon clamp'),
    (old_invincible_payload, new_invincible_payload, 'invincible recognizable spawn X'),
]:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1, got {count}')
    text = text.replace(old, new, 1)

path.write_text(text)
print('P5 runtime event plan and invincibility timing tuned')
