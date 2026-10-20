"""Evaluation report for the Teacher agent (teacher-prompt.md): guided
exercise grading AND the free-form "מורה לאנגלית" chat.

Unlike the other eval_*.py files, this logic isn't factored into a
reusable OrchestratorAgent method -- it lives inline in server.py's
do_POST (payload assembly, the guided-practice policy text, the JSON
verdict schema). Duplicating that here would drift out of sync, so this
script instead hits the real running server over HTTP, exactly like the
browser does. Start the server first:

    python3 server.py

Run: python3 evals/eval_teacher.py
"""
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

from harness import banner, section

PORT = os.environ.get('PORT', '8765')
BASE = f'http://127.0.0.1:{PORT}'
MODEL = os.environ.get('AGENTEACHER_EVAL_TEACHER_MODEL', 'qwen3.5:4b')  # UI's default guided-practice model

# Exercise context exactly as dist/app.js's guided() sends it: topic, the
# current stage's question, and the lesson's explanation. Copied verbatim
# from the lessons array in dist/app.js so wording stays in sync with the
# real app; update here if that array changes.
LESSONS = {
    'be-verb': {
        'topic': 'המילה שחסרה: am / is / are',
        'question': 'כתבו באנגלית: היא עסוקה.',
        'explanation': 'בעברית אפשר לומר ״אני עייף״ בלי פועל מפורש בהווה. באנגלית משפט כזה צריך את הפועל be.\nI → am · he / she / it → is · you / we / they → are\nהמבנה: נושא + be + תיאור.',
    },
    'do-does': {
        'topic': 'שאלות עם do / does',
        'question': 'כתבו באנגלית: האם היא גרה כאן?',
        'explanation': 'בעברית אפשר להפוך ״אתה עובד כאן״ לשאלה באמצעות ההקשר והאינטונציה. באנגלית בשאלות הווה פשוט עם פועל רגיל מוסיפים do או does לפני הנושא.\nDoes + she + work — בלי s בפועל עצמו.\nעם be המבנה אחר: Are you tired?',
    },
    'negation': {
        'topic': 'שלילה בלי תרגום מילה במילה',
        'question': 'כתבו באנגלית: היא לא אוהבת קפה.',
        'explanation': 'באנגלית לא מצמידים not ישירות לכל פועל. בהווה פשוט עם פועל רגיל משתמשים ב־do not או does not + צורת הבסיס.\nI don’t know. / She doesn’t know.\nעם be לא מוסיפים do: She is not tired.',
    },
}

# (title, lesson key, learner attempt) -- mirrors guided()'s messages shape:
# just the learner's text, no history, no "Current lesson" prefix.
GUIDED_CASES = [
    ('be-verb / correct', 'be-verb', 'She is busy.'),
    ('be-verb / retry (missing be)', 'be-verb', 'she busy'),
    ('be-verb / clarify (explicit answer request)', 'be-verb', 'אני לא יודעת, מה התשובה?'),
    ('be-verb / spelling typo should short-circuit before grading', 'be-verb', 'she buzy'),
    ('do-does / correct', 'do-does', 'Does she live here?'),
    ('do-does / retry (statement word order, no do-support)', 'do-does', 'she lives here?'),
    ('do-does / retry (double marking: does + lives)', 'do-does', 'Does she lives here?'),
    ('negation / correct', 'negation', "She doesn't like coffee."),
    ('negation / retry (literal word-for-word not)', 'negation', 'she not like coffee'),
    ('negation / retry (agreement: don\'t vs doesn\'t)', 'negation', "she don't like coffee"),
]

# (title, messages) for the model-select "מורה לאנגלית" free chat (no exercise).
FREE_CHAT_CASES = [
    ('Greeting -> warm one-liner + one question, no lesson dumped',
     [{'role': 'user', 'content': 'היי, את יכולה ללמד אותי אנגלית?'}]),

    ('Off-topic -> brief redirect back to English practice',
     [{'role': 'user', 'content': 'מה דעתך על הפוליטיקה בישראל?'}]),

    ("Preposition correction, hint only -- the prompt's own worked example",
     [{'role': 'user', 'content': 'hey chat, I live tel aviv, i am 30'}]),
]


def call(messages, exercise=None):
    payload = {'model': MODEL, 'mode': 'teacher', 'messages': messages}
    if exercise is not None:
        payload['exercise'] = exercise
    request = Request(f'{BASE}/api/chat', json.dumps(payload).encode(),
                       {'Content-Type': 'application/json', 'Origin': BASE})
    try:
        with urlopen(request, timeout=120) as response:
            return json.load(response)
    except URLError as error:
        return {'error': f'Could not reach {BASE} ({error}). Start the server first: python3 server.py'}


def main():
    banner('TEACHER eval -- teacher-prompt.md (guided exercise grading)')
    for title, lesson_key, attempt in GUIDED_CASES:
        result = call([{'role': 'user', 'content': attempt}], exercise=LESSONS[lesson_key])
        print(f'\n[{title}]')
        section('learner attempt', attempt)
        if 'error' in result:
            section('ERROR', result['error'])
            continue
        section('verdict', result.get('verdict', ''))
        section('reply', result.get('reply', ''))
        if result.get('spelling_hint'):
            section('spelling_hint (grading was skipped this turn)', result['spelling_hint'])

    banner('TEACHER eval -- teacher-prompt.md (free "מורה לאנגלית" chat)')
    for title, messages in FREE_CHAT_CASES:
        result = call(messages)
        print(f'\n[{title}]')
        section('learner message', messages[-1]['content'])
        if 'error' in result:
            section('ERROR', result['error'])
            continue
        section('reply', result.get('reply', ''))


if __name__ == '__main__':
    main()
