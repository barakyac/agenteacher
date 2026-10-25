"""Evaluation report for the Spelling/Language agent (spelling-prompt.md).

Calls OrchestratorAgent.spelling() directly -- the exact code path both
general chat and guided/teacher mode use -- for a set of curated learner
messages, and prints each verdict for human review. Needs Ollama running
locally with qwen3.5:4b installed (COACH_MODEL in orchestrator.py).

Note: orchestrator.spelling() is currently patched to always force
allowed=True (never blocks a message) and to downgrade a model 'blocked'
verdict to 'hint' -- see orchestrator.py. This report still shows the
model's raw status/hint so you can judge whether its language judgement
itself is accurate, even though it can no longer stop a message.

Run: python3 evals/eval_spelling.py
"""
from harness import banner, new_agent, run_method, section

CASES = [
    ("Clear misspelling -- should point to the word, not reveal the fix",
     'I want monney'),

    ("Grammatically off but correctly spelled -- spelling check ignores grammar",
     'I want many money'),

    ("Mistyped verb that looks like an acronym -- must flag asm, not the name",
     'i asm Barak'),

    ("Foreign language in Latin script -- previously blocked, now just a hint",
     'bonjour je voudrais parler francais'),

    ("Mixed Hebrew/English -- allowed",
     'שלום hello'),

    ("Borrowed place name + informal phrasing (the original false-positive report)",
     'ko samoi\ni hate pad thai'),

    ("URL/code-like token -- should not be treated as foreign language",
     'check example.com for info'),

    ("Short ambiguous shared word -- should be allowed, not guessed at",
     'ok'),

    ("Real learner question with no spelling issue",
     'how much water to buy?'),

    ("Long compound-tense sentence with one embedded typo -- should flag 'tommorow' without being thrown off by sentence complexity",
     'I will have been going to the gym, by the time you would have been going to school tommorow'),
]


def main():
    banner('SPELLING / LANGUAGE eval -- spelling-prompt.md')
    for title, text in CASES:
        agent = new_agent([{'role': 'user', 'content': text}])
        result, elapsed = run_method(agent, 'spelling')
        print(f'\n[{title}]  ({elapsed:.1f}s)')
        section('input', text)
        if isinstance(result, dict):
            section('ERROR', result['error'])
            continue
        events = [e for e in result if e.get('type') == 'result']
        if not events:
            section('ERROR', 'No result event emitted')
            continue
        event = events[0]
        section('allowed (always True post-patch)', str(event.get('allowed')))
        section('status', event.get('status', ''))
        section('hint', event.get('hint', ''))


if __name__ == '__main__':
    main()
