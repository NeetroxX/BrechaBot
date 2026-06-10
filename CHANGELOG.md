# Changelog

## 0.1.2

- Black-box by default: `--system-prompt-file` is now optional. When omitted, BrechaBot
  sends **no** system message to the target (so a deployed bot keeps its own server-side
  prompt) and the LLM judge uses a dedicated black-box rubric that scores from the observed
  exchange alone — leak/secret disclosure, instruction-following, persona breaks, etc. Provide
  `--system-prompt-file` only for a white-box test where you know the target's prompt.

## 0.1.1

- Fix the global `brechabot` command producing no output when installed via
  `npm i -g` / `npx`. The bin now has a dedicated always-run entry (`dist/bin.js`)
  instead of relying on an `import.meta.url` entry guard that didn't match npm's
  shim path. Also drop the leading `./` from the `bin` path so npm keeps it on publish.

## 0.1.0

- Re-implemented the engine + CLI in **TypeScript**, published to npm
  (`npm i -g brechabot`, `npx brechabot`). Zero Python runtime for users.
- Pack-pluggable corpus, 10-attack **starter** pack, two-layer judge (deterministic leak
  markers + LLM judge), async multi-turn orchestrator, HTML/JSON reports, and a
  commander-based CLI (`brechabot scan` / `corpus` / `version`).
- **Note:** the `brc-` corpus version hash is computed with Node `crypto`; it is an internal
  version string only and is not a compatibility contract.
