# BrechaBot

**Open-source AI chatbot red-team scanner.** Point it at a chatbot you own, and BrechaBot fires a
library of prompt-injection / jailbreak attacks, judges the replies with a two-layer engine
(deterministic leak markers + an LLM judge), and produces a graded vulnerability report mapped to
the OWASP LLM Top 10.

> ⚠️ **Authorized use only.** Only scan bots you own or are explicitly authorized to test.

## Install

```bash
npm install -g brechabot
# or run without installing:
npx brechabot --help
```

Requires Node ≥ 20. No Python needed.

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

The corpus is pluggable. The **starter** pack (10 attacks) ships built-in. Load more with
`--pack` (a builtin name or a path), repeatable and merged:

```bash
brechabot scan --pack starter --pack ./my-pack ...
```

## Use as a library

```ts
import { loadCorpus, runScan, summarize, htmlReport } from "brechabot";
```

## Develop

```bash
npm install
npm run typecheck && npm run lint && npm test && npm run build
```

Apache-2.0. See `CONTRIBUTING.md` to author your own attack pack.
