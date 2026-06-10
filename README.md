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

Black-box by default — just point it at your bot's endpoint, no system prompt required:

```bash
brechabot corpus list
brechabot scan \
  --target-url https://your-bot.example/chat \
  --schema openai --target-model your-model \
  --judge-base-url http://localhost:11434/v1 --judge-model llama3.1 \
  --out report.json --html report.html
```

Judge providers (any OpenAI-compatible endpoint): Ollama, Groq, OpenAI, Gemini.

### Black-box vs. white-box

By default BrechaBot sends **no** system message to your target — your bot keeps its own
server-side prompt, and the judge scores from the observed exchange alone. If you *do* know the
target's system prompt and want sharper, prompt-aware verdicts, add `--system-prompt-file
your_prompt.txt` for a white-box scan.

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
