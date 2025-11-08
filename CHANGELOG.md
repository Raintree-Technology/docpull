# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-07

### Added
- Initial release of docpull
- Support for fetching documentation from multiple sources:
  - Stripe API documentation
  - Plaid API documentation
  - Next.js documentation
  - D3.js documentation (devdocs.io)
  - Bun runtime documentation
  - Tailwind CSS documentation
  - React documentation
- CLI interface with config file support (YAML/JSON)
- Parallel fetching with ThreadPoolExecutor for improved performance
- Security features:
  - Path traversal protection
  - XXE (XML External Entity) protection
  - File size limits (50MB default)
  - Redirect limits (5 hops)
  - Request timeouts (30s)
  - HTTPS enforcement with certificate verification
- Rate limiting to respect server resources
- Structured logging with configurable levels
- YAML frontmatter metadata in generated markdown files
- Config file generation command
- Extensible fetcher architecture for easy addition of new sources
- Comprehensive documentation and examples

### Changed
- Cleaned up README to remove emojis and update to organization URLs
- Applied 2025 PyPI best practices to packaging configuration
- Reorganized project structure for better maintainability

### Security
- Implemented multiple security layers for safe web scraping
- Added security scanning with Bandit and pip-audit
- Created GitHub Actions workflow for automated security checks
- Documented security features in SECURITY.md

---

[1.0.0]: https://github.com/raintree-technology/docpull/releases/tag/v1.0.0
