# docpull

**Pull documentation from any website and converts it into clean, AI-ready Markdown.**
Fast, type-safe, secure, and optimized for building knowledge bases or training datasets.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/docpull.svg)](https://badge.fury.io/py/docpull)
[![License: MIT](https://img.shields.io/github/license/raintree-technology/docpull)](https://github.com/raintree-technology/docpull/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

## Why docpull?

Unlike tools like wget or httrack, docpull extracts only the main content, removing ads, navbars, and clutter. Output is clean Markdown with optional YAML frontmatter—ideal for RAG systems, offline docs, or ML pipelines.

## Key Features

- Works on any documentation site
- Smart extraction of main content
- Async + parallel fetching (up to 10× faster)
- Optional JavaScript rendering via Playwright
- Sitemap + link crawling
- URL-based filtering (include/exclude)
- Rate limiting, timeouts, content-type checks
- Saves docs in structured Markdown with YAML metadata
- Optimized profiles for popular platforms (Stripe, Next.js, React, Plaid, Tailwind, etc.)

## Quick Start

```bash
pip install docpull
docpull --doctor         # verify installation
docpull https://aptos.dev
docpull stripe           # use a built-in profile
docpull https://site.com/docs --max-pages 100 --max-concurrent 20
```

### JavaScript-heavy sites

```bash
pip install docpull[js]
python -m playwright install chromium
docpull https://site.com --js
```

## Python API

```python
from docpull import GenericAsyncFetcher

fetcher = GenericAsyncFetcher(
    url_or_profile="https://aptos.dev",
    output_dir="./docs",
    max_pages=100,
    max_concurrent=20,
)
fetcher.fetch()
```

## Common Options

- `--doctor` – verify installation and dependencies
- `--max-pages N` – limit crawl size
- `--max-depth N` – restrict link depth
- `--max-concurrent N` – control parallel fetches
- `--js` – enable Playwright rendering
- `--output-dir DIR`
- `--rate-limit X`
- `--no-skip-existing`
- `--dry-run`

## Performance

Async fetching drastically reduces runtime:

| Pages | Sync | Async | Speedup |
|-------|------|-------|---------|
| 50 | ~50s | ~6s | 8× faster |

Higher concurrency yields even better results.

## Output Format

Each downloaded page becomes a Markdown file:

```markdown
---
url: https://stripe.com/docs/payments
fetched: 2025-11-13
---
# Payment Intents
...
```

Directory layout mirrors the target site's structure.

## Configuration File (Optional)

```yaml
output_dir: ./docs
rate_limit: 0.5
sources:
  - stripe
  - nextjs
```

Run with:
```bash
docpull --config config.yaml
```

## Custom Profiles

Easily define profiles for frequently scraped sites.

```python
from docpull.profiles.base import SiteProfile

MY_PROFILE = SiteProfile(
    name="mysite",
    domains={"docs.mysite.com"},
    include_patterns=["/docs/", "/api/"],
)
```

## Security

- HTTPS-only
- Blocks private network IPs
- 50MB page size limit
- Timeout controls
- Validates content-type
- Playwright sandboxing

## Troubleshooting

- **Installation issues**: Run `docpull --doctor` to diagnose problems
- **Missing dependencies**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common fixes
- **Site requires JS**: install Playwright + `--js`
- **Slow or rate limited**: lower concurrency or raise `--rate-limit`
- **Large sites**: set `--max-pages`

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Links

- [PyPI](https://pypi.org/project/docpull/)
- [GitHub](https://github.com/raintree-technology/docpull)
- [Issues](https://github.com/raintree-technology/docpull/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details
