from pathlib import Path
import re

ROOT = Path('.')
INDEX = ROOT / 'index.html'
OLD_VERSION = 'kiriganaito-2026-07-20-v21-chase-invincible'
NEW_VERSION = 'kiriganaito-2026-07-20-v22-device-feedback-ui'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    return text.replace(old, new, 1)


def sub_once(text: str, pattern: str, replacement: str, label: str, flags: int = 0) -> str:
    result, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    return result


index = INDEX.read_text()
if OLD_VERSION not in index:
    raise SystemExit('old CLIENT_VERSION not found in index.html')
index = index.replace(OLD_VERSION, NEW_VERSION)

css = r'''      #home.screen.active {
        justify-content: flex-start;
        gap: 8px;
      }
      .homeHero {
        padding: 16px;
      }
      .homeKicker {
        margin: 0 0 4px;
        color: #9fc6ff;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.12em;
      }
      .homeHero .title {
        margin-bottom: 8px;
        font-size: clamp(34px, 10vw, 46px);
      }
      .homeConcept {
        margin: 0 0 8px;
        color: #ffe879;
        font-size: clamp(20px, 6vw, 27px);
        font-weight: 900;
        line-height: 1.32;
      }
      .homeSupport {
        margin: 0 0 14px;
        color: #d9e2ff;
        font-size: 14px;
        line-height: 1.55;
      }
      .homePrimary {
        width: 100%;
        min-height: 60px;
        margin-bottom: 10px;
        font-size: 20px;
      }
      .homeActions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
      }
      .homeNameButton {
        width: 100%;
        margin-top: 10px;
      }
      .homeHero .toast {
        margin: 8px 0 0;
      }
      .homeHero .versionNote {
        margin: 2px 0 0;
      }
      .otherGamesLink {
        display: block;
        padding: 7px 4px 2px;
        text-align: center;
        font-weight: 700;
      }
      details.rankingDetails {
        padding: 0;
        overflow: hidden;
      }
      .rankingDetails > summary {
        min-height: 52px;
        padding: 15px 16px;
        cursor: pointer;
        color: #dce7ff;
        font-weight: 850;
        list-style: none;
      }
      .rankingDetails > summary::-webkit-details-marker {
        display: none;
      }
      .rankingDetails > summary::after {
        content: "＋";
        float: right;
        color: #ffe879;
      }
      .rankingDetails[open] > summary::after {
        content: "−";
      }
      .rankingDetails[open] > summary {
        border-bottom: 1px solid #3a4161;
      }
      .rankingBody {
        padding: 10px 16px 14px;
      }
      .rulesCard {
        padding: 16px;
      }
      .ruleConcept {
        margin: 0 0 12px;
        color: #ffe879;
        font-size: 20px;
        font-weight: 900;
        line-height: 1.4;
      }
      .rulesGrid {
        display: grid;
        gap: 10px;
        margin-bottom: 14px;
      }
      .ruleBlock {
        padding: 12px;
        border: 1px solid #465071;
        border-radius: 14px;
        background: rgba(12, 15, 28, 0.38);
      }
      .ruleBlock h3 {
        margin: 0 0 6px;
        color: #fff1a6;
        font-size: 16px;
      }
      .ruleBlock p,
      .ruleBlock ul {
        margin: 0;
        color: #d9e2ff;
        font-size: 14px;
        line-height: 1.58;
      }
      .ruleBlock ul {
        padding-left: 1.3em;
      }
      .ruleBlock li + li {
        margin-top: 4px;
      }
'''
index = replace_once(index, '      .hud {\n', css + '      .hud {\n', 'UI CSS insertion')

