# Maintenance Guide

This document explains the automated workflows that maintain this package with minimal manual intervention.

## Automated Workflows

### 1. Automatic Releases to PyPI

Trigger: Push a git tag starting with `v` (e.g., `v1.0.1`)

What happens automatically:
1. Builds the package
2. Runs quality checks
3. Publishes to PyPI
4. Creates a GitHub release with artifacts

How to release:
```bash
# Update version with bump2version
bump2version patch  # or minor, or major

# Push the tag
git push origin --tags
```

The package will be on PyPI within 5-10 minutes.

---

### 2. Automatic Dependency Updates

Trigger: Dependabot runs weekly (Mondays at 9am)

What happens automatically:
1. Dependabot checks for outdated dependencies
2. Creates PRs for updates
3. Tests run automatically on the PR
4. Patch and minor updates are auto-merged if tests pass
5. Major updates require manual review

Configuration: `.github/dependabot.yml`

---

### 3. Automatic Issue Management

Trigger: Daily at midnight

What happens automatically:
1. Issues inactive for 60 days → marked as stale
2. Stale issues with no activity for 7 days → closed
3. PRs inactive for 30 days → marked as stale
4. Stale PRs with no activity for 7 days → closed

Exempt labels: `pinned`, `security`, `bug`, `enhancement`, `work-in-progress`

Configuration: `.github/workflows/stale.yml`

---

### 4. Automatic Issue and PR Labeling

Trigger: When issues or PRs are opened/edited

What happens automatically:
- Bug reports → labeled `bug`
- Feature requests → labeled `enhancement`
- Documentation issues → labeled `documentation`
- New source requests → labeled `new-source`
- PRs labeled based on changed files (tests, docs, fetchers, etc.)

Configuration: `.github/workflows/labeler.yml`, `.github/labeler.yml`

---

### 5. Continuous Integration

Trigger: Every push and pull request

What happens automatically:
1. Tests run on multiple OS (Ubuntu, macOS, Windows)
2. Tests run on multiple Python versions (3.9-3.13)
3. Security scans run (Bandit, pip-audit)
4. Code quality checks run (Black, Ruff, mypy)
5. Coverage reports sent to Codecov

Configuration: `.github/workflows/test.yml`, `.github/workflows/security.yml`

---

## Manual Tasks (Minimal)

### When to Intervene

Monthly (5 minutes):
- Review Dependabot PRs for major version updates
- Check security scan results

Per release (10 minutes):
- Update CHANGELOG.md with new features/fixes
- Review and merge any outstanding PRs
- Bump version and push tag

Quarterly (30 minutes):
- Review open issues and close obsolete ones
- Update documentation if needed
- Consider adding new fetchers if requested

---

## Required Secrets

For full automation to work, configure these GitHub secrets:

### PyPI API Token (Required for releases)
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with upload permissions
3. Add to GitHub: Settings → Secrets → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: Your token (starts with `pypi-`)

### GitHub Token (Automatic)
- `GITHUB_TOKEN` is automatically provided by GitHub Actions
- No manual configuration needed

---

## Quick Reference

### To release a new version:
```bash
# Patch release (1.0.0 → 1.0.1)
bump2version patch && git push origin --tags

# Minor release (1.0.0 → 1.1.0)
bump2version minor && git push origin --tags

# Major release (1.0.0 → 2.0.0)
bump2version major && git push origin --tags
```

### To disable a workflow:
Edit the workflow file in `.github/workflows/` and add:
```yaml
on:
  workflow_dispatch:  # Manual trigger only
```

### To check automation status:
- GitHub Actions: https://github.com/raintree-technology/docpull/actions
- PyPI releases: https://pypi.org/project/docpull/#history
- Dependabot: https://github.com/raintree-technology/docpull/network/updates

---

## Customization

### Adjust Dependabot frequency:
Edit `.github/dependabot.yml`:
```yaml
schedule:
  interval: "weekly"  # or "daily", "monthly"
```

### Adjust stale issue timeouts:
Edit `.github/workflows/stale.yml`:
```yaml
days-before-stale: 60  # Change this
days-before-close: 7    # And this
```

### Disable auto-merge for Dependabot:
Delete or disable `.github/workflows/auto-merge-dependabot.yml`

---

## Monitoring

Things to monitor (optional):
- PyPI download stats: https://pypistats.org/packages/docpull
- GitHub traffic: https://github.com/raintree-technology/docpull/graphs/traffic
- Security advisories: https://github.com/raintree-technology/docpull/security

Set up notifications:
- Watch the repository for releases only
- Enable GitHub mobile app for critical alerts
- Dependabot sends weekly summary emails

---

## Summary

What's automated:
- Releases to PyPI
- Dependency updates (patch/minor)
- Issue and PR labeling
- Stale issue management
- Testing on all platforms
- Security scanning
- Code quality checks

What requires attention:
- Major dependency updates (quarterly)
- Security advisories (rare)
- Community PRs (occasional)

Time investment: ~1-2 hours per month average

---

## Troubleshooting

Release failed:
- Check GitHub Actions logs
- Verify PYPI_API_TOKEN is set correctly
- Ensure version in pyproject.toml matches tag

Dependabot not working:
- Check `.github/dependabot.yml` for syntax errors
- Verify Dependabot is enabled in repo settings

Tests failing:
- Check recent changes for breaking code
- Review test logs in GitHub Actions
- Run tests locally: `make test`

For questions or issues with automation, open an issue with the `ci-cd` label.
