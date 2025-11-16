#!/bin/bash
# Pre-push validation script
# Run this before pushing to ensure all tests and checks pass

set -e

echo "🔍 Running validation checks before push..."
echo ""

# Reinstall package in editable mode to ensure latest code is used
echo "📦 Reinstalling package..."
pip install -e . --no-deps > /dev/null 2>&1
echo "✅ Package reinstalled"
echo ""

# Run tests
echo "📝 Running tests..."
pytest --tb=short -q
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi
echo "✅ Tests passed"
echo ""

# Run linting
echo "🔎 Running ruff linting..."
ruff check docpull/
if [ $? -ne 0 ]; then
    echo "❌ Linting failed"
    exit 1
fi
echo "✅ Linting passed"
echo ""

# Run type checking
echo "🔍 Running mypy type checking..."
mypy docpull/
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed"
    exit 1
fi
echo "✅ Type checking passed"
echo ""

echo "✅ All validation checks passed - safe to push!"
exit 0
