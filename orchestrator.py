"""Three roles: code orchestrator, streaming conversation agent, independent coach."""
import json
import os
import queue
import threading
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
COACH_MODEL = os.environ.get('AGENTEACHER_COACH_MODEL', 'qwen3.5:4b')


class OrchestratorAgent:
    """Own routing, concurrent dispatch, validation and independent failures.

    No LLM planning call: the two tasks are known in advance. Ollama decides
    actual GPU concurrency; concurrent HTTP calls don't guarantee faster inference.
    """
    def __init__(self, model, expert, messages):
        self.model, self.expert, self.messages = model, expert, messages
        self.events = queue.Queue()
        self.cancelled = threading.Event()
        self.started = time.monotonic()

    def emit(self, agent, kind, **fields):
        if not self.cancelled.is_set():
            self.events.put({'agent': agent, 'type': kind, 'elapsed': round(time.monotonic()-self.started, 2), **fields})

    def call(self, model, prompt, messages, stream=False, schema=None):
        payload = {'model': model, 'messages': [{'role': 'system', 'content': prompt}]+messages,
                   'think': False, 'stream': stream, 'keep_alive': '15m',
                   'options': {'temperature': 0.2, 'num_predict': 240}}
        if schema:
            payload['format'] = schema
        return urlopen(Request('http://127.0.0.1:11434/api/chat', json.dumps(payload).encode(),
                               {'Content-Type': 'application/json'}), timeout=90)

    def conversation(self):
        prompt = (ROOT/'conversation-prompt.md').read_text()+'\nRequested role: '+self.expert
        with self.call(self.model, prompt, self.messages, stream=True) as response:
            ended = False
            for line in response:
                if self.cancelled.is_set():
                    return
                event = json.loads(line)
                if event.get('error'):
                    raise ValueError('Model failed')
                chunk = event.get('message', {}).get('content', '')
                if chunk:
                    self.emit('conversation', 'delta', text=chunk)
                if event.get('done'):
                    ended = True
                    break
            if not ended:
                raise ValueError('Incomplete model response')

    def coach(self):
        schema = {'type':'object','properties':{
            'status':{'type':'string','enum':['hint','ok','not_english']},
            'hint':{'type':'string'}}, 'required':['status','hint'], 'additionalProperties':False}
        # A short original conversation excerpt helps resolve fragments and references.
        with self.call(COACH_MODEL, (ROOT/'coach-prompt.md').read_text(), self.messages[-5:], schema=schema) as response:
            result = json.loads(json.load(response)['message']['content'])
        if result.get('status') not in ('hint','ok','not_english') or not isinstance(result.get('hint'),str):
            raise ValueError('Invalid coaching response')
        if result['status']=='hint' and not result['hint'].strip():
            raise ValueError('Empty hint')
        self.emit('coach','result', **result)

    def spelling(self):
        schema={'type':'object','properties':{'allowed':{'type':'boolean'},'status':{'type':'string','enum':['hint','ok','blocked']},'hint':{'type':'string'}},'required':['allowed','status','hint'],'additionalProperties':False}
        with self.call(COACH_MODEL,(ROOT/'spelling-prompt.md').read_text(),[self.messages[-1]],schema=schema) as response:
            result=json.loads(json.load(response)['message']['content'])
        if not isinstance(result.get('allowed'),bool) or result.get('status') not in ('hint','ok','blocked') or not isinstance(result.get('hint'),str):
            raise ValueError('Invalid spelling response')
        if result['allowed'] == (result['status']=='blocked') or (result['status']=='hint' and not result['hint'].strip()):
            raise ValueError('Inconsistent spelling response')
        if not result['allowed']:
            result['hint']='אפשר לכתוב רק בעברית או באנגלית. Please use Hebrew or English only.'
        self.emit('spelling','result',**result)

    def worker(self, name, action):
        try:
            action()
        except Exception:
            self.emit(name, 'error', message='לא התקבלה תשובה מהסוכן הזה. אפשר לנסות שוב.')
        finally:
            self.emit(name, 'done')

    def run(self):
        yield {'agent':'orchestrator','type':'start','conversation_model':self.model,'coach_model':COACH_MODEL}
        for name, action in [('conversation',self.conversation),('coach',self.coach),('spelling',self.spelling)]:
            threading.Thread(target=self.worker,args=(name,action),daemon=True).start()
        finished=set()
        allowed=None
        pending=[]
        try:
            while len(finished)<3:
                remaining=100-(time.monotonic()-self.started)
                if remaining<=0:
                    for name in {'conversation','coach','spelling'}-finished:
                        yield {'agent':name,'type':'error','message':'זמן ההמתנה הסתיים. אפשר לנסות שוב.'}
                    break
                try:
                    event=self.events.get(timeout=min(5,remaining))
                except queue.Empty:
                    yield {'agent':'orchestrator','type':'heartbeat'}
                    continue
                if event['type']=='done':
                    finished.add(event['agent'])
                if event['agent']=='spelling':
                    yield event
                    if event['type']=='result':
                        allowed=event['allowed']
                        if not allowed:
                            yield {'agent':'orchestrator','type':'blocked'}
                            return
                        for buffered in pending:
                            yield buffered
                        pending.clear()
                    elif event['type']=='error':
                        yield {'agent':'orchestrator','type':'blocked','message':'בדיקת השפה נכשלה. נסו שוב.'}
                        return
                elif allowed:
                    yield event
                else:
                    pending.append(event)
            yield {'agent':'orchestrator','type':'complete'}
        finally:
            self.cancelled.set()
