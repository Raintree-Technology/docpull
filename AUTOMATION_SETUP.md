# Automation Setup Guide

Follow these one-time setup steps to enable full automation.

## One-Time Setup

### 1. Enable GitHub Actions

GitHub Actions should be enabled by default, but verify:
1. Go to your repo → Settings → Actions → General
2. Ensure "Allow all actions and reusable workflows" is selected
3. Ensure "Read and write permissions" is enabled for GITHUB_TOKEN
4. Click "Save"

### 2. Create PyPI API Token

For automatic releases to PyPI:

1. Go to https://pypi.org/account/register/ (if needed)
2. Verify your email
3. Go to https://pypi.org/manage/account/token/
4. Click "Add API token"
   - Token name: `docpull-github-actions`
   - Scope: "Project: docpull" (after first manual upload)
5. Copy the token (starts with `pypi-`)
6. Save this token - you can only see it once

### 3. Add Token to GitHub

1. Go to your repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste your PyPI token
5. Click "Add secret"

### 4. First Release (Manual)

The first release must be manual to register the package on PyPI:

```bash
# Build the package
python -m build

# Upload to PyPI manually (first time only)
twine upload dist/*
# Enter your PyPI username and password when prompted
```

After this first upload, all future releases are automatic!

### 5. Enable Dependabot

Dependabot should be enabled by default, but verify:
1. Go to your repo → Settings → Security → Code security and analysis
2. Ensure "Dependabot alerts" is enabled
3. Ensure "Dependabot security updates" is enabled
4. Click "Enable" for both if needed

## Verification

Check that everything is working:

### Verify GitHub Actions:
```bash
git push origin main
```
Then check: https://github.com/raintree-technology/docpull/actions

You should see tests running.

### Verify Dependabot:
Check: https://github.com/raintree-technology/docpull/network/updates

You should see "Dependabot is checking for updates."

### Verify Release Automation:
```bash
# After first manual upload to PyPI
bump2version patch
git push origin --tags
```

Check:
- GitHub Actions: https://github.com/raintree-technology/docpull/actions
- PyPI: https://pypi.org/project/docpull/

New version should appear within 5-10 minutes.

## Complete

From now on:
- Push code - tests run automatically
- Push tags - releases happen automatically
- Dependencies update automatically
- Issues get triaged automatically

Total maintenance time: ~1-2 hours per month

## Optional: Customize Automation

See [MAINTENANCE.md](MAINTENANCE.md) for customization options:
- Adjust Dependabot frequency
- Change stale issue timeouts
- Disable certain automations
- Add more workflows

## Troubleshooting

"Permission denied" errors in GitHub Actions:
- Check Settings → Actions → General → Workflow permissions
- Ensure "Read and write permissions" is enabled

Release to PyPI failed:
- Verify `PYPI_API_TOKEN` secret is set correctly
- Check GitHub Actions logs for specific error
- Make sure package name is available on PyPI

Dependabot PRs not auto-merging:
- Tests must pass first
- Only patch/minor updates auto-merge
- Major updates require manual review

Still having issues:
Open an issue with the `ci-cd` label and include:
- What you're trying to do
- Error messages from GitHub Actions logs
- Steps you've already tried

## Quick Reference

To release a new version:
```bash
bump2version patch && git push origin --tags
```

To disable a workflow temporarily:
Go to Actions → Select workflow → ••• → Disable workflow

To check automation status:
- Actions: https://github.com/raintree-technology/docpull/actions
- PyPI: https://pypi.org/project/docpull/#history
- Dependabot: Settings → Security → Dependabot alerts

For complete documentation, see [MAINTENANCE.md](MAINTENANCE.md).