home_html = '''      <section id="home" class="screen active">
        <div class="card homeHero">
          <p class="homeKicker">ワンタップ回収ラン</p>
          <h1 class="title">kiriganaito</h1>
          <p class="homeConcept">落とした積荷と落ちてるお金を拾い集めよう</p>
          <p class="homeSupport">穴や障害物を見分けてジャンプ。拾った分を記録へ加えながら、できるだけ遠くまで走ろう。</p>
          <button id="startBtn" class="homePrimary">ゲーム開始</button>
          <div class="homeActions">
            <button id="rulesBtn" class="secondary">ルール説明</button>
            <button id="homeShareBtn" class="secondary">ゲームをシェア</button>
          </div>
          <button id="changeNameBtn" class="secondary homeNameButton">名前を変更</button>
          <p id="homeToast" class="toast"></p>
          <p id="homeVersionNote" class="small versionNote">version: kiriganaito-2026-07-20-v22-device-feedback-ui</p>
        </div>
        <details id="homeRankingDetails" class="card rankingDetails">
          <summary>詳細ランキングを見る</summary>
          <div class="rankingBody">
            <div id="homeRanking" class="rank">ランキング未設定</div>
            <p id="homeStats" class="small"></p>
          </div>
        </details>
        <a id="otherGamesHome" class="otherGamesLink" href="https://chameleonjp.codeberg.page/">その他のゲームで遊ぶ</a>
      </section>
'''
index = sub_once(
    index,
    r'      <section id="home" class="screen active">.*?      </section>\n(?=      <section id="rules")',
    home_html,
    'home screen replacement',
    re.S,
)

rules_html = '''      <section id="rules" class="screen">
        <div class="card rulesCard">
          <h2>ルール</h2>
          <p class="ruleConcept">落とした積荷と落ちてるお金を拾い集めよう</p>
          <div class="rulesGrid">
            <section class="ruleBlock">
              <h3>目的</h3>
              <p>🚚は自動で走ります。道に落ちたお金と、荷台から落とした積荷を回収しながら、できるだけ遠くまで進みます。</p>
            </section>
            <section class="ruleBlock">
              <h3>操作</h3>
              <ul>
                <li>ゲーム画面か「ジャンプ」ボタンをタップすると1段ジャンプします。</li>
                <li>2段ジャンプはできません。着地してから次のジャンプができます。</li>
              </ul>
            </section>
            <section class="ruleBlock">
              <h3>拾うもの</h3>
              <ul>
                <li>💰 お金：+0.10km</li>
                <li>🔩 落とした積荷：+0.03km。取り逃がすと-0.05km</li>
                <li>⚙️ 落とした積荷：+0.07km。取り逃がすと-0.05km</li>
              </ul>
            </section>
            <section class="ruleBlock">
              <h3>避けるもの</h3>
              <ul>
                <li>🕳️ 穴：落ちると即終了。👯‍♀️無敵中でも防げません。</li>
                <li>🚶・車両などの地上障害物：ジャンプで避けます。</li>
                <li>吊り下げバー：ジャンプせず、地上にいれば安全です。</li>
                <li>対向障害物：速度を見てジャンプするタイミングを決めます。</li>
              </ul>
            </section>
            <section class="ruleBlock">
              <h3>事故と逃走</h3>
              <ul>
                <li>障害物事故で警戒度+1。3回目の事故で🚓に捕まり終了します。</li>
                <li>事故ペナルティは1km未満で-0.10km、1km以降で-0.20kmです。</li>
                <li>事故後15秒は逃走モード。見た目速度は2倍ですが、走行距離の加算速度は通常と同じです。</li>
              </ul>
            </section>
            <section class="ruleBlock">
              <h3>👯‍♀️ 無敵</h3>
              <p>取得すると実際にプレイしている時間で8秒間、障害物事故だけを防ぎます。穴は防げません。無敵中に障害物へ当たると「無敵で突破!」になります。</p>
            </section>
            <section class="ruleBlock">
              <h3>記録</h3>
              <p>最終スコアは「実走行距離 + アイテム加算 − 事故・取り逃がしペナルティ」です。結果画面とランキングはkmで表示します。</p>
            </section>
          </div>
          <button id="rulesBackBtn">ホームに戻る</button>
        </div>
      </section>
'''
index = sub_once(
    index,
    r'      <section id="rules" class="screen">.*?      </section>\n(?=      <section id="name")',
    rules_html,
    'rules screen replacement',
    re.S,
)

