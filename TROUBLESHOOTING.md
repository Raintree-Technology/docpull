# Troubleshooting Guide

This guide covers common issues you might encounter when installing or using docpull.

## Table of Contents

- [Installation Issues](#installation-issues)
  - [Missing Dependencies](#missing-dependencies)
  - [pipx Installation Problems](#pipx-installation-problems)
  - [Development Installation](#development-installation)
- [Runtime Issues](#runtime-issues)
  - [YAML Configuration Errors](#yaml-configuration-errors)
  - [JavaScript Rendering Not Working](#javascript-rendering-not-working)
  - [Network/Connection Issues](#networkconnection-issues)
- [Diagnostic Tools](#diagnostic-tools)

---

## Installation Issues

### Missing Dependencies

**Symptom:**
```
ERROR: Missing required dependency: defusedxml
ModuleNotFoundError: No module named 'defusedxml'
```

**Cause:**
This usually happens when:
1. Installation was interrupted or incomplete
2. pipx cache is stale (common with pipx)
3. Dependencies weren't properly declared or installed

**Solutions:**

#### For pipx Users (Recommended)
```bash
# Force reinstall to clear cache
pipx reinstall docpull --force

# Or uninstall and reinstall
pipx uninstall docpull
pipx install docpull
```

#### For pip Users
```bash
# Force reinstall all dependencies
pip install --upgrade --force-reinstall docpull

# Or with dependencies explicitly
pip install --upgrade --force-reinstall docpull[all]
```

#### Verify Installation
```bash
# Check if all dependencies are working
docpull --doctor
```

---

### pipx Installation Problems

**Symptom:**
Tool installs successfully but crashes with import errors when run.

**Cause:**
pipx creates isolated environments and sometimes caches old package metadata.

**Solution:**
```bash
# Clear pipx cache and reinstall
pipx uninstall docpull
pipx install docpull --force

# If problems persist, try reinstalling pipx itself
python3 -m pip install --user --upgrade pipx
pipx ensurepath
```

---

### Development Installation

**For Contributors:**

```bash
# Clone the repository
git clone https://github.com/yourusername/docpull
cd docpull

# Install in editable mode with all dependencies
pip install -e ".[dev]"

# Or use the requirements file
pip install -r requirements.txt

# Verify installation
docpull --doctor
python -m pytest  # Run tests
```

---

## Runtime Issues

### YAML Configuration Errors

**Symptom:**
```
ERROR: PyYAML is required for YAML config files
ImportError: PyYAML is required for YAML config
```

**Cause:**
PyYAML is an optional dependency and not installed by default.

**Solutions:**

#### Install YAML Support
```bash
# For pipx
pipx install docpull[yaml]
# or
pipx reinstall docpull --force --pip-args="[yaml]"

# For pip
pip install docpull[yaml]
# or
pip install pyyaml>=6.0
```

#### Use JSON Instead
```bash
# Generate JSON config instead
docpull --generate-config config.json

# Use JSON config file
docpull --config config.json
```

---

### JavaScript Rendering Not Working

**Symptom:**
```
[WARN] Playwright not installed. Install with: pip install docpull[js]
Falling back to non-JS mode
```

**Cause:**
Playwright is an optional dependency for JavaScript-heavy sites.

**Solution:**

```bash
# Install JavaScript rendering support
pip install docpull[js]

# Install Playwright browsers (required after first install)
playwright install

# Or install specific browser only
playwright install chromium
```

**Note:** Playwright is large (~300MB) and slower, only use if needed for JS-heavy documentation sites.

---

### Network/Connection Issues

**Symptom:**
- Timeouts
- Connection refused
- DNS resolution errors

**Diagnosis:**
```bash
# Check network connectivity
docpull --doctor

# Test specific URL manually
curl https://docs.example.com
```

**Solutions:**

1. **Check your internet connection**
2. **Check if site is accessible:**
   ```bash
   # Test if URL is reachable
   curl -I https://docs.example.com
   ```

3. **Check firewall/proxy settings:**
   ```bash
   # If behind proxy, set environment variables
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   ```

4. **Try with rate limiting:**
   ```bash
   # Slow down requests if being rate-limited
   docpull https://example.com --rate-limit 2.0
   ```

---

## Diagnostic Tools

### Using --doctor

The `--doctor` command runs comprehensive checks:

```bash
# Basic diagnostic
docpull --doctor

# Check specific output directory
docpull --doctor --output-dir /custom/path
```

**What it checks:**
- [OK] Core dependencies (requests, beautifulsoup4, etc.)
- [WARN] Optional dependencies (PyYAML, Playwright)
- [OK] Network connectivity
- [OK] Output directory write permissions

**Example output:**
```
Running docpull diagnostics...

Core Dependencies:
  [OK] requests
  [OK] beautifulsoup4
  [OK] html2text
  [OK] defusedxml
  [OK] aiohttp
  [OK] rich

Optional Dependencies:
  [WARN] pyyaml (optional - not installed)
  [OK] playwright

System:
  [OK] Network connectivity
  [OK] Output directory writable (./docs)

All core dependencies installed correctly!

Optional features available:
  - YAML config support: pip install docpull[yaml]
  - JavaScript rendering: pip install docpull[js]
  - All optional features: pip install docpull[all]
```

---

### Checking Logs

Enable verbose logging to debug issues:

```bash
# Verbose output
docpull https://example.com --verbose

# Or specific log level
docpull https://example.com --log-level DEBUG

# Save logs to file
docpull https://example.com --log-file debug.log
```

---

### Common Error Messages

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `ModuleNotFoundError: No module named 'X'` | Missing dependency | Run `docpull --doctor`, then `pipx reinstall docpull --force` |
| `ImportError: PyYAML is required` | YAML support not installed | Install with `pip install docpull[yaml]` or use JSON config |
| `Playwright not installed` | JS rendering not available | Install with `pip install docpull[js]` (optional, only if needed) |
| `Permission denied` writing to directory | No write access to output dir | Check permissions or use `--output-dir` with writable path |
| `Connection timeout` | Network/firewall issue | Check network, try `--rate-limit` to slow requests |
| `404 Not Found` | Invalid URL or page moved | Verify URL in browser first |

---

## Still Having Issues?

If you're still experiencing problems:

1. **Run diagnostics:**
   ```bash
   docpull --doctor
   ```

2. **Check version:**
   ```bash
   docpull --version
   ```

3. **Try with verbose logging:**
   ```bash
   docpull https://example.com --verbose --log-file debug.log
   ```

4. **Report the issue:**
   - Include the output from `--doctor`
   - Include relevant logs from `--verbose`
   - Describe what you were trying to do
   - Include your OS and Python version

---

## Getting Help

- **Documentation:** Check README.md for usage examples
- **Report bugs:** Open an issue on GitHub
- **Feature requests:** Open an issue with the "enhancement" label

---

## Quick Reference

```bash
# Installation
pipx install docpull                    # Basic install
pipx install docpull[all]              # With all optional features

# Verification
docpull --doctor                        # Check installation
docpull --version                       # Check version

# Basic usage
docpull https://docs.example.com        # Fetch docs
docpull stripe                          # Use profile
docpull --help                          # Show help

# Debugging
docpull https://example.com --verbose   # Verbose output
docpull https://example.com --dry-run   # Show what would be fetched
```
