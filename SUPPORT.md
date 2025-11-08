# Support

This document provides information on how to get help with docpull.

## Documentation

- [README.md](README.md) - Quick start and basic usage
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup and contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history and release notes
- [SECURITY.md](SECURITY.md) - Security features and reporting vulnerabilities

## Getting Help

### Before Opening an Issue

1. Check the documentation and examples in `docs/examples/`
2. Search existing issues
3. Update to the latest version: `pip install --upgrade docpull`

### How to Ask for Help

#### For Questions and Discussions

Use [GitHub Discussions](https://github.com/raintree-technology/docpull/discussions) for:
- General questions about usage
- Feature ideas and brainstorming
- Community support
- Showcasing your projects

#### For Bug Reports

Open an [issue](https://github.com/raintree-technology/docpull/issues/new?template=bug_report.md) if you encounter:
- Unexpected behavior
- Errors or crashes
- Installation problems
- Documentation errors

Please include:
- docpull version (`docpull --version`)
- Python version (`python --version`)
- Operating system
- Steps to reproduce the issue
- Error messages and logs

#### For Feature Requests

Open a [feature request](https://github.com/raintree-technology/docpull/issues/new?template=feature_request.md) if you'd like to suggest:
- New features
- Enhancements to existing functionality
- New documentation sources

#### For New Documentation Sources

Use the [new source template](https://github.com/raintree-technology/docpull/issues/new?template=new_source.md) to propose adding support for a new documentation site.

## Community Support

### Response Times

This is an open-source project maintained by volunteers. Response times may vary:

- **Bug reports**: We aim to respond within 1-3 days
- **Feature requests**: We aim to respond within 1 week
- **Pull requests**: We aim to review within 1 week

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to set up your development environment
- Coding standards and best practices
- How to submit pull requests
- Adding new documentation sources

## Commercial Support

For commercial support, custom development, or consulting services:
- Email: support@raintree.technology
- Website: https://raintree.technology

## Security Issues

Do not open public issues for security vulnerabilities. Email support@raintree.technology and see [SECURITY.md](SECURITY.md) for details.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

Report unacceptable behavior to support@raintree.technology.

## Useful Resources

- **PyPI Package**: https://pypi.org/project/docpull/
- **Source Code**: https://github.com/raintree-technology/docpull
- **Issue Tracker**: https://github.com/raintree-technology/docpull/issues
- **Discussions**: https://github.com/raintree-technology/docpull/discussions

## Example Usage

Quick examples to get started:

```bash
# Fetch Stripe documentation
docpull --sources stripe --output-dir ./docs

# Fetch multiple sources
docpull --sources stripe plaid nextjs --output-dir ./docs

# Use a config file
docpull --config config.yaml

# Generate a config file
docpull --generate-config config.yaml
```

For more examples, see `docs/examples/`.