result_rank_old = '''        <div class="card">
          <h2>ランキング</h2>
          <div id="resultRanking" class="rank">ランキング未設定</div>
          <p id="resultStats" class="small"></p>
        </div>'''
result_rank_new = '''        <details id="resultRankingDetails" class="card rankingDetails">
          <summary>詳細ランキングを見る</summary>
          <div class="rankingBody">
            <div id="resultRanking" class="rank">ランキング未設定</div>
            <p id="resultStats" class="small"></p>
          </div>
        </details>'''
index = replace_once(index, result_rank_old, result_rank_new, 'result ranking details')

index = sub_once(
    index,
    r'      function getGroundY\(x\) \{\n.*?      \}',
    '      function getGroundY(x) {\n        return groundY;\n      }',
    'flat ground function',
    re.S,
)

index, duration_count = re.subn(r'(INVINCIBLE_DURATION_SEC:\s*)4\b', r'\g<1>8', index, count=1)
if duration_count != 1:
    raise SystemExit(f'invincible duration constant: expected 1, got {duration_count}')
index = replace_once(index, '{ emoji: "👯‍♀️", kind: "invincible", value: 0, missPenalty: 0, duration: 4, placed: true }', '{ emoji: "👯‍♀️", kind: "invincible", value: 0, missPenalty: 0, duration: 8, placed: true }', 'invincible item duration')
index = replace_once(index, 'floatText(it.x + 14, it.y - 4, "👯‍♀️無敵 4.0s", "#f4eaff");', 'floatText(it.x + 14, it.y - 4, "👯‍♀️無敵 8.0s", "#f4eaff");', 'invincible pickup message')

index = replace_once(
    index,
    'ctx.ellipse(player.x + 22, getGroundY(player.x) + 7 + t * 7, 22 * shadowScale, 6 * shadowScale, 0, 0, Math.PI * 2);',
    'ctx.ellipse(player.x + 21, getGroundY(player.x) + 7 + t * 7, 18 * shadowScale, 5 * shadowScale, 0, 0, Math.PI * 2);',
    'truck shadow size',
)
index = replace_once(
    index,
    'ctx.ellipse(player.x + 21, player.y + 18, 31, 24, 0, 0, Math.PI * 2);',
    'ctx.ellipse(player.x + 21, player.y + 18, 28, 22, 0, 0, Math.PI * 2);',
    'truck invincible aura size',
)
truck_pos = index.find('ctx.fillText("🚚", player.x + 21, player.y + 18')
if truck_pos < 0:
    raise SystemExit('truck draw call not found')
font_pos = index.rfind('ctx.font = "42px serif";', 0, truck_pos)
if font_pos < 0:
    raise SystemExit('truck 42px font assignment not found')
index = index[:font_pos] + 'ctx.font = "36px serif";' + index[font_pos + len('ctx.font = "42px serif";'):]

index = replace_once(
    index,
    '          `kiriganaito\n逆走する🚚で穴と障害物をジャンプ回避。事故ると🚓から15秒逃走！\n${PUBLIC_URL}`,',
    '          `kiriganaito\n落とした積荷と落ちてるお金を拾い集めよう\n穴と障害物を見分けて、できるだけ遠くまで走ろう。\n${PUBLIC_URL}`,',
    'home share concept',
)

