## 0.1.0 — TypeScript rewrite

- Re-implemented the engine + CLI in TypeScript; published to npm (`npm i -g brechabot`, `npx brechabot`). Zero Python runtime for users.
- Behavior parity with the Python engine. **Note:** the `brc-` corpus version hash is recomputed with Node `crypto` and differs from prior Python values (internal version string only).

# Changelog

## 0.1.0

- Initial public release: pack-pluggable corpus, 10-attack starter pack, two-layer judge
  (deterministic leak markers + LLM judge), async multi-turn orchestrator, HTML/JSON reports,
  and a Typer CLI (`brechabot scan` / `corpus` / `version`).
