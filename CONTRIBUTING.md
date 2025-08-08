Contributing to Agno Brand Protection & DMCA Agent Suite

Thank you for your interest in contributing! This project welcomes issues and pull requests.

How to contribute

1. Fork and branch

- Fork the repo and create a feature branch: feature/short-description or fix/short-description.

2. Set up your environment

- Python 3.10+
- Create a virtualenv and install dependencies:
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
- Create a `.env` from `.env.example` and fill keys (GOOGLE_API_KEY, FIRECRAWL_API_KEY, optional STORAGE_DIR, TMP_DIR).

3. Coding standards

- Prefer explicit, readable code; avoid micro-optimizations.
- Keep business rules documented in docstrings or module headers.
- Avoid hardcoded absolute paths; prefer configuration or environment variables.
- Do not commit secrets or credentials.

4. Tests

- Add minimal unit tests for critical logic (e.g., report generation, scoring functions).
- Prefer deterministic tests; network-dependent tests should be skipped by default.

5. Commits & PRs

- Keep commits small and focused; reference issues when applicable.
- Suggested prefixes: feat:, fix:, refactor:, docs:, chore:.
- Describe what and why, not just how.

Security

- Never include secrets in code or logs.
- If you discover a vulnerability, follow SECURITY.md.

Code of Conduct

- Be respectful and constructive. Assume good intent. Collaborate openly.
