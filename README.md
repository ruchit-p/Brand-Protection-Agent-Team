Agno Brand Protection & DMCA Agent Suite

Overview

- A conversational agent suite for brand protection workflows built on the Agno agent framework.
- Includes two interactive agents:
  - Brand Protection Agent: crawls/scrapes sites, performs domain intelligence (WHOIS/DNS), analyzes screenshots/logos using Google Gemini, and generates a standardized, zero‑trust evidence report.
  - DMCA Report Agent: produces DMCA takedown notices using structured inputs and saved evidence.
- Provides a handoff flow from brand analysis to DMCA drafting, and saves artifacts (reports, screenshots) to disk.

Features

- Website scraping/crawling via Firecrawl (markdown, HTML, screenshots)
- Domain intelligence (WHOIS, A/MX/TXT DNS)
- Multimodal image analysis and comparison with Google Gemini
- Zero‑trust brand analysis report with numeric score and breakdown
- DMCA notice generation (markdown)
- Session-scoped storage for artifacts
  - Requires GOOGLE_API_KEY (Gemini) and FIRECRAWL_API_KEY (Firecrawl)

Repository structure

```
agnoagent/
  agent_team.py              # Orchestrated multi-agent CLI (recommended entrypoint)
  main.py                    # Standalone Brand Protection Agent CLI
  dmca_agent.py              # Standalone DMCA Agent CLI
  brand_analysis_report.py   # Toolkit for standardized brand analysis report
  dmca_report_tool.py        # Toolkit for DMCA notice generation
  domain_intelligence_tool.py# WHOIS/DNS and typosquatting checks
  firecrawl_tool.py          # Firecrawl integration (scrape/crawl/screenshots)
  image_analyzer.py          # Google Gemini multimodal image analysis helpers
  file_toolkit.py            # File read/write/list helpers
  requirements.txt
```

Prerequisites

- Python 3.10+
- Internet access (for WHOIS/DNS, Firecrawl, Gemini, image downloads)
- Accounts/API keys:
  - Google Generative AI (Gemini)
  - Firecrawl

Quick start

1. Setup environment

```
cd agnoagent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables

Create a .env file (or copy from .env.example):

```
GOOGLE_API_KEY=your_google_generative_ai_key
FIRECRAWL_API_KEY=your_firecrawl_key
# Optional: override storage and tmp directories
STORAGE_DIR=/absolute/path/to/storage
TMP_DIR=/absolute/path/to/tmp
```

3. Storage directory

By default, storage is created under `<project>/storage`. You can override via `STORAGE_DIR`. A configurable `TMP_DIR` is used for SQLite state; defaults to `<project>/tmp`.

How to run

- Recommended (multi-agent with handoff):

```
python agent_team.py
```

- Switch between agents during a session: type "switch to dmca" or "switch to brand".

- Single agents:

```
python main.py        # Brand Protection Agent only
python dmca_agent.py  # DMCA Agent only
```

Usage examples

- Brand analysis:
  - "Analyze brand 'Acme' on https://example.com and generate a full report."
- DMCA drafting:
  - "Create a DMCA takedown notice for brand 'Acme' against https://badsite.tld using the saved report."

Outputs

- Markdown reports (brand analysis, DMCA notices)
- Session folders with screenshots and analysis artifacts

Troubleshooting

- Missing API key errors:
  - image_analyzer.py requires GOOGLE_API_KEY
  - firecrawl_tool.py requires FIRECRAWL_API_KEY
- Firecrawl/Gemini response shape or version drift:
  - requirements pin minimum versions; newer minor versions may change response fields. If you hit attribute/key errors, check the respective SDK docs and adjust.
- Offline usage:
  - WHOIS/DNS, Firecrawl, Gemini, and image downloads require network access.

Security & privacy

- Do not commit secrets. Use .env (already gitignored). See SECURITY.md for reporting vulnerabilities.
- This repository does not transmit user data except to configured third‑party services (Firecrawl, Google Generative AI) when tools are invoked.
- Code of Conduct: see CODE_OF_CONDUCT.md

Limitations

- dmca_report_tool.py uses placeholder registrar/contact data; integrate a real WHOIS/ICANN API for production use.

Roadmap (suggested)

- Make storage directory configurable via STORAGE_DIR env var
- Honor FileTools(base_directory) consistently
- Add real registrar/contact lookups
- Add tests and CI

Contributing

See CONTRIBUTING.md for guidelines.

License

MIT — see LICENSE for details.
