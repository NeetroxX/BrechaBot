# Publishing BrechaBot

These steps require your own GitHub + PyPI credentials.

## 1. Verify the names are free
- **PyPI:** open <https://pypi.org/project/brechabot/> — it must 404 (available). Fallback: `brechabot-engine`.
- **GitHub:** pick the owner/org and repo name `brechabot`. The `[project.urls]` in `pyproject.toml`
  currently point at `https://github.com/bravokk29/brechabot` — update `bravokk29` if that's not your handle.

## 2. Push to GitHub
```bash
git branch -M main
git remote add origin https://github.com/<you>/brechabot.git
git push -u origin main
```

## 3. Publish to PyPI
```bash
pip install build twine
python -m build
twine upload dist/*          # prompts for a PyPI API token
```

## 4. Tag a release (optional)
```bash
git tag v0.1.0 && git push --tags
# then create a GitHub Release from the tag
```

After step 2, GitHub Actions (`.github/workflows/ci.yml`) runs tests + ruff + mypy on every push/PR.
