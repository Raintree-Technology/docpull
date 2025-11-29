# Security Policy

docpull follows OWASP Top 10, OpenSSF guidelines, and supply chain security standards.

## Security Features

docpull implements multiple layers of defense-in-depth security to protect users when downloading documentation from the web:

### 1. HTTPS-Only (TLS/SSL)
- **All network requests require HTTPS**
- HTTP URLs are automatically rejected
- Prevents man-in-the-middle attacks
- SSL certificate verification enabled by default

### 2. Path Traversal Protection
- All output paths are validated and resolved
- Files must be written within the specified output directory
- Prevents directory traversal attacks (e.g., `../../etc/passwd`)
- Filenames are sanitized to remove dangerous characters

### 3. Content Size Limits
- **Maximum file size: 50MB** per document
- Prevents memory exhaustion attacks
- Protects against zip bombs and decompression bombs
- Size checked before and during download

### 4. XML External Entity (XXE) Protection
- Uses defusedxml library for safe XML parsing
- Automatically rejects external entities
- Prevents XXE injection attacks
- Protects against billion laughs attack (XML bomb)

### 5. URL Validation
- URLs validated before any network request
- Scheme must be HTTPS
- Domain must be present
- Prevents SSRF (Server-Side Request Forgery) attacks

### 6. Redirect Validation
- Maximum of 5 redirects per request
- All redirect URLs validated for security
- Prevents redirect-based SSRF attacks
- Blocks redirects to private IPs

### 7. Request Timeouts
- All HTTP requests have 30-second connection timeout
- Download time limited to 5 minutes maximum
- Prevents hanging on slow/malicious servers
- Resource exhaustion protection

### 8. Rate Limiting
- Configurable delay between requests (default: 0.5s)
- Prevents hammering target servers
- Respectful scraping behavior
- Async-safe implementation with semaphores

### 9. Concurrent Request Limiting
- **Maximum concurrent requests: 10** (configurable)
- Prevents overwhelming target servers
- Resource exhaustion protection
- Async-safe semaphore implementation
- Independent rate limiting per request

### 10. Playwright Security (JavaScript Rendering)
When using `--js` flag for JavaScript rendering:
- **Headless mode by default** (no GUI vulnerabilities)
- **Resource blocking**: Images, fonts, and media blocked (faster + safer)
- **Timeout controls**: 30-second limit per page render
- **URL validation**: All URLs validated before rendering
- **Context isolation**: Each page in isolated browser context
- **No persistent storage**: Browser state cleared after each run

### 11. Input Sanitization
- Filenames sanitized to alphanumeric, dash, dot, underscore
- Maximum filename length: 200 characters with hash-based collision prevention
- Special characters removed
- Configuration values validated
- Prevents command injection via filenames

### 12. No Code Execution
- No use of `eval()`, `exec()`, or `os.system()`
- No dynamic code generation
- No shell command execution
- Safe file operations only

### 13. Content-Type Validation
- Only accepts HTML, XML, and feed content types
- Rejects unexpected file types (executables, archives, etc.)
- Prevents malicious file download attacks

### 14. Comprehensive Private IP Blocking
- Blocks all localhost addresses (127.0.0.0/8, localhost)
- Blocks RFC1918 private IPs (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Blocks link-local addresses (169.254.0.0/16)
- Blocks IPv6 private ranges (fc00::/7, fe80::/10, ::1)
- Blocks .internal and .local domains
- Prevents SSRF attacks on cloud metadata services (AWS/GCP/Azure)

### 15. Domain Allowlist
- Optional domain allowlist feature
- Restricts fetching to approved domains only
- Zero-trust security model

### 16. Information Disclosure Prevention
- Error messages sanitized
- No stack traces exposed to users
- Minimal logging of sensitive data

## Threat Model

### Protected Against
- Man-in-the-middle attacks (HTTPS-only)
- Path traversal and directory escape
- XML External Entity (XXE) attacks (defusedxml)
- XML bomb and billion laughs attack
- Zip bombs and decompression bombs (size limits)
- Memory exhaustion (file size limits)
- SSRF - External (HTTPS-only, comprehensive IP blocking)
- SSRF - Internal (localhost, RFC1918, link-local, IPv6 private)
- SSRF - Cloud metadata services (169.254.169.254 blocked)
- SSRF via redirects (redirect URL validation)
- Infinite redirects
- Request timeout attacks (connection and download timeouts)
- Slow DoS attacks (5-minute download limit)
- Command injection via filenames
- Code injection (no dynamic execution)
- Symlink attacks (path resolution)
- Content-type spoofing (validation)
- Filename collisions (hash-based uniqueness)
- Configuration injection (input validation)
- Information disclosure (sanitized errors)
- Supply chain attacks (pinned dependencies, scanning)

### Not Protected Against
- Malicious content within documentation (XSS in markdown)
- DNS rebinding attacks
- Compromised upstream documentation sources
- Social engineering

## Best Practices

### For Users
1. Only fetch from trusted sources
2. Run in isolated environments when possible
3. Review downloaded content before use
4. Use specific output directories
5. Monitor resource usage during large fetches

### For Developers
1. Never disable SSL verification
2. Validate all user inputs
3. Keep dependencies updated

## Reporting Security Issues

Report security vulnerabilities to support@raintree.technology.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if applicable)

Do not open public GitHub issues for security vulnerabilities.

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1).

Check the [Releases page](https://github.com/raintree-technology/docpull/releases) for security advisories.

## Supply Chain Security

### Dependency Management
- Exact version pinning in pyproject.toml
- Automated security scanning with pip-audit
- Weekly dependency reviews

### Core Dependencies
- **requests** - HTTP library with SSL/TLS support
- **beautifulsoup4** - HTML parser
- **html2text** - HTML to Markdown converter
- **defusedxml** - Secure XML parsing library
- **aiohttp** - Async HTTP library with SSL/TLS support
- **rich** - Terminal output library (no network access)
- **certifi** - SSL certificates

### Optional Dependencies
- **playwright** - Browser automation (optional, for `--js` flag)
  - Sandboxed browser execution
  - Resource blocking for security
  - Isolated contexts per page

All dependencies are actively maintained and scanned weekly for CVEs.

### Security Scanning
- Bandit - Static security analysis
- pip-audit - Dependency vulnerability scanner

## Compliance

- OWASP Top 10: Protected against injection, XXE, insecure deserialization
- CWE-22: Path Traversal Prevention
- CWE-611: XXE Prevention
- CWE-918: SSRF Prevention
- CWE-400: Resource Exhaustion Prevention
