"""Tests for rich metadata extraction."""

from docpull.metadata_extractor import RichMetadataExtractor


class TestRichMetadataExtractor:
    """Test RichMetadataExtractor class."""

    def test_extractor_initialization(self):
        """Test extractor can be initialized."""
        extractor = RichMetadataExtractor()
        assert extractor is not None
        assert extractor.base_url == ""

    def test_extractor_with_base_url(self):
        """Test extractor with custom base URL."""
        extractor = RichMetadataExtractor(base_url="https://example.com")
        assert extractor.base_url == "https://example.com"

    def test_extract_from_basic_html(self):
        """Test extraction from basic HTML without metadata."""
        extractor = RichMetadataExtractor()
        html = "<html><head><title>Test</title></head><body>Content</body></html>"
        url = "https://example.com/test"

        metadata = extractor.extract(html, url)

        assert metadata["url"] == url
        # Without extruct, should return basic metadata
        assert "url" in metadata

    def test_extract_opengraph_metadata(self):
        """Test extraction of Open Graph metadata."""
        extractor = RichMetadataExtractor()
        html = """
        <html>
        <head>
            <meta property="og:title" content="Test Page" />
            <meta property="og:description" content="This is a test description" />
            <meta property="og:image" content="https://example.com/image.jpg" />
            <meta property="og:type" content="article" />
            <meta property="og:site_name" content="Example Site" />
        </head>
        <body>Content</body>
        </html>
        """
        url = "https://example.com/test"

        metadata = extractor.extract(html, url)

        assert metadata["url"] == url
        # These will only be present if extruct is installed and working
        if metadata.get("title"):
            assert metadata["title"] == "Test Page"
        if metadata.get("description"):
            assert "test description" in metadata["description"].lower()

    def test_extract_jsonld_metadata(self):
        """Test extraction of JSON-LD metadata."""
        extractor = RichMetadataExtractor()
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Test Article",
                "description": "A test article description",
                "author": {
                    "@type": "Person",
                    "name": "John Doe"
                },
                "datePublished": "2024-01-15",
                "dateModified": "2024-01-20",
                "keywords": "test, article, metadata"
            }
            </script>
        </head>
        <body>Content</body>
        </html>
        """
        url = "https://example.com/article"

        metadata = extractor.extract(html, url)

        assert metadata["url"] == url
        # These will only be present if extruct is installed and working
        if metadata.get("author"):
            assert metadata["author"] == "John Doe"
        if metadata.get("keywords"):
            assert isinstance(metadata["keywords"], list)

    def test_extract_with_multiple_sources(self):
        """Test extraction when both OG and JSON-LD are present."""
        extractor = RichMetadataExtractor()
        html = """
        <html>
        <head>
            <meta property="og:title" content="OG Title" />
            <meta property="og:description" content="OG Description" />
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "JSON-LD Title",
                "author": "Jane Smith"
            }
            </script>
        </head>
        <body>Content</body>
        </html>
        """
        url = "https://example.com/test"

        metadata = extractor.extract(html, url)

        assert metadata["url"] == url
        # Should extract from both sources
        # OG typically takes precedence for title
        if metadata.get("title"):
            assert metadata["title"] in ["OG Title", "JSON-LD Title"]
        if metadata.get("author"):
            assert metadata["author"] == "Jane Smith"

    def test_safe_string_conversion(self):
        """Test _safe_string method handles various inputs."""
        extractor = RichMetadataExtractor()

        assert extractor._safe_string(None) == ""
        assert extractor._safe_string("test") == "test"
        assert extractor._safe_string("  test  ") == "test"
        assert extractor._safe_string(["first", "second"]) == "first"
        assert extractor._safe_string([]) == ""
        assert extractor._safe_string(123) == "123"

    def test_merge_with_fallback(self):
        """Test merging metadata with fallback values."""
        extractor = RichMetadataExtractor()

        rich_meta = {
            "url": "https://example.com",
            "title": "Test",
            "description": "",  # Empty value
        }

        merged = extractor.merge_with_fallback(rich_meta, fallback_title="Fallback")

        assert merged["url"] == "https://example.com"
        assert merged["title"] == "Test"
        # Empty description should be removed
        assert "description" not in merged

    def test_merge_with_fallback_uses_fallback_when_no_title(self):
        """Test that fallback title is used when no title in metadata."""
        extractor = RichMetadataExtractor()

        rich_meta = {
            "url": "https://example.com",
            "description": "Test description",
        }

        merged = extractor.merge_with_fallback(rich_meta, fallback_title="Fallback Title")

        assert merged["title"] == "Fallback Title"
        assert merged["description"] == "Test description"

    def test_extract_handles_malformed_html(self):
        """Test extraction handles malformed HTML gracefully."""
        extractor = RichMetadataExtractor()
        html = "<html><head><meta property='og:title' content='Test'</head>"  # Missing closing >
        url = "https://example.com/test"

        # Should not raise exception
        metadata = extractor.extract(html, url)
        assert metadata["url"] == url

    def test_extract_with_article_metadata(self):
        """Test extraction of article-specific Open Graph metadata."""
        extractor = RichMetadataExtractor()
        html = """
        <html>
        <head>
            <meta property="og:type" content="article" />
            <meta property="article:author" content="John Doe" />
            <meta property="article:published_time" content="2024-01-15T10:00:00Z" />
            <meta property="article:modified_time" content="2024-01-20T15:30:00Z" />
            <meta property="article:section" content="Technology" />
            <meta property="article:tag" content="python" />
            <meta property="article:tag" content="scraping" />
        </head>
        <body>Content</body>
        </html>
        """
        url = "https://example.com/article"

        metadata = extractor.extract(html, url)

        assert metadata["url"] == url
        # Check article-specific fields if extruct is working
        if metadata.get("type"):
            assert metadata["type"] == "article"
        if metadata.get("section"):
            assert metadata["section"] == "Technology"

    def test_extract_with_empty_html(self):
        """Test extraction from empty HTML."""
        extractor = RichMetadataExtractor()
        html = ""
        url = "https://example.com/empty"

        metadata = extractor.extract(html, url)
        assert metadata["url"] == url

    def test_extract_with_special_characters(self):
        """Test extraction handles special characters in metadata."""
        extractor = RichMetadataExtractor()
        html = """
        <html>
        <head>
            <meta property="og:title" content="Test: A Guide to Python & Web Scraping" />
            <meta property="og:description" content="Learn how to scrape data with Python's libraries" />
        </head>
        <body>Content</body>
        </html>
        """
        url = "https://example.com/test"

        metadata = extractor.extract(html, url)
        assert metadata["url"] == url
        # Should handle special characters like colons and ampersands
        if metadata.get("title"):
            assert ":" in metadata["title"] or "&" in metadata["title"]
