# Contributing to BrechaBot

## Dev setup

```bash
python -m venv .venv
. .venv/Scripts/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q && ruff check . && mypy -p brechabot
```

## Authoring an attack pack

A pack is a directory with three files:

```
my-pack/
  pack.json        {"id": "my-pack", "name": "My Pack", "version": "1.0.0", "description": "..."}
  attacks.json     [ { "id": "...", "category": "...", "name": "...",
                       "severity": "high|medium|low",
                       "prompt": "..."  |  "turns": ["...", "..."],
                       "markers": ["regex", ...], "lang": "en" }, ... ]
  categories.json  { "<category>": { "owasp": "LLM01: ...", "remediation": "..." } }
```

- Single-turn attacks use `prompt`; multi-turn use `turns` (sent as a real sequential conversation).
- `markers` are case-insensitive regexes; a match flags a likely leak (the LLM judge handles the rest).
- Run it: `brechabot scan --pack ./my-pack ...` (repeat `--pack` to merge packs).

PRs that add high-quality, original attacks to the starter pack are welcome — keep the starter
broad and representative across categories.
