#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const TARGETS = [1000, 5000, 10000, 30000, 150000];
const seeds = [1001,1002,1003,1004,1005,2001,2002,2003,2004,2005,3001,3002,3003,3004,3005];
const SUPABASE_HOST = 'https://mlpnjgezrnhdxsxolyzj.supabase.co';
const MAX_STEPS_FOR_150KM = 260000;
function mulberry32(a){return function(){let t=a+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return ((t^t>>>14)>>>0)/4294967296}}
function makeEl(id){
  const el={id,textContent:'',value:'',hidden:false,className:'',children:[],style:{},onclick:null,
    classList:{add(){},remove(){},toggle(){}},append(...xs){this.children.push(...xs)},appendChild(x){this.children.push(x);return x},
    addEventListener(){},setAttribute(){},getBoundingClientRect(){return {width:390,height:430}}};
  Object.defineProperty(el,'innerHTML',{get(){return this.children.map(c=>c.textContent||'').join('')},set(v){this.children=[];this.textContent=String(v)}});
  return el;
}
function createContext(seed){
  const elements=new Map();
  const ids=['home','rules','name','game','result','error','gameCanvas','startBtn','jumpBtn','retireBtn','homeRanking','resultRanking','homeStats','resultStats','homeToast','playerName','nameError','hudRun','hudScore','hudTime','hudChase','hudDanger','hudChaseBox','hudDangerBox','playStatus','resultReason','resultComment','resultScore','resultBreakdown','rankingStatus','rankingRetryBtn','clientVersionNote','debug','errorText','homeBtn','errorHomeBtn','nameBtn','rulesBtn','rulesBackBtn','readyBtn','otherGamesResult'];
  ids.forEach(id=>elements.set(id,makeEl(id)));
  const drawCalls=[];
  const canvas=elements.get('gameCanvas');
  canvas.getContext=()=>new Proxy({createLinearGradient(){return {addColorStop(){}}},createRadialGradient(){return {addColorStop(){}}},measureText(t){return {width:String(t).length*10}},fillText(t,x,y){drawCalls.push({text:String(t),x,y})}},
    {get(t,p){if(p in t)return t[p]; return ()=>{}},set(){return true}});
  const storage=new Map([['kiriganaitoName','AUTO']]);
  const blockedRequests=[], consoleErrors=[], consoleWarnings=[];
  global.window=global; global.addEventListener=()=>{}; global.setTimeout=(fn)=>0;
  global.document={getElementById:id=>elements.get(id)||(elements.set(id,makeEl(id)),elements.get(id)),createElement:tag=>makeEl(tag),addEventListener(){}};
  global.localStorage={getItem:k=>storage.has(k)?storage.get(k):null,setItem:(k,v)=>storage.set(k,String(v)),removeItem:k=>storage.delete(k)};
  global.performance={now:()=>0}; global.requestAnimationFrame=()=>0; global.cancelAnimationFrame=()=>{}; global.devicePixelRatio=1;
  global.fetch=async(url,opts={})=>{ const u=String(url); blockedRequests.push({url:u,body:opts.body||''}); if(!u.startsWith(SUPABASE_HOST)) throw new Error('Unexpected network: '+u); return {ok:true,json:async()=>u.includes('get_game_play_stats')?{play_count:0,player_count:0}:[]}; };
  global.console={...console,error:(...a)=>{consoleErrors.push(a.join(' ')); console.error(...a)},warn:(...a)=>{consoleWarnings.push(a.join(' ')); console.warn(...a)}};
  Math.random=mulberry32(seed);
  return {elements,storage,blockedRequests,consoleErrors,consoleWarnings,drawCalls};
}
function runOne(seed,target){
  const ctx=createContext(seed); const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8'); const script=html.match(/<script>([\s\S]*)<\/script>/)[1];
  const appended=`;(()=>{
fetchBestRanking=async()=>({ok:true,rows:[],error:''}); fetchPlayStats=async()=>({ok:true,stats:{play_count:0,player_count:0},error:''});
el.resultComment=$('resultComment'); sendScoreAfterResult=async(result)=>{global.__mockSubmitPayload=pendingToRpcPayload({gameSlug:GAME_SLUG,displayName:'AUTO',score:Math.trunc(Number(result.score)),clientVersion:CLIENT_VERSION}); setRankingStatus('ランキング送信モック'); return {ok:true}}; flushPendingScores=async()=>({ok:true});
el.playerName.value='AUTO'; localStorage.setItem('kiriganaitoName','AUTO'); startGame();
const target=${target}, maxSteps=${MAX_STEPS_FOR_150KM}; let maxRun=0,maxScore=0,maxDanger=0,lastJumpAt=null,sawDancer=false,dancerPicked=false,sawBike=false,bikeCleared=false, bikeJumped=false;
let lastVisible={holes:[],obstacles:[],items:[]}, lastPlayer={}, lastPatternName='', warningRendered=false, truckBlackRisk=false, lastDangerAhead=[];
function snap(){ lastVisible={holes:holes.map(h=>({x:+h.x.toFixed(1),w:+h.w.toFixed(1),right:+(h.x+h.w).toFixed(1)})).slice(-6),obstacles:obstacles.map(o=>({x:+o.x.toFixed(1),emoji:o.emoji,direction:o.direction,speed:o.speed})).slice(-8),items:items.map(it=>({x:+it.x.toFixed(1),y:+it.y.toFixed(1),emoji:it.emoji,kind:it.kind})).slice(-8)}; lastPlayer={x:+player.x.toFixed(1),y:+player.y.toFixed(1),vy:+player.vy.toFixed(1),onGround:player.onGround,jumping:!player.onGround}; lastPatternName=spawn.lastPatternName; }
function decide(){ const d=[]; for(const h of holes){ const lead=player.x-(h.x+h.w); const center=(h.x+h.w/2)-player.x; if(lead>-30&&lead<210)d.push({type:'hole',lead:+lead.toFixed(1),center:+center.toFixed(1),width:+h.w.toFixed(1)}); }
 for(const o of obstacles){ if(o.emoji==='🚴')sawBike=true; const lead=player.x-(o.x+o.w); const lim=o.direction===1?230:180; if(lead>-45&&lead<lim)d.push({type:'obstacle',lead:+lead.toFixed(1),emoji:o.emoji,direction:o.direction,speed:o.speed}); }
 for(const it of items){ if(it.emoji==='👯‍♀️')sawDancer=true; }
 lastDangerAhead=d; let jump=false; for(const q of d){ if(q.type==='hole' && q.lead>=82 && q.lead<=172) jump=true; if(q.type==='obstacle' && q.direction===-1 && q.lead>=80 && q.lead<=150) jump=true; if(q.type==='obstacle' && q.direction===1 && q.lead>=115 && q.lead<=215) jump=true; }
 if(player.onGround && jump){ inputState.jumpBuffer=HIT.JUMP_BUFFER_SEC; lastJumpAt={runMeters:+run.runMeters.toFixed(1),elapsed:+run.elapsed.toFixed(2),dangerAhead:d}; if(d.some(q=>q.emoji==='🚴')) bikeJumped=true; }
}
for(let step=0; step<maxSteps && mode===MODE.PLAYING && run.runMeters<target; step++){ decide(); update(FIXED_STEP); snap(); maxRun=Math.max(maxRun,run.runMeters); maxScore=Math.max(maxScore,run.scoreMeters); maxDanger=Math.max(maxDanger,run.maxDanger); if(run.dancerItems>0)dancerPicked=true; if(sawBike&&bikeJumped&&run.accidents===0&&run.runMeters>900)bikeCleared=true; if(holes.some(h=>h.x<W&&h.x+h.w>0)) warningRendered=true; if(holes.some(h=>h.x+h.w<player.x&&h.x+h.w>player.x-60)&&player.inv>0) truckBlackRisk=true; }
if(mode===MODE.PLAYING && run.runMeters>=target) finishGame('自然走行で目標到達');
function classify(){ const reason=(resultSnapshot&&resultSnapshot.reason)||run.finishReason||''; const h=lastVisible.holes[0]; const o=lastVisible.obstacles[0]; if(reason.includes('穴')){ if(o&&h&&Math.abs(o.x-h.x)<120)return o.x<h.x?'hole_after_obstacle_unavoidable':'obstacle_after_hole_unavoidable'; if(lastJumpAt&&lastJumpAt.dangerAhead&&lastJumpAt.dangerAhead.some(x=>x.type==='hole')){ const q=lastJumpAt.dangerAhead.find(x=>x.type==='hole'); if(q.lead<95)return 'hole_timing_late'; if(q.lead>155)return 'hole_timing_early'; return 'autopilot_limit'; } return 'hole_timing_late'; } if(reason.includes('🚓')) return 'oncoming_unavoidable'; if(lastVisible.obstacles.some(x=>x.emoji==='🚴')&&!bikeCleared)return 'bike_not_cleared'; return mode===MODE.RESULT&&run.runMeters>=target?'none':'unknown'; }
global.__result={seed:${seed},target,reached:!!(resultSnapshot&&resultSnapshot.runMeters>=target),maxRunMeters:Math.round(maxRun),maxScoreMeters:maxScore,finishReason:(resultSnapshot&&resultSnapshot.reason)||run.finishReason||'',failureCategory:classify(),lastPatternName,accidents:run.accidents,maxDanger,sawDancer,dancerPicked,sawBike,bikeCleared,warningRendered,truckBlackRisk,lastVisible,lastPlayer,lastJumpAt,holesLength:holes.length,obstaclesLength:obstacles.length,itemsLength:items.length,particlesLength:particles.length,mockSubmitPayload:global.__mockSubmitPayload};
})();`;
  try{Function(script+appended)()}catch(e){ctx.consoleErrors.push(e.stack||String(e))}
  return {...global.__result, consoleErrors:ctx.consoleErrors, consoleWarnings:ctx.consoleWarnings, supabaseRequests:ctx.blockedRequests};
}
const runs=[]; let stopAt=null; for(const target of TARGETS){ for(const seed of seeds) runs.push(runOne(seed,target)); if(!runs.some(r=>r.target===target&&r.reached)){stopAt=target; break;} }
const best=runs.reduce((a,b)=>(!a||b.maxRunMeters>a.maxRunMeters)?b:a,null); const highest=TARGETS.filter(t=>runs.some(r=>r.target===t&&r.reached)).pop()||0;
const counts=(k)=>runs.reduce((m,r)=>(m[r[k]||'']=(m[r[k]||'']||0)+1,m),{}); const top=(obj)=>Object.entries(obj).sort((a,b)=>b[1]-a[1])[0]?.[0]||'';
const report={generatedAt:new Date().toISOString(),targets:TARGETS,seeds,supabaseMocked:true,realSupabaseSubmission:false,summary:{maxRunMeters:best?.maxRunMeters||0,maxScoreMeters:best?.maxScoreMeters||0,bestSeed:best?.seed||0,highestTargetReached:highest,natural150kmReached:runs.some(r=>r.target===150000&&r.reached)},runs,findings:[`Highest target reached: ${highest}m`,`Best natural run: ${best?.maxRunMeters||0}m seed ${best?.seed||0}`,`Most common failure category: ${top(counts('failureCategory'))}`],recommendedFixes:['検証結果に基づく候補のみ: 穴・障害物複合パターンの安全余白、警告描画と当たり判定位置、🚴のクリアランスを人間プレイで再確認する。ゲーム本体は未変更。']};
fs.mkdirSync(path.join(__dirname,'..','artifacts'),{recursive:true}); fs.writeFileSync(path.join(__dirname,'..','artifacts','progressive-autoplay-report.json'),JSON.stringify(report,null,2));
const reasonTop=top(counts('finishReason')), failTop=top(counts('failureCategory'));
const summary=`実行コマンド: node tests/progressive-autoplay.js\n検証方法: index.html のゲームロジックを Node ハーネスで読み込み、runMeters/scoreMeters を直接代入せず、画面上の holes/obstacles/items と player 状態を読んでジャンプ入力だけを行う自然走行を複数 seed・段階目標で実行。\nSupabase遮断: fetch とランキング/送信関数をテスト内でモックし、${SUPABASE_HOST} への実送信を行わず submit_score は成功扱い、ランキングは空、統計は0件扱い。\n1km到達: ${runs.some(r=>r.target===1000&&r.reached)?'可':'不可'}\n5km到達: ${runs.some(r=>r.target===5000&&r.reached)?'可':'不可'}\n10km到達: ${runs.some(r=>r.target===10000&&r.reached)?'可':'不可'}\n30km到達: ${runs.some(r=>r.target===30000&&r.reached)?'可':'不可'}\n150km自然到達: ${runs.some(r=>r.target===150000&&r.reached)?'可':'不可'}\n最大到達距離: ${best?.maxRunMeters||0}m\n最大補正込みスコア: ${best?.maxScoreMeters||0}m\n最多終了理由: ${reasonTop}\n最多失敗分類: ${failTop}\n🚴: 認識=${runs.some(r=>r.sawBike)} / ジャンプ越え=${runs.some(r=>r.bikeCleared)}\n👯‍♀️: 認識=${runs.some(r=>r.sawDancer)} / 取得=${runs.some(r=>r.dancerPicked)}\n穴の⚠️表示: 描画対象に含まれる穴あり=${runs.some(r=>r.warningRendered)}。ロジック上の穴矩形と警告表示の差は要目視確認。\n穴手前の🚚黒化疑い: ${runs.some(r=>r.truckBlackRisk)}\nconsole error/warning: errors=${runs.reduce((n,r)=>n+r.consoleErrors.length,0)}, warnings=${runs.reduce((n,r)=>n+r.consoleWarnings.length,0)}\n修正候補: recommendedFixes を参照。今回はゲーム本体を修正していない。\n`;
fs.writeFileSync(path.join(__dirname,'..','artifacts','progressive-autoplay-summary.txt'),summary); console.log(summary); console.log(JSON.stringify(report.summary,null,2));
