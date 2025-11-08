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
- XML parser configured to reject external entities
- Prevents XXE injection attacks
- Protects against billion laughs attack (XML bomb)

### 5. URL Validation
- URLs validated before any network request
- Scheme must be HTTPS
- Domain must be present
- Prevents SSRF (Server-Side Request Forgery) attacks

### 6. Redirect Limits
- Maximum of 5 redirects per request
- Prevents infinite redirect loops
- Protects against redirect-based attacks

### 7. Request Timeouts
- All HTTP requests have 30-second timeout
- Prevents hanging on slow/malicious servers
- Resource exhaustion protection

### 8. Rate Limiting
- Configurable delay between requests (default: 0.5s)
- Prevents hammering target servers
- Respectful scraping behavior

### 9. Input Sanitization
- Filenames sanitized to alphanumeric, dash, dot, underscore
- Maximum filename length: 200 characters
- Special characters removed
- Prevents command injection via filenames

### 10. No Code Execution
- No use of `eval()`, `exec()`, or `os.system()`
- No dynamic code generation
- No shell command execution
- Safe file operations only

### 11. Content-Type Validation
- Only accepts HTML, XML, and feed content types
- Rejects unexpected file types (executables, archives, etc.)
- Prevents malicious file download attacks

### 12. Private IP Blocking
- Blocks localhost (127.0.0.1, localhost)
- Blocks RFC1918 private IPs (10.x, 172.16.x, 192.168.x)
- Prevents SSRF attacks on internal networks

### 13. Domain Allowlist
- Optional domain allowlist feature
- Restricts fetching to approved domains only
- Zero-trust security model

### 14. Information Disclosure Prevention
- Error messages sanitized
- No stack traces exposed to users
- Minimal logging of sensitive data

## Threat Model

### Protected Against
- Man-in-the-middle attacks (HTTPS-only)
- Path traversal and directory escape
- XML External Entity (XXE) attacks
- XML bomb and billion laughs attack
- Zip bombs and decompression bombs (size limits)
- Memory exhaustion (file size limits)
- SSRF - External (HTTPS-only, private IP blocking)
- SSRF - Internal (localhost, RFC1918 blocking)
- Infinite redirects
- Request timeout attacks
- Command injection via filenames
- Code injection (no dynamic execution)
- Symlink attacks (path resolution)
- Content-type spoofing (validation)
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
- Exact version pinning in requirements.txt
- Automated security scanning with pip-audit
- Dependabot enabled for automated updates
- Weekly dependency reviews

### Core Dependencies
- requests - HTTP library with SSL/TLS support
- beautifulsoup4 - HTML parser
- html2text - HTML to Markdown converter
- certifi - SSL certificates

All dependencies are actively maintained and scanned weekly for CVEs.

### Security Scanning
- Bandit - Static security analysis
- pip-audit - Dependency vulnerability scanner
- CodeQL - Semantic code analysis
- Dependency Review - PR-based scanning

## Compliance

- OWASP Top 10: Protected against injection, XXE, insecure deserialization
- CWE-22: Path Traversal Prevention
- CWE-611: XXE Prevention
- CWE-918: SSRF Prevention
- CWE-400: Resource Exhaustion Prevention
