const lessons = [
 {title:'המילה שחסרה: am / is / are',he:'אני עייף',en:'I am tired.',explain:'בעברית אפשר לומר ״אני עייף״ בלי פועל מפורש בהווה. באנגלית משפט כזה צריך את הפועל be.\nI → am · he / she / it → is · you / we / they → are\nהמבנה: נושא + be + תיאור.',task:'כתבו באנגלית: היא עסוקה.',answers:['she is busy',"she’s busy","she's busy"],hint:'התחילו ב־She. איזו צורה של be מתאימה?',answer:'She is busy.',next:'they are happy',transfer:'עכשיו נסו משפט חדש: הם שמחים.',accepted:['they are happy',"they’re happy","they're happy"]},
 {title:'איפה שמים את התואר?',he:'בית גדול',en:'a big house',explain:'בעברית התואר בדרך כלל בא אחרי שם העצם: בית גדול. באנגלית תואר שמתאר שם עצם בא בדרך כלל לפניו: a big house.\nזה שונה ממשפט כמו The house is big — כאן התיאור בא אחרי is.',task:'תרגמו את הצירוף: מכונית אדומה (לא מכונית מסוימת).',answers:['a red car'],hint:'סדר המילים: a + צבע + שם העצם.',answer:'a red car',transfer:'נסו צירוף חדש: ספר קטן (לא ספר מסוים).',accepted:['a small book','a little book']},
 {title:'שאלות עם do / does',he:'אתה עובד כאן?',en:'Do you work here?',explain:'בעברית אפשר להפוך ״אתה עובד כאן״ לשאלה באמצעות ההקשר והאינטונציה. באנגלית בשאלות הווה פשוט עם פועל רגיל מוסיפים do או does לפני הנושא.\nDoes + she + work — בלי s בפועל עצמו.\nעם be המבנה אחר: Are you tired?',task:'כתבו באנגלית: האם היא גרה כאן?',answers:['does she live here'],hint:'התחילו ב־Does she, ואז הפועל בצורת הבסיס.',answer:'Does she live here?',transfer:'עכשיו: האם הם עובדים כאן?',accepted:['do they work here']},
 {title:'הרגל או משהו שקורה עכשיו?',he:'אני עובד עכשיו',en:'I am working now.',explain:'בעברית ״אני עובד״ יכול לתאר הרגל או פעולה שמתרחשת עכשיו. באנגלית מבדילים לעיתים קרובות:\nI work every day. — הרגל\nI am working now. — פעולה שמתרחשת עכשיו\nלא כל פועל מתאים לצורה המתמשכת: בדרך כלל אומרים I know, לא I am knowing.',task:'תרגמו: היא עובדת עכשיו.',answers:['she is working now',"she's working now","she’s working now"],hint:'צריך She + is + פועל שמסתיים ב־ing + now.',answer:'She is working now.',transfer:'עכשיו תארו הרגל: היא עובדת בכל יום.',accepted:['she works every day','she works everyday']},
 {title:'קטנה אבל חשובה: a / an',he:'יש לי כלב',en:'I have a dog.',explain:'בעברית אין מילה שמקבילה ישירות ל־a/an. באנגלית שם עצם ספיר ביחיד בדרך כלל צריך מילה לפניו.\nI have a dog. — כלב לא מסוים\nThe dog is happy. — הכלב המסוים\nבוחרים a או an לפי הצליל: an apple, אבל a university.',task:'כתבו באנגלית: יש לי תפוח.',answers:['i have an apple',"i've got an apple"],hint:'apple מתחילה בצליל תנועה. צריך an לפניה.',answer:'I have an apple.',transfer:'עכשיו: יש לי ספר.',accepted:['i have a book',"i've got a book"]},
 {title:'שלילה בלי תרגום מילה במילה',he:'אני לא יודע',en:'I do not know.',explain:'באנגלית לא מצמידים not ישירות לכל פועל. בהווה פשוט עם פועל רגיל משתמשים ב־do not או does not + צורת הבסיס.\nI don’t know. / She doesn’t know.\nעם be לא מוסיפים do: She is not tired.',task:'כתבו באנגלית: היא לא אוהבת קפה.',answers:["she doesn't like coffee",'she does not like coffee',"she doesn’t like coffee"],hint:'אחרי She צריך doesn’t, ואז like בלי s.',answer:"She doesn't like coffee.",transfer:'עכשיו: הם לא יודעים.',accepted:["they don't know",'they do not know',"they don’t know"]}
];
const $ = id => document.getElementById(id);
let saved; try { saved=JSON.parse(localStorage.getItem('agenteacher-progress')||'[]'); } catch { saved=[]; }
let completed=new Set(Array.isArray(saved)?saved.filter(x=>Number.isInteger(x)&&x>=0&&x<lessons.length):[]);
let current=0,stage=0,mode='guided',busy=false,history=[];
const normal=s=>s.toLowerCase().replace(/[.?!]/g,'').replace(/’/g,"'").replace(/\s+/g,' ').trim();
function bubble(text,who='teacher'){const box=document.createElement('div');box.className='bubble '+who;box.dir='auto';const label=document.createElement('span');label.className='speaker';label.textContent=who==='user'?'YOU · התור שלך':(mode==='general'?'AGENTEACHER · '+activeExpert:'AGENTEACHER · המורה שלך');box.append(label);for(const line of text.split('\n')){const row=document.createElement('div');row.dir='auto';row.style.unicodeBidi='plaintext';row.textContent=line||'\u00a0';box.append(row);}$('chat').append(box);$('chat').scrollTop=$('chat').scrollHeight;}
function drawNav(){$('lessons').replaceChildren();lessons.forEach((lesson,i)=>{const b=document.createElement('button');b.className=i===current?'selected':'';b.setAttribute('aria-current',i===current?'step':'false');const n=document.createElement('small');n.textContent=completed.has(i)?'✓':String(i+1).padStart(2,'0');const t=document.createElement('strong');t.textContent=lesson.title;b.append(n,t);b.onclick=()=>{if(!busy)start(i)};$('lessons').append(b)});$('progress').textContent=`${completed.size} / ${lessons.length}`;}
function actions(entries){$('actions').replaceChildren();for(const [text,fn]of entries){const b=document.createElement('button');b.textContent=text;b.onclick=fn;$('actions').append(b)}}
let activeExpert='שותף לשיחה';
function start(i){if(mode==='general'){startGeneral();return;}current=i;stage=0;history=[];drawNav();const l=lessons[i];$('title').textContent=l.title;$('hebrew').textContent=l.he;$('english').textContent=l.en;$('chat').replaceChildren();$('message').value='';if(mode==='guided'){bubble(l.explain+'\n\nהתור שלך: '+l.task);actions([['רמז קטן',()=>bubble(stage===0?l.hint:'השתמשו באותו מבנה עם המילים של המשפט החדש.')],['הסבר שוב',()=>bubble(l.explain)]]);}else{bubble('אפשר לשאול בעברית או לתרגל באנגלית. נתחיל בנושא ״'+l.title+'״.\nהשיחה דורשת מודל מקומי פעיל.');actions([['נתחיל שיעור',()=>sendAI('למד אותי את הנושא: '+l.title)],['למה המבנה שונה?',()=>sendAI('הסבר את ההבדל בין '+l.he+' לבין '+l.en)]]);}}
async function guided(text){
 if(busy)return;
 if(stage===2){bubble('התרגול הושלם. אפשר לבחור נושא חדש או לתרגל שוב.');return;}
 if(!$('model').value){bubble('כדי לקבל הסבר אישי צריך מודל מקומי פעיל. בחרו מודל או לחצו על רענון חיבור.');return;}
 const l=lessons[current]; const pending=[...history,{role:'user',content:text}];
 bubble(text,'user');setBusy(true);
 try{
  const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:$('model').value,exercise:{topic:l.title,question:stage===0?l.task:l.transfer,explanation:l.explain},messages:pending.slice(-28)})});
  const data=await res.json();if(!res.ok)throw Error(data.error||'שגיאת חיבור');
  if(!['correct','retry','clarify'].includes(data.verdict)||typeof data.reply!=='string')throw Error('לא התקבל משוב תקין. נסו שוב.');
  if(data.spelling_hint)agentCard('SPELLING · רמז לאיות',data.spelling_hint);bubble(data.reply);history=[...pending,{role:'assistant',content:(data.spelling_hint?data.spelling_hint+'\n':'')+data.reply}];$('message').value='';
  if(data.verdict==='correct'){
   if(stage===0){stage=1;history=[];bubble(l.transfer);}
   else{stage=2;completed.add(current);try{localStorage.setItem('agenteacher-progress',JSON.stringify([...completed]))}catch{}drawNav();bubble('השלמתם את שני תרגילי הנושא.');actions([['לנושא הבא',()=>start((current+1)%lessons.length)],['לתרגל שוב',()=>start(current)]]);}
  }
 }catch(err){bubble('לא התקבל משוב: '+err.message+'\nהתשובה נשמרה בשדה, ואפשר לנסות שוב.');}
 finally{setBusy(false);$('message').focus();}
}
function setBusy(value){busy=value;$('send').disabled=value;$('guided').disabled=value;$('ai').disabled=value;$('general').disabled=value;$('expert').disabled=value;$('custom-expert').disabled=value;$('new-general').disabled=value;$('message').disabled=value;$('model').disabled=value;$('reset').disabled=value;document.querySelectorAll('#actions button,#lessons button').forEach(b=>b.disabled=value);$('send').textContent=value?'חושבים…':'שליחה ↗';}
async function refresh(){try{const res=await fetch('/api/status');if(!res.ok)throw Error();const data=await res.json();const previous=$('model').value;$('model').replaceChildren();data.models.forEach(m=>{const o=document.createElement('option');o.value=m;o.textContent=m;$('model').append(o)});if(data.models.includes(previous))$('model').value=previous;else if(data.models.includes('qwen3.5:4b'))$('model').value='qwen3.5:4b';$('connection').textContent=data.models.length?'מחובר ל־Ollama המקומי. איכות ההסבר בעברית תלויה במודל שנבחר.':'אין מודל מקומי זמין. התקינו Ollama והורידו מודל, ואז לחצו רענון. אפשר לקרוא את השיעורים; בדיקת תשובות דורשת מודל.';}catch{$('connection').textContent='לא ניתן להתחבר לשרת המקומי. הפעילו שוב את server.py.';}}
async function sendAI(text){if(mode==='general')return sendTeam(text);if(busy)return;if(!$('model').value){bubble('כדי לשוחח באופן חופשי, צריך לחבר מודל מקומי. הוראות ההפעלה נמצאות בקובץ README.');return;}bubble(text,'user');const pending=[...history,{role:'user',content:text}];setBusy(true);try{const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:$('model').value,mode:mode==='general'?'general':'teacher',expert:activeExpert,messages:mode==='general'?pending.slice(-28):[{role:'user',content:'Current lesson: '+lessons[current].title},...pending.slice(-28)]})});const data=await res.json();if(!res.ok)throw Error(data.error||'שגיאת חיבור');if(data.spelling_hint)agentCard('SPELLING · רמז לאיות',data.spelling_hint);bubble(data.reply);history=[...pending,{role:'assistant',content:(data.spelling_hint?data.spelling_hint+'\n':'')+data.reply}];$('message').value='';}catch(err){bubble('לא התקבלה תשובה: '+err.message+'\nאפשר לנסות שוב.');}finally{setBusy(false);$('message').focus();}}
$('composer').onsubmit=e=>{e.preventDefault();const text=$('message').value.trim();if(!text||busy)return;if(mode!=='guided')sendAI(text);else guided(text)};
$('message').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('composer').requestSubmit()}};
function startGeneral(){history=[];$('chat').replaceChildren();$('message').value='';$('title').textContent='שיחה עם '+activeExpert;bubble('על מה נדבר? אפשר לכתוב באנגלית; אענה לתוכן ואעזור לשפר את הניסוח תוך כדי.');actions([]);}
for(const name of ['guided','ai','general'])$(name).onclick=()=>{if(busy)return;mode=name;for(const n of ['guided','ai','general'])$(n).classList.toggle('active',n===name);$('expert-panel').hidden=name!=='general';document.querySelector('.comparison').hidden=name==='general';$('lessons').hidden=name==='general';$('message').placeholder=name==='general'?'על מה תרצו לדבר? אפשר לכתוב באנגלית…':'כאן כותבים באנגלית…';$('footnote').textContent=name==='general'?'שיחת תפקיד עם AI · הסבר קצר על טעות מרכזית, בלי לחשוף את התיקון אלא אם מבקשים.':'טעות היא נקודת התחלה. נבין אותה יחד, משפט אחד בכל פעם.';$('mode-note').textContent=name==='general'?'שיחה חופשית + עזרה באנגלית':name==='ai'?'מורה לאנגלית · Ollama מקומי':'תרגילים מובנים · משוב מהמודל';start(current);};
$('expert').onchange=()=>{$('custom-expert').hidden=$('expert').value!=='custom';};
$('new-general').onclick=()=>{if(busy)return;const value=$('expert').value==='custom'?$('custom-expert').value.trim():$('expert').value;if(!value){$('custom-expert').focus();return;}activeExpert=value;startGeneral();};
$('refresh').onclick=refresh;$('reset').onclick=()=>{if(confirm('לאפס את ההתקדמות בכל הנושאים?')){completed.clear();try{localStorage.removeItem('agenteacher-progress')}catch{}start(0)}};start(0);

