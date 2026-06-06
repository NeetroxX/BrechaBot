# Changelog

## 0.1.0

- Re-implemented the engine + CLI in **TypeScript**, published to npm
  (`npm i -g brechabot`, `npx brechabot`). Zero Python runtime for users.
- Pack-pluggable corpus, 10-attack **starter** pack, two-layer judge (deterministic leak
  markers + LLM judge), async multi-turn orchestrator, HTML/JSON reports, and a
  commander-based CLI (`brechabot scan` / `corpus` / `version`).
- **Note:** the `brc-` corpus version hash is computed with Node `crypto`; it is an internal
  version string only and is not a compatibility contract.
