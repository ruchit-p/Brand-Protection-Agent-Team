Security Policy

Reporting a Vulnerability

- Please report suspected security vulnerabilities privately.
- Email: security@example.com (replace with a monitored address before publishing)
- Include a description, steps to reproduce, affected versions/commits, and any proof of concept.
- We aim to acknowledge within 72 hours and provide a remediation timeline once triaged.

Supported Versions

- This project is pre-1.0; security fixes will generally target main.

Secrets & Sensitive Data

- Do not commit secrets. Use `.env` (already gitignored) and `.env.example` for documentation.
- Required env vars: `GOOGLE_API_KEY`, `FIRECRAWL_API_KEY`.

Third‑party Services

- Firecrawl and Google Generative AI process data externally. Review their policies before use.

Hardcoded Paths (Known Issue)

- Some modules contain hardcoded paths to a local storage directory. This is not security-sensitive, but is noted for portability. See README roadmap for remediation.
