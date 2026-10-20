"""Shared helpers for the agent evaluation reports in this directory.

These are human-judged quality reports, not pass/fail tests: LLM teaching
output can't be asserted on exactly, so each eval_*.py file prints curated
inputs next to the real model output for a bilingual reviewer to read (see
README.md's "Next POC validation"). For deterministic orchestration tests
(mocked, no model calls) see ../test_orchestrator.py.

Requires Ollama running locally with qwen3.5:9b and qwen3.5:4b installed.
"""
import os
import queue
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from orchestrator import OrchestratorAgent  # noqa: E402

CONVERSATION_MODEL = os.environ.get('AGENTEACHER_EVAL_MODEL', 'qwen3.5:9b')


def new_agent(messages, model=CONVERSATION_MODEL, expert=''):
    return OrchestratorAgent(model, expert, messages)


def drain(agent):
    events = []
    while True:
        try:
            events.append(agent.events.get_nowait())
        except queue.Empty:
            break
    return events


def run_method(agent, name):
    """Call one OrchestratorAgent method directly (bypassing the thread
    pool / queue dance in .run()) and collect whatever it emitted."""
    started = time.monotonic()
    try:
        getattr(agent, name)()
    except Exception as error:
        return {'error': f'{type(error).__name__}: {error}'}, time.monotonic() - started
    return drain(agent), time.monotonic() - started


def banner(text):
    print('\n' + '=' * 78)
    print(text)
    print('=' * 78)


def section(title, body):
    body = (body or '').strip()
    print(f'\n--- {title} ---')
    print(body if body else '(empty)')
