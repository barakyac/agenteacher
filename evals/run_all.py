"""Run every per-agent eval report in sequence.

python3 evals/eval_teacher.py needs the dev server running
(python3 server.py); the others call OrchestratorAgent directly and only
need Ollama running. All of them are slow (real model calls) -- expect a
few minutes total.

Run: python3 evals/run_all.py
"""
import eval_coach
import eval_conversation
import eval_spelling
import eval_teacher

if __name__ == '__main__':
    eval_spelling.main()
    eval_coach.main()
    eval_conversation.main()
    eval_teacher.main()