index = replace_once(index, '        if (mode === MODE.HOME) loadHomeRankingOnce();\n', '', 'remove automatic home ranking load')
ranking_setup = '''      function setupRankingDetails() {
        const homeDetails = $("homeRankingDetails");
        if (homeDetails) homeDetails.addEventListener("toggle", () => {
          if (homeDetails.open) loadHomeRankingOnce();
        });
        const resultDetails = $("resultRankingDetails");
        if (resultDetails) resultDetails.addEventListener("toggle", () => {
          if (resultDetails.open) fetchAndRenderResultRanking();
        });
      }
'''
index = replace_once(index, '      async function loadHomeRankingOnce() {\n', ranking_setup + '      async function loadHomeRankingOnce() {\n', 'ranking details setup')
index = replace_once(
    index,
    '      updateRetryButton();\n      flushPendingScores();\n      loadHomeRankingOnce();',
    '      updateRetryButton();\n      setupRankingDetails();\n      flushPendingScores();',
    'defer home ranking startup',
)

INDEX.write_text(index)

# Synchronize exact version strings across permanent tests and documents.
version_paths = [
    ROOT / 'SPEC.md',
    ROOT / 'TEST_REPORT.md',
    ROOT / 'P5_CHASE_INVINCIBLE_CONTRACT.md',
    ROOT / 'tests/effective-presentation-metrics.js',
    ROOT / 'tests/p2-density-regression.js',
    ROOT / 'tests/p3-pattern-regression.js',
    ROOT / 'tests/p4-air-obstacle-regression.js',
    ROOT / 'tests/p5-chase-invincible-regression.js',
    ROOT / 'tests/release-comprehensive.js',
]
for path in version_paths:
    if path.exists():
        path.write_text(path.read_text().replace(OLD_VERSION, NEW_VERSION))

# Update the P5 timing regression from 4 played seconds to 8 played seconds.
p5_test_path = ROOT / 'tests/p5-chase-invincible-regression.js'
p5_test = p5_test_path.read_text()
old_timing = '''  for (let i = 0; i < 120; i++) updateDancerInvincible(FIXED_STEP);
  const afterTwoPlayedSeconds = getDancerInvincibleRemainingSec();
  run.runMeters = 25 * 1000;
  run.maxRunMeters = run.runMeters;
  for (let i = 0; i < 120; i++) updateDancerInvincible(FIXED_STEP);
  const afterFourPlayedSeconds = getDancerInvincibleRemainingSec();
  const blockUntil = run.invincibleLargeHoleBlockUntilKm;'''
new_timing = '''  for (let i = 0; i < 120; i++) updateDancerInvincible(FIXED_STEP);
  const afterTwoPlayedSeconds = getDancerInvincibleRemainingSec();
  run.runMeters = 25 * 1000;
  run.maxRunMeters = run.runMeters;
  for (let i = 0; i < 120; i++) updateDancerInvincible(FIXED_STEP);
  const afterFourPlayedSeconds = getDancerInvincibleRemainingSec();
  for (let i = 0; i < 240; i++) updateDancerInvincible(FIXED_STEP);
  const afterEightPlayedSeconds = getDancerInvincibleRemainingSec();
  const blockUntil = run.invincibleLargeHoleBlockUntilKm;'''
p5_test = replace_once(p5_test, old_timing, new_timing, 'P5 eight-second timing scenario')
p5_test = replace_once(
    p5_test,
    '''    afterTwoPlayedSeconds,
    afterFourPlayedSeconds,
    blockUntil,''',
    '''    afterTwoPlayedSeconds,
    afterFourPlayedSeconds,
    afterEightPlayedSeconds,
    blockUntil,''',
    'P5 eight-second timing report',
)
old_validator = '''  if (Math.abs(run.initial - 4) > 1e-9) failures.push(`initial duration: ${run.initial}`);
  if (Math.abs(run.afterWallClockOnly - 4) > 1e-9) failures.push(`wall-clock decay: ${run.afterWallClockOnly}`);
  if (Math.abs(run.afterTwoPlayedSeconds - 2) > 1e-6) failures.push(`two-second duration: ${run.afterTwoPlayedSeconds}`);
  if (run.afterFourPlayedSeconds > 1e-6) failures.push(`four-second duration: ${run.afterFourPlayedSeconds}`);'''
