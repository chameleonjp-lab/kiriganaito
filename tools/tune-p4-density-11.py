from pathlib import Path

path = Path('index.html')
text = path.read_text()
old = '        SCROLL_PX: 360,'
new = '        SCROLL_PX: STATIC_OBSTACLE_SCROLL_PX,'
if text.count(old) != 1:
    raise SystemExit(f'P4 equal scroll speed: expected 1, got {text.count(old)}')
path.write_text(text.replace(old, new, 1))
print('P4 AIR uses the exact world-scroll speed to preserve horizontal separation')
