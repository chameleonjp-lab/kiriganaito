from pathlib import Path

index_path = Path("index.html")
index = index_path.read_text()

old_threshold = '        ONCOMING_CRITICAL_OVERDUE_KM: 0.24,'
new_threshold = '        ONCOMING_CRITICAL_OVERDUE_KM: 0.28,'
if old_threshold not in index:
    raise SystemExit("fourth-pass oncoming threshold missing")
index = index.replace(old_threshold, new_threshold, 1)

old_hole_retry = 'req.kind === SPAWN_REQUEST_KIND.HOLE ? 0.003 : SPAWN_DIRECTOR_LIMITS.retryKm'
new_hole_retry = 'req.kind === SPAWN_REQUEST_KIND.HOLE ? 0.001 : SPAWN_DIRECTOR_LIMITS.retryKm'
retry_count = index.count(old_hole_retry)
if retry_count < 2:
    raise SystemExit(f"expected hole retry tuning in at least two paths, found {retry_count}")
index = index.replace(old_hole_retry, new_hole_retry)

index_path.write_text(index)
