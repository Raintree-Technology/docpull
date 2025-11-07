"""Setup configuration for doc_fetcher package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="doc-fetcher",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A flexible documentation fetching and conversion tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/doc-fetcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "html2text>=2020.1.16",
    ],
    extras_require={
        "yaml": ["pyyaml>=6.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "doc-fetcher=doc_fetcher.cli:main",
        ],
    },
)
