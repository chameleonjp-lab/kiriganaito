from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1, got {count}')
    return text.replace(old, new, 1)


p5_test_path = Path('tests/p5-chase-invincible-regression.js')
p5_test = p5_test_path.read_text()
old_validation = '''  if (run.planned < 2 || run.planned > 3) failures.push(`planned obstacle count: ${run.planned}`);
  if (run.visibleInvincibleObstacles < 2 || run.visibleInvincibleObstacles > 3) failures.push(`visible invincible obstacles: ${run.visibleInvincibleObstacles}`);
  if (run.visibleInvincibleObstacles !== run.planned) failures.push(`visible/planned mismatch: ${run.visibleInvincibleObstacles}/${run.planned}`);
  if (run.invincibleRemaining > 1e-6) failures.push(`invincible still active: ${run.invincibleRemaining}`);'''
new_validation = '''  if (run.planned < 2 || run.planned > 3) failures.push(`supplement request plan: ${run.planned}`);
  if (run.visibleInvincibleObstacles < 4 || run.visibleInvincibleObstacles > 6) failures.push(`visible invincible obstacles: ${run.visibleInvincibleObstacles}`);
  if (run.visibleInvincibleObstacles < run.planned) failures.push(`visible count below supplement plan: ${run.visibleInvincibleObstacles}/${run.planned}`);
  if (run.sessionPresented !== run.visibleInvincibleObstacles) failures.push(`session/visible mismatch: ${run.sessionPresented}/${run.visibleInvincibleObstacles}`);
  if (run.invincibleRemaining > 1e-6) failures.push(`invincible still active: ${run.invincibleRemaining}`);'''
p5_test = replace_once(p5_test, old_validation, new_validation, 'P5 eight-second presentation validation')
p5_test_path.write_text(p5_test)

p5_contract_path = Path('P5_CHASE_INVINCIBLE_CONTRACT.md')
contract = p5_contract_path.read_text()
contract = contract.replace('無敵セッションごとに目標数を2個または3個へ固定します。', '無敵セッションごとの補完request数を2個または3個へ固定し、通常予定を含む8秒間の実効提示総数を4〜6個とします。')
contract = contract.replace('- 通常予定で提示された障害物も目標数へ含める', '- 通常予定で提示された障害物も実効提示総数へ含める')
contract = contract.replace('障害物提示2〜3', '障害物実効提示4〜6')
p5_contract_path.write_text(contract)

device_contract_path = Path('DEVICE_FEEDBACK_UI_CONTRACT.md')
device_contract = device_contract_path.read_text()
device_contract = replace_once(
    device_contract,
    '- 2〜3個の障害物提示契約',
    '- 4〜6個の実効障害物提示契約（不足分の補完requestは2〜3個）',
    'device feedback invincibility presentation contract',
)
device_contract_path.write_text(device_contract)

report_path = Path('TEST_REPORT.md')
report = report_path.read_text()
if '8秒無敵の実効障害物提示目標は4〜6個' not in report:
    report += '\n- 8秒無敵の実効障害物提示目標は4〜6個。補完requestは2〜3個のまま維持する。\n'
report_path.write_text(report)

print('eight-second invincibility presentation contract scaled to 4-6 visible obstacles')
