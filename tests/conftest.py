"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary output directory for tests."""
    output_dir = tmp_path / "test_docs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_html():
    """Provide sample HTML for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Test Heading</h1>
        <p>Test paragraph with <a href="/link">a link</a>.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </body>
    </html>
    """


@pytest.fixture
def sample_config():
    """Provide sample configuration dictionary."""
    return {
        "output_dir": "./docs",
        "rate_limit": 0.5,
        "skip_existing": True,
        "log_level": "INFO",
    }