$('model-panel').hidden=false;$('mode-note').textContent='תרגילים מובנים · משוב מהמודל';refresh();

function agentCard(title, initial){const box=document.createElement('div');box.className='bubble teacher';const label=document.createElement('span');label.className='speaker';label.textContent=title;const body=document.createElement('div');body.dir='auto';body.style.unicodeBidi='plaintext';body.textContent=initial;box.append(label,body);$('chat').append(box);return body;}
async function sendTeam(text){
 if(busy)return;if(!$('model').value){bubble('בחרו מודל מקומי פעיל.');return;}
 const pending=[...history,{role:'user',content:text}];bubble(text,'user');
 const coach=agentCard('ENGLISH COACH · רמז לאנגלית','בודק את האנגלית…');
 const spelling=agentCard('SPELLING · איות ושפה','בודק איות ושפה…');
 const conversation=agentCard('CONVERSATION · '+activeExpert,'מכין תשובה…');
 setBusy(true);let answer='',hint='',conversationFailed=false,coachFinished=false,completed=false,spellingFinished=false,blocked=false;
 function event(e){
  if(e.agent==='spelling'&&e.type==='result'){spellingFinished=true;spelling.textContent=e.hint||'לא זוהתה טעות איות ברורה.';}
  if(e.agent==='spelling'&&e.type==='error'){spellingFinished=true;spelling.textContent=e.message;}
  if(e.type==='blocked'){blocked=true;completed=true;conversation.textContent=e.message||'ההודעה לא נשלחה לשיחה: כתבו בעברית או באנגלית.';coach.textContent='בדיקת הדקדוק לא הוצגה.';}
  if(e.agent==='conversation'&&e.type==='delta'){answer+=e.text;conversation.textContent=answer;}
  if(e.agent==='coach'&&e.type==='result'){coachFinished=true;hint=e.status==='hint'?e.hint:'';coach.textContent=hint||(e.status==='ok'?'לא זוהתה טעות דקדוקית ברורה.':'אין טקסט באנגלית לבדיקה.');}
  if(e.type==='error'){if(e.agent==='coach'){coachFinished=true;coach.textContent=e.message;}else if(e.agent==='conversation'){conversationFailed=true;conversation.textContent=(answer?answer+'\n\n':'')+e.message;}}
  if(e.type==='complete')completed=true;
  $('chat').scrollTop=$('chat').scrollHeight;
 }
 try{
  const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:$('model').value,mode:'general',expert:activeExpert,messages:pending.slice(-28)})});
  if(!res.ok){const data=await res.json();throw Error(data.error||'שגיאת חיבור');}
  const reader=res.body.getReader(),decoder=new TextDecoder();let buffer='';
  while(true){const {value,done}=await reader.read();buffer+=done?decoder.decode():decoder.decode(value,{stream:true});let end;while((end=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(line.trim())event(JSON.parse(line));}if(done)break;}
  if(buffer.trim())event(JSON.parse(buffer));if(!completed)throw Error('החיבור הסתיים לפני השלמת הבדיקה.');
  if(answer&&!conversationFailed&&!blocked){history=[...pending,{role:'assistant',content:answer+(hint?'\n[English coaching hint] '+hint:'')}];$('message').value='';}
 }catch(err){if(!conversationFailed)conversation.textContent=(answer?answer+'\n\n':'')+'שגיאה: '+err.message;if(!coachFinished)coach.textContent='בדיקת האנגלית לא הושלמה.';if(!spellingFinished)spelling.textContent='בדיקת האיות והשפה לא הושלמה.';}
 finally{setBusy(false);$('message').focus();}
}