new_validator = '''  if (Math.abs(run.initial - 8) > 1e-9) failures.push(`initial duration: ${run.initial}`);
  if (Math.abs(run.afterWallClockOnly - 8) > 1e-9) failures.push(`wall-clock decay: ${run.afterWallClockOnly}`);
  if (Math.abs(run.afterTwoPlayedSeconds - 6) > 1e-6) failures.push(`two-second duration: ${run.afterTwoPlayedSeconds}`);
  if (Math.abs(run.afterFourPlayedSeconds - 4) > 1e-6) failures.push(`four-second duration: ${run.afterFourPlayedSeconds}`);
  if (run.afterEightPlayedSeconds > 1e-6) failures.push(`eight-second duration: ${run.afterEightPlayedSeconds}`);'''
p5_test = replace_once(p5_test, old_validator, new_validator, 'P5 eight-second timing validator')
p5_test_path.write_text(p5_test)

# Synchronize P5 contract prose with the user-approved 8-second duration.
p5_contract_path = ROOT / 'P5_CHASE_INVINCIBLE_CONTRACT.md'
if p5_contract_path.exists():
    contract = p5_contract_path.read_text()
    contract = contract.replace('無敵4秒', '無敵8秒').replace('実プレイ時間4秒', '実プレイ時間8秒')
    contract = contract.replace('補充分は`x=-18`から提示し、4秒以内', '補充分は`x=-18`から提示し、8秒以内')
    old_block = '''取得直後: 4.000秒
PLAYING update 120回後: 約2.000秒
PLAYING update 240回後: 0秒
performance clockだけを30秒進めた場合: 4.000秒のまま'''
    new_block = '''取得直後: 8.000秒
PLAYING update 120回後: 約6.000秒
PLAYING update 240回後: 約4.000秒
PLAYING update 480回後: 0秒
performance clockだけを30秒進めた場合: 8.000秒のまま'''
    if old_block not in contract:
        raise SystemExit('P5 contract timing block not found')
    contract = contract.replace(old_block, new_block, 1)
    contract = contract.replace('固定step 240回で4秒終了', '固定step 480回で8秒終了')
    p5_contract_path.write_text(contract)

spec_path = ROOT / 'SPEC.md'
if spec_path.exists():
    spec = spec_path.read_text()
    if '## v22 実機フィードバックUI修正' not in spec:
        spec += '''\n\n## v22 実機フィードバックUI修正\n\n- コンセプトを「落とした積荷と落ちてるお金を拾い集めよう」へ統一する。\n- `getGroundY()`を水平化し、地面の波打ちを廃止する。\n- ホームと結果の詳細ランキングを初期状態で閉じる。\n- ホームの主要操作を上部へ集約する。\n- 👯‍♀️無敵を実プレイ時間8秒へ延長する。\n- player物理サイズ42x34を維持し、🚚描画だけ36pxへ縮小する。\n- ルールを目的、操作、取得物、危険、事故・逃走、無敵、記録へ分割する。\n- スコア式、ランキング送信値、Supabase、P2〜P5の安全契約は変更しない。\n'''
    spec_path.write_text(spec)

report_path = ROOT / 'TEST_REPORT.md'
if report_path.exists():
    report = report_path.read_text()
    if '## v22 実機フィードバックUI修正' not in report:
        report += '''\n\n## v22 実機フィードバックUI修正\n\n- 実機指摘に基づき地面を水平化。\n- ホームと結果の詳細ランキングを`details`で初期非表示化。\n- ホームの情報優先順位と操作配置を再構成。\n- コンセプト文言を「落とした積荷と落ちてるお金を拾い集めよう」へ統一。\n- 👯‍♀️無敵を実プレイ時間8秒へ延長。\n- player物理サイズを維持し、🚚描画だけ36pxへ縮小。\n- ルール情報を7区分へ整理。\n- `tests/device-feedback-ui-regression.js`とP1〜P5全回帰で検証する。\n'''
    report_path.write_text(report)

print('device feedback UI implementation patch applied')
