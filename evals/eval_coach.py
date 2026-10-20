"""Evaluation report for the English Coach agent (coach-prompt.md).

Calls OrchestratorAgent.coach() directly -- the exact code path general
chat uses -- for a set of curated learner messages, and prints each
verdict for human review. Needs Ollama running locally with qwen3.5:4b
installed (COACH_MODEL in orchestrator.py).

Run: python3 evals/eval_coach.py
"""
from harness import banner, new_agent, run_method, section

CASES = [
    ("Missing copula (classic be-verb gap)",
     [{'role': 'user', 'content': 'she busy'}]),

    ("Uncountable noun used with 'many'",
     [{'role': 'user', 'content': 'i want many money'}]),

    ("Already correct -- should not flag anything",
     [{'role': 'user', 'content': 'I want more money.'}]),

    ("Hebrew only, no English being practiced -- not_english",
     [{'role': 'user', 'content': 'שלום, אפשר לדבר על טיולים?'}]),

    ("Casual contraction, grammatical -- should not be flagged as an error",
     [{'role': 'user', 'content': "I don't wanna go today"}]),

    ("Subject-verb agreement + borrowed place name",
     [{'role': 'user', 'content': 'me love Thailand'}]),

    ("Past tense + missing preposition, one central issue expected",
     [{'role': 'user', 'content': 'I go to store yesterday'}]),

    ("Trivial fragment -- should not invent an error",
     [{'role': 'user', 'content': 'ok'}]),

    ("Explicit request for a previous correction -- should answer with hint, same two-line format",
     [
        {'role': 'user', 'content': 'she busy'},
        {'role': 'assistant', 'content': 'באנגלית צריך פועל שמקשר בין הנושא לתיאור. איזו צורה מתאימה ל-she?\nShe is busy.'},
        {'role': 'user', 'content': 'מה המשפט הנכון?'},
     ]),
]


def main():
    banner('ENGLISH COACH eval -- coach-prompt.md')
    for title, messages in CASES:
        agent = new_agent(messages)
        result, elapsed = run_method(agent, 'coach')
        print(f'\n[{title}]  ({elapsed:.1f}s)')
        section('input (last user message)', messages[-1]['content'])
        if isinstance(result, dict):
            section('ERROR', result['error'])
            continue
        events = [e for e in result if e.get('type') == 'result']
        if not events:
            section('ERROR', 'No result event emitted')
            continue
        event = events[0]
        section('status', event.get('status', ''))
        section('hint', event.get('hint', ''))
        if event.get('status') == 'hint':
            lines = event.get('hint', '').split('\n')
            if len(lines) != 2:
                section('FORMAT WARNING', f'Expected exactly 2 lines (explanation + corrected sentence), got {len(lines)}')


if __name__ == '__main__':
    main()
