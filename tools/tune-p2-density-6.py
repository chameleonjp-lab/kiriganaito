from pathlib import Path

index_path = Path("index.html")
index = index_path.read_text()

old_threshold = '        ONCOMING_CRITICAL_OVERDUE_KM: 0.28,'
new_threshold = '        ONCOMING_CRITICAL_OVERDUE_KM: 0.275,'
if old_threshold not in index:
    raise SystemExit("fifth-pass oncoming threshold missing")
index = index.replace(old_threshold, new_threshold, 1)

old_retry = 'req.kind === SPAWN_REQUEST_KIND.HOLE ? 0.001 : SPAWN_DIRECTOR_LIMITS.retryKm'
new_retry = 'req.kind === SPAWN_REQUEST_KIND.HOLE ? 0.0005 : (req.spawnSource === SPAWN_SOURCE.BETWEEN_HOLES ? 0.003 : SPAWN_DIRECTOR_LIMITS.retryKm)'
retry_count = index.count(old_retry)
if retry_count < 2:
    raise SystemExit(f"expected tuned retry assignment in at least two paths, found {retry_count}")
index = index.replace(old_retry, new_retry)

index_path.write_text(index)
