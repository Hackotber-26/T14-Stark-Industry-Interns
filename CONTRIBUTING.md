# Contributing to FixCheck

Start with the [README](README.md) for setup and the [starter issues](docs/ISSUES.md) for scoped contributions. Choose one issue and describe the proposed behavior before making a large change.

## Development

Use Python 3.12 and a recent Node.js release. Activate your Python environment and run commands from the repository root:

```bash
source .venv/bin/activate
pytest backend -q
node --test frontend/tests/api.test.mjs
(cd frontend && npm run build)
```

For the prepared development environment, replace the activation command with `source ~/hack/.venv/bin/activate`. When the backend is already running on port 8000, also run `bash scripts/smoke.sh`; it starts no servers and checks all five expected demo verdicts.

## Change guidelines

- Keep changes small, readable, and focused on one behavior. Add regression tests for bugs and tests for meaningful new behavior.
- Keep thresholds in `backend/pipeline/config.py`, and preserve public request and response shapes when possible.
- Keep processing local. Optional box suggestions must not be required when a user supplies a marked box.
- Use synthetic fixtures without personal information in tests. Do not commit private uploads, local databases, generated run images, model weights, credentials, or dependency folders.
- Label simulated repairs clearly. Report measured failures and uncertainty; never hard-code a verdict for a demo case.
- If scoring or generation changes, rerun `python scripts/eval.py`, inspect the contact sheet after regenerating demos, and explain changes to the measured results.
- Preserve photo attribution and the separate CC BY-SA 2.0 image license when reusing or modifying the supplied photos.

## Pull requests

Explain the problem, the resulting behavior, and how you checked it. Include test commands and their results, screenshots for visible changes, and any change in evaluation accuracy or demo verdicts. Use meaningful commit messages such as `fix(api): preserve phone photo orientation`.

Contributions are distributed under the repository's AGPL-3.0 software license. See [LICENSE](LICENSE).
