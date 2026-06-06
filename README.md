# BrechaBot

**Open-source AI chatbot red-team scanner.** Point it at a chatbot you own, and BrechaBot fires a
library of prompt-injection / jailbreak attacks, judges the replies with a two-layer engine
(deterministic leak markers + an LLM judge), and produces a graded vulnerability report mapped to
the OWASP LLM Top 10.

> ⚠️ **Authorized use only.** Only scan bots you own or are explicitly authorized to test.

## Install

```bash
pip install brechabot
```

## Quickstart

```bash
brechabot corpus list
brechabot scan \
  --target-url https://your-bot.example/chat \
  --schema openai --target-model gpt-4o-mini \
  --system-prompt-file your_bot_system_prompt.txt \
  --judge-base-url http://localhost:11434/v1 --judge-model llama3.1 \
  --out report.json --html report.html
```

Judge providers (any OpenAI-compatible endpoint): Ollama, Groq, OpenAI, Gemini.

## Attack packs

The corpus is pluggable. The free **starter** pack (10 attacks) ships built-in. Load more with
`--pack` (a builtin name or a path), repeatable and merged:

```bash
brechabot scan --pack starter --pack ./my-pack ...
```

## Free vs. Pro

| | Free (this repo) | Pro / Hosted |
|---|---|---|
| Attacks | 10-attack starter | 49+ curated corpus |
| Categories | sampler | full OWASP LLM Top 10 coverage |
| Multilingual / multi-turn | one example each | full depth |
| Hosted scans, history, CI, dashboards | — | ✅ BrechaBot Cloud |

→ Pro corpus + hosted SaaS: **(link TBD at launch)**.

## Develop

```bash
pip install -e ".[dev]"
pytest -q && ruff check . && mypy -p brechabot
```

Apache-2.0. See `CONTRIBUTING.md` to author your own attack pack.
