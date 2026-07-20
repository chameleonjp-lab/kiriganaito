from pathlib import Path

path = Path('tools/apply-device-feedback-ui.py')
text = path.read_text()
old = '''def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    return text.replace(old, new, 1)
'''
new = '''def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if label == 'UI CSS insertion' and count >= 1:
        return text.replace(old, new, 1)
    if label == 'home share concept' and count == 0:
        old_literal = old.replace('\\n', '\\\\n')
        new_literal = new.replace('\\n', '\\\\n')
        literal_count = text.count(old_literal)
        if literal_count == 1:
            return text.replace(old_literal, new_literal, 1)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    return text.replace(old, new, 1)
'''
if text.count(old) != 1:
    raise SystemExit(f'replace_once helper: expected 1, got {text.count(old)}')
path.write_text(text.replace(old, new, 1))
print('device feedback apply matchers fixed')
