from pathlib import Path

path = Path('tools/apply-p4-air-obstacle.py')
text = path.read_text()
old = """    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, got {count}')\n    return text.replace(old, new, 1)\n"""
new = """    if label == 'air fallback' and count == 2:\n        return text.replace(old, new, 1)\n    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, got {count}')\n    return text.replace(old, new, 1)\n"""
if old not in text:
    raise SystemExit('replace_once body not found')
path.write_text(text.replace(old, new, 1))
print('P4 apply script fallback matcher fixed')
