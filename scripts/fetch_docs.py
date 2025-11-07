#!/usr/bin/env python3
"""
Fetch Stripe and Plaid documentation from their sitemaps.
Converts HTML to markdown and saves organized by category.
"""

import os
import re
import time
import urllib.parse
from pathlib import Path
from typing import List, Dict, Set
import xml.etree.ElementTree as ET

try:
    import requests
    from bs4 import BeautifulSoup
    import html2text
except ImportError:
    print("Installing required packages...")
    os.system("pip3 install requests beautifulsoup4 html2text")
    import requests
    from bs4 import BeautifulSoup
    import html2text


class DocFetcher:
    """Fetches and organizes documentation from sitemaps."""

    def __init__(self, base_dir: str, rate_limit: float = 0.5):
        self.base_dir = Path(base_dir)
        self.rate_limit = rate_limit
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # Don't wrap text
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_sitemap(self, url: str) -> List[str]:
        """Fetch and parse XML sitemap."""
        print(f"Fetching sitemap: {url}")
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Handle namespace
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # Extract all URLs
            urls = []
            for url_elem in root.findall('.//ns:url/ns:loc', namespace):
                if url_elem.text:
                    urls.append(url_elem.text)

            # If no namespace, try without
            if not urls:
                for url_elem in root.findall('.//url/loc'):
                    if url_elem.text:
                        urls.append(url_elem.text)

            print(f"Found {len(urls)} URLs in sitemap")
            return urls

        except Exception as e:
            print(f"Error fetching sitemap {url}: {e}")
            return []

    def filter_technical_docs(self, urls: List[str], patterns: List[str], exclude_patterns: List[str] = None) -> List[str]:
        """Filter URLs to only technical documentation."""
        filtered = []
        exclude_patterns = exclude_patterns or []

        for url in urls:
            # Check if URL matches any include pattern
            if any(pattern in url for pattern in patterns):
                # Check if URL doesn't match any exclude pattern
                if not any(ex_pattern in url for ex_pattern in exclude_patterns):
                    filtered.append(url)

        print(f"Filtered to {len(filtered)} technical documentation URLs")
        return filtered

    def categorize_urls(self, urls: List[str], base_url: str) -> Dict[str, List[str]]:
        """Categorize URLs based on their path structure."""
        categories = {}

        for url in urls:
            # Remove base URL and parse path
            path = url.replace(base_url, '').strip('/')

            if not path:
                continue

            # Get the first path segment as category
            parts = path.split('/')
            if len(parts) > 0:
                category = parts[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(url)

        return categories

    def clean_filename(self, url: str, base_url: str) -> str:
        """Convert URL to a clean filename."""
        # Remove base URL
        path = url.replace(base_url, '').strip('/')

        # Replace slashes with hyphens
        filename = path.replace('/', '-')

        # Remove or replace problematic characters
        filename = re.sub(r'[^\w\-.]', '-', filename)

        # Remove multiple consecutive hyphens
        filename = re.sub(r'-+', '-', filename)

        # Ensure .md extension
        if not filename.endswith('.md'):
            filename += '.md'

        return filename

    def fetch_page_content(self, url: str) -> str:
        """Fetch a single page and convert to markdown."""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            # Try to find main content area
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find(class_=re.compile(r'content|documentation|docs')) or
                soup.find('body')
            )

            if main_content:
                # Convert to markdown
                markdown = self.h2t.handle(str(main_content))

                # Add frontmatter
                frontmatter = f"""---
url: {url}
fetched: {time.strftime('%Y-%m-%d')}
---

"""
                return frontmatter + markdown.strip()
            else:
                return f"# Error\n\nCould not find main content for {url}"

        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return f"# Error\n\nFailed to fetch {url}\n\nError: {str(e)}"

    def save_content(self, content: str, filepath: Path):
        """Save content to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def fetch_stripe_docs(self):
        """Fetch all Stripe documentation."""
        print("\n" + "="*80)
        print("FETCHING STRIPE DOCUMENTATION")
        print("="*80 + "\n")

        stripe_dir = self.base_dir / 'stripe'
        sitemap_url = 'https://docs.stripe.com/sitemap.xml'
        base_url = 'https://docs.stripe.com/'

        # Fetch sitemap
        urls = self.fetch_sitemap(sitemap_url)

        if not urls:
            print("No URLs found in Stripe sitemap")
            return

        # Filter for technical docs (exclude changelog noise)
        exclude_patterns = ['/changelog/', '/upgrades/']
        urls = [u for u in urls if not any(p in u for p in exclude_patterns)]

        # Categorize URLs
        categories = self.categorize_urls(urls, base_url)

        print(f"\nFound {len(categories)} categories:")
        for cat, cat_urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {cat}: {len(cat_urls)} pages")

        # Fetch each page
        total = len(urls)
        for idx, url in enumerate(urls, 1):
            print(f"\n[{idx}/{total}] Processing Stripe documentation...")

            # Determine category and subcategory
            path = url.replace(base_url, '').strip('/')
            parts = path.split('/')

            # Create organized directory structure
            if len(parts) >= 2:
                category_dir = stripe_dir / parts[0] / parts[1]
            elif len(parts) == 1:
                category_dir = stripe_dir / parts[0]
            else:
                category_dir = stripe_dir / 'other'

            # Generate filename
            filename = self.clean_filename(url, base_url)
            filepath = category_dir / filename

            # Skip if already exists
            if filepath.exists():
                print(f"  Skipping (already exists): {filepath}")
                continue

            # Fetch and save
            content = self.fetch_page_content(url)
            self.save_content(content, filepath)

            print(f"  Saved: {filepath}")

            # Rate limiting
            time.sleep(self.rate_limit)

        print(f"\n✓ Stripe documentation fetch complete!")

    def fetch_plaid_docs(self):
        """Fetch all Plaid documentation."""
        print("\n" + "="*80)
        print("FETCHING PLAID DOCUMENTATION")
        print("="*80 + "\n")

        plaid_dir = self.base_dir / 'plaid'

        # Plaid doesn't have a comprehensive docs sitemap, so we'll use known patterns
        # and crawl from the main docs page

        base_docs_url = 'https://plaid.com/docs/'

        print(f"Fetching Plaid docs index from {base_docs_url}")

        try:
            response = self.session.get(base_docs_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links to documentation pages
            doc_urls = set()
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Convert relative URLs to absolute
                if href.startswith('/docs/'):
                    href = 'https://plaid.com' + href
                elif href.startswith('/api/'):
                    href = 'https://plaid.com' + href

                # Only include docs and api pages
                if 'plaid.com/docs/' in href or 'plaid.com/api/' in href:
                    # Remove anchors and query params
                    href = href.split('#')[0].split('?')[0]
                    doc_urls.add(href)

            # Also try the sitemap
            sitemap_urls = self.fetch_sitemap('https://plaid.com/sitemap.xml')

            # Filter sitemap for docs and API pages
            for url in sitemap_urls:
                if '/docs/' in url or '/api/' in url:
                    # Exclude blog, marketing
                    if not any(x in url for x in ['/blog/', '/resources/', '/company/', '/customers/']):
                        doc_urls.add(url.split('#')[0].split('?')[0])

            doc_urls = sorted(list(doc_urls))

            print(f"Found {len(doc_urls)} Plaid documentation URLs")

            # Fetch each page
            total = len(doc_urls)
            for idx, url in enumerate(doc_urls, 1):
                print(f"\n[{idx}/{total}] Processing Plaid documentation...")

                # Determine directory structure
                if '/api/' in url:
                    path = url.replace('https://plaid.com/api/', '').strip('/')
                    category_dir = plaid_dir / 'api-reference'
                elif '/docs/' in url:
                    path = url.replace('https://plaid.com/docs/', '').strip('/')
                    category_dir = plaid_dir / 'guides'
                else:
                    category_dir = plaid_dir / 'other'

                # Create subdirectories based on path
                if '/' in path:
                    parts = path.split('/')
                    category_dir = category_dir / parts[0]

                # Generate filename
                filename = self.clean_filename(url, 'https://plaid.com/')
                filepath = category_dir / filename

                # Skip if already exists
                if filepath.exists():
                    print(f"  Skipping (already exists): {filepath}")
                    continue

                # Fetch and save
                content = self.fetch_page_content(url)
                self.save_content(content, filepath)

                print(f"  Saved: {filepath}")

                # Rate limiting
                time.sleep(self.rate_limit)

            print(f"\n✓ Plaid documentation fetch complete!")

        except Exception as e:
            print(f"Error fetching Plaid docs: {e}")

    def fetch_supabase_docs(self):
        """Fetch all Supabase documentation."""
        print("\n" + "="*80)
        print("FETCHING SUPABASE DOCUMENTATION")
        print("="*80 + "\n")

        supabase_dir = self.base_dir / 'supabase'
        sitemap_url = 'https://supabase.com/docs/sitemap.xml'
        base_url = 'https://supabase.com/'

        # Fetch sitemap
        urls = self.fetch_sitemap(sitemap_url)

        if not urls:
            print("No URLs found in Supabase sitemap")
            return

        # Filter for docs pages only
        doc_patterns = ['/docs/']
        exclude_patterns = ['/blog/', '/customers/', '/partners/', '/ga-week/', '/launch-week/']
        urls = self.filter_technical_docs(urls, doc_patterns, exclude_patterns)

        # Categorize URLs
        categories = self.categorize_urls(urls, base_url + 'docs/')

        print(f"\nFound {len(categories)} categories:")
        for cat, cat_urls in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {cat}: {len(cat_urls)} pages")

        # Fetch each page
        total = len(urls)
        for idx, url in enumerate(urls, 1):
            print(f"\n[{idx}/{total}] Processing Supabase documentation...")

            # Determine category and subcategory
            path = url.replace(base_url + 'docs/', '').strip('/')
            parts = path.split('/')

            # Create organized directory structure
            if len(parts) >= 2:
                category_dir = supabase_dir / parts[0] / parts[1]
            elif len(parts) == 1:
                category_dir = supabase_dir / parts[0]
            else:
                category_dir = supabase_dir / 'other'

            # Generate filename
            filename = self.clean_filename(url, base_url)
            # Change extension to .txt
            filename = filename.replace('.md', '.txt')
            filepath = category_dir / filename

            # Skip if already exists
            if filepath.exists():
                print(f"  Skipping (already exists): {filepath}")
                continue

            # Fetch and save
            content = self.fetch_page_content(url)
            self.save_content(content, filepath)

            print(f"  Saved: {filepath}")

            # Rate limiting
            time.sleep(self.rate_limit)

        print(f"\n✓ Supabase documentation fetch complete!")


def main():
    """Main execution function."""
    docs_dir = Path(__file__).parent / 'docs'

    fetcher = DocFetcher(docs_dir, rate_limit=0.5)

    print("Documentation Fetcher")
    print("=" * 80)
    print(f"Output directory: {docs_dir}")
    print(f"Rate limit: {fetcher.rate_limit}s between requests")
    print()

    # Fetch Supabase docs
    fetcher.fetch_supabase_docs()

    print("\n" + "="*80)
    print("ALL DOCUMENTATION FETCHED SUCCESSFULLY")
    print("="*80)


if __name__ == '__main__':
    main()
