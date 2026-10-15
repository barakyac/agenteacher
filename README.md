# agenteacher

A local, editable English-teacher POC for adult Hebrew speakers with basic English.

## Run

Requires Python 3.10+; no Python or JavaScript packages to install.

```sh
cd agenteacher
python3 server.py
```

Open http://127.0.0.1:8765. Stop with Ctrl+C. Override the port with `PORT=8766 python3 server.py` if needed.

## Two modes

**Guided practice:** six authored lessons compare Hebrew and English, then send the learner's answer and current exercise context to the selected local model. The model supplies specific Hebrew feedback and a structured correct/retry/clarify verdict. Correct answers advance to transfer practice; errors and questions retain the current exercise. There is no fixed-answer matching. Reading lessons works without a model; personalized assessment requires Ollama. Model judgments can still be wrong and need teacher review.

**Local AI conversation:** talks to Ollama at `http://127.0.0.1:11434/api/chat`. Install Ollama from https://ollama.com, download a chat model with Hebrew support using `ollama pull MODEL_NAME`, and start Ollama. Select “שיחה עם AI מקומי”, refresh, and choose your downloaded model. Model choice depends on available memory and Hebrew quality; this project does not download weights. See the official API documentation at https://docs.ollama.com/api/chat.

Local qwen3.5:9b is installed. Guided feedback was smoke-tested on an omitted be verb and a valid contraction; this is not a broad evaluation of teaching quality. Installation/model download requires internet; a downloaded local model can subsequently run offline. The app sends chat only to the loopback Ollama service and has no analytics or external assets.

## Teaching approach

Explain in Hebrew; practise in English. Contrast structures rather than translating word by word. Correct one central issue, preserve the learner's meaning, give an example, then ask one new question and wait. Avoid assuming all errors come from Hebrew. Accept grammatical alternatives in AI mode. Text only: no microphone, speech recognition, or pronunciation scoring.

Topics: present-tense be; attributive adjective order; do/does questions; habits vs ongoing actions; indefinite articles; present-simple negation.

## Source map

- `server.py`: standard-library HTTP server, local model discovery and chat proxy; bound to loopback only.
- `teacher-prompt.md`: editable bilingual teaching instructions.
- `dist/app.js`: lesson content, practice checks, progress, chat interaction.
- `dist/style.css`: responsive RTL interface.
- `dist/index.html`: accessible application markup.

Progress is stored in browser localStorage (`agenteacher-progress`). Conversation is kept in page memory only and resets when switching topics/modes or reloading. AI requests include the selected topic and at most the latest 28 conversation messages; this is not durable learner memory. No accounts or database. Python's development HTTP server is not intended for public deployment.

## Verification

```sh
python3 -m py_compile server.py
node --check dist/app.js
```

Browser checks: complete the first lesson with `She is busy.` and `They are happy.`; confirm progress survives reload; check unmatched input and hints; select AI mode without Ollama and verify setup guidance. A real inference smoke test remains required once a suitable model is available.

## Next POC validation

Have a bilingual teacher review the lessons and model responses. Try with adult learners: check whether they can explain the structural difference and apply it to an unseen sentence. For a subsequent iteration, add persistent error categories and spaced review; do not infer mastery from a single correct answer.

Source is provided under the MIT license. Model weights have their own licenses.

## General expert chat

The third tab, צ׳אט כללי, supports a general conversation partner, technology specialist, job interviewer, travel guide, history specialist, or a custom topic (up to 200 characters). Choose a role and press התחלת שיחה בתפקיד; this clears the conversation so roles do not mix. Switching modes also starts a fresh conversation. The model answers the topic and adds a brief Hebrew hint for one English mistake when applicable, preserving the hint-first teaching preference. Explicit requests can reveal a correction. Hebrew messages receive ordinary Hebrew answers. These are AI role simulations, not verified professional credentials. Instructions live in `general-prompt.md`; general requests do not include the English lesson or exercise grading instructions.

## Parallel agents in general chat

`orchestrator.py` implements three roles: a deterministic OrchestratorAgent dispatches a conversation agent (selected model, normally 9b) and a grammar coach (4b by default). There is no third LLM planning call; orchestration owns concurrent dispatch, validated coach output, independent errors, cancellation of event delivery, and a 100-second overall deadline. Worker HTTP reads time out after 90 seconds. Disconnects stop delivery but may not immediately cancel an inference already running inside Ollama.

The server streams newline-delimited JSON. The conversation card updates token by token; the independent coach card shows its hint as soon as ready. A failed grammar check never appears as a passed check. Conversation history includes successful hints for follow-up questions. Model roles have separate prompts in `conversation-prompt.md` and `coach-prompt.md`. Set `AGENTEACHER_COACH_MODEL` before starting the server to override the coach model. Install that model before use; failures remain visible rather than silently skipping review.

Concurrent HTTP requests do not guarantee concurrent GPU execution: Ollama scheduling and memory affect speed. One local run of `i want many money` with 9b + 4b returned the coach hint in 6.6s, first conversation text in 11.6s, and completed in 13.0s. This is a smoke measurement, not a latency guarantee or controlled comparison. Grammar judgments remain model-generated and can be wrong. Verify with `python3 -m unittest test_orchestrator.py` (parallel dispatch and independent failure handling).

## Spelling and permitted languages

A fourth role, the spelling/language agent (`spelling-prompt.md`, local 4b), checks spelling independently of grammar. General chat runs all three model workers concurrently, but the orchestrator buffers conversation/grammar output until the spelling agent accepts the language. Rejected messages are not committed to chat history. The model calls may already have started locally; rejection suppresses their output. Teacher modes perform the same semantic language check before generating a reply.

`language_guard.py` immediately rejects letters outside English ASCII and Hebrew, including mixed-script messages; Hebrew vowel marks, numbers, punctuation and emoji are supported. This intentionally strict alphabet restriction also excludes accented Latin letters. ASCII French/Spanish/etc. are checked by the local model, so semantic enforcement is best-effort; ambiguous short words, names and misspelled English should remain usable. Language-check errors do not count as a pass. An extra model request can increase latency; no new speed claim has been measured.

## Local latency check

The browser now initially selects the installed 4b model when available; manual model selection remains available. In a small teacher-mode check, `she busy` took 27.8s on 9b and 15.6s on 4b; `i asm Barak` took 7.4s on 4b. These were individual runs, not controlled benchmarks. The smaller model's grammar response still leaked a correction and used English despite Hebrew instructions, so teaching quality and hint-only compliance remain limitations. A combined single-call experiment performed worse and was reverted; teaching still checks spelling before generating its reply.
