# Release Checklist for docpull v1.0.0

This checklist ensures everything is ready for your first PyPI release.

## Pre-Release Checklist (Complete Before Publishing)

### 1. Organization Approval
- [ ] PyPI organization request approved (submitted Nov 7, 2025)
  - Check: https://pypi.org/manage/organizations/

### 2. PyPI Account Setup
- [ ] PyPI account created and email verified
- [ ] Added to `raintree-technology` organization (after approval)
- [ ] API token created for the organization
  - Go to: https://pypi.org/manage/account/token/
  - Create token with name: `docpull-github-actions`
  - Scope: "Entire account" (will be scoped to project after first upload)

### 3. GitHub Secrets
- [ ] `PYPI_API_TOKEN` added to GitHub repository secrets
  - Go to: https://github.com/raintree-technology/docpull/settings/secrets/actions
  - Click "New repository secret"
  - Name: `PYPI_API_TOKEN`
  - Value: Your PyPI token (starts with `pypi-`)

### 4. GitHub Settings
- [ ] GitHub Actions enabled
  - Check: https://github.com/raintree-technology/docpull/settings/actions
  - Ensure "Allow all actions" is selected
  - Ensure "Read and write permissions" is enabled
- [ ] Dependabot enabled
  - Check: https://github.com/raintree-technology/docpull/settings/security_analysis
  - Enable "Dependabot alerts" and "Dependabot security updates"

### 5. Code Quality Check
- [ ] All tests pass locally: `make test`
- [ ] Code formatting clean: `make format`
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `make type-check`
- [ ] Security scans clean: `make security`

### 6. Documentation Review
- [ ] README.md is accurate and complete
- [ ] CHANGELOG.md documents v1.0.0 features
- [ ] All example code works
- [ ] Links in documentation are valid

### 7. Package Metadata
- [ ] `pyproject.toml` has correct author: Zachary Roth
- [ ] `pyproject.toml` has correct email: support@raintree.technology
- [ ] `pyproject.toml` has correct organization: Raintree Technology
- [ ] `LICENSE` has correct copyright: 2025 Raintree Technology
- [ ] Version is `1.0.0` in both `pyproject.toml` and `docpull/__init__.py`

## First Release Steps (After Organization Approval)

### Step 1: Test Build Locally
```bash
# Clean any old builds
make clean

# Build the package
python -m build

# Check the built package
twine check dist/*

# Expected output: "Checking dist/docpull-1.0.0.tar.gz: PASSED"
#                  "Checking dist/docpull-1.0.0-py3-none-any.whl: PASSED"
```

### Step 2: First Manual Upload (Required)
```bash
# Upload to PyPI manually for the first time
twine upload dist/*

# Enter credentials when prompted:
# Username: __token__
# Password: pypi-... (your API token)

# Expected output: "View at: https://pypi.org/project/docpull/1.0.0/"
```

### Step 3: Create Git Tag
```bash
# Tag the release
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"

# Push the tag (DO NOT DO THIS YET - it will trigger auto-release)
# git push origin v1.0.0
```

### Step 4: Verify Manual Upload
- [ ] Check PyPI page: https://pypi.org/project/docpull/
- [ ] Test installation: `pip install docpull`
- [ ] Test CLI: `docpull --version` (should show 1.0.0)
- [ ] Test import: `python -c "from docpull import StripeFetcher; print('OK')"`

### Step 5: Update PyPI Token Scope
After first successful upload:
1. Go to https://pypi.org/manage/account/token/
2. Delete the old token
3. Create a new token:
   - Name: `docpull-github-actions`
   - Scope: "Project: docpull" (now available after first upload)
4. Update GitHub secret with new token

### Step 6: Test Automated Release
```bash
# Now test the automated release workflow
git tag -a v1.0.1-test -m "Test automated release"
git push origin v1.0.1-test

# Watch GitHub Actions: https://github.com/raintree-technology/docpull/actions
# Should see: Build → Publish to PyPI → Create GitHub Release
# Check PyPI: https://pypi.org/project/docpull/
# Should see v1.0.1-test appear within 5-10 minutes
```

### Step 7: Clean Up Test Release
```bash
# Delete test release from PyPI (via PyPI web interface)
# Delete test tag locally and remote
git tag -d v1.0.1-test
git push origin --delete v1.0.1-test
```

## Ongoing Releases (After Setup Complete)

All future releases are fully automated:

```bash
# For patch release (1.0.0 → 1.0.1)
bump2version patch
git push origin --tags

# For minor release (1.0.0 → 1.1.0)
bump2version minor
git push origin --tags

# For major release (1.0.0 → 2.0.0)
bump2version major
git push origin --tags
```

That's it! Everything else happens automatically.

## Post-Release Verification

After each release, verify:
- [ ] Package appears on PyPI: https://pypi.org/project/docpull/
- [ ] GitHub release created: https://github.com/raintree-technology/docpull/releases
- [ ] Badges update on README (may take a few minutes)
- [ ] Can install via pip: `pip install --upgrade docpull`

## Troubleshooting

**Organization request still pending?**
- Can take up to a few days for PyPI to approve
- Check email for updates from PyPI
- In the meantime, you can publish under your personal account

**"Package name already taken" error?**
- The name `docpull` should be available
- If not, check https://pypi.org/project/docpull/
- May need to choose a different name

**GitHub Actions failing?**
- Check the logs at https://github.com/raintree-technology/docpull/actions
- Most common issue: Missing or incorrect `PYPI_API_TOKEN`
- Verify token has correct permissions

**First upload failing?**
- Make sure you're using `__token__` as username
- Make sure token starts with `pypi-`
- Try with `--verbose` flag: `twine upload --verbose dist/*`

## Support

If you encounter issues:
1. Check [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)
2. Check [MAINTENANCE.md](MAINTENANCE.md)
3. Review GitHub Actions logs
4. Open an issue with the `ci-cd` label

---

## Status: Waiting for PyPI Organization Approval

**Submitted:** November 7, 2025
**Organization:** raintree-technology
**Package:** docpull
**Author:** Zachary Roth

Once approved, follow the steps above to complete your first release!
