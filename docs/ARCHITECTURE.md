Architecture

High-level

- Two interactive agents built on the Agno framework:
  - Brand Protection Agent (scrape + analyze + report)
  - DMCA Report Agent (notice drafting)
- Handoff tools coordinate evidence and context between agents.
- Storage: session-scoped directories for artifacts (reports, screenshots, analysis).

Core modules

- agent_team.py

  - EnhancedBrandProtectionAgent: wraps tools (DuckDuckGo, domain intelligence, Firecrawl, image analysis, file ops, handoff, report generator). Creates session directories.
  - EnhancedDmcaReportAgent: DMCA-focused agent with file ops and DMCA tools; can read handoff context.
  - HandoffTools: persists context + user guidance to switch agents.
  - CLI orchestration and switching loop.

- main.py

  - Standalone brand agent (simpler) for single-agent usage.

- dmca_agent.py

  - Standalone DMCA agent CLI.

- brand_analysis_report.py

  - BrandAnalysisReportGenerator: generates standardized markdown reports and computes a conservative evidence score. Exposed as a toolkit for the agent.

- domain_intelligence_tool.py

  - WHOIS lookup, DNS A/MX/TXT record retrieval, simple typosquatting variant checks.

- firecrawl_tool.py

  - Firecrawl wrappers: scrape_website, scrape_with_brand_detection, crawl_website.
  - Captures screenshots, stores metadata per session, and optionally auto-runs image analysis.

- image_analyzer.py

  - Google Gemini multimodal analysis: analyze_brand_image, compare_brand_images, detect_logo_usage, analyze_product_similarity.

- dmca_report_tool.py

  - Generates DMCA takedown notices (markdown), provides placeholder domain/DMCA contact info, saves reports.

- file_toolkit.py
  - File read/write/list helpers. Honors `base_directory` and defaults to env `STORAGE_DIR`.

Data flow (typical)

1. User asks to analyze a brand vs suspected site in Brand agent.
2. Firecrawl scrapes the site; screenshots and text/HTML captured.
3. ImageAnalyzer (Gemini) analyzes screenshots; optional comparison between original and suspected assets.
4. Domain tool fetches WHOIS and DNS basics.
5. Report generator compiles a zero‑trust report + score; saved to storage.
6. If warranted, HandoffTools saves context and instructs user to switch to DMCA agent.
7. DMCA agent uses saved report to generate a DMCA notice.

Configuration

- Environment variables:
  - GOOGLE_API_KEY — required for image analysis
  - FIRECRAWL_API_KEY — required for scraping/crawling
- Storage path is configurable via env `STORAGE_DIR`; `TMP_DIR` controls SQLite state.

Known limitations

- Hardcoded absolute storage path; needs env-based configuration.
- Placeholder registrar/contact data in DMCA tool.
- No automated tests yet.
