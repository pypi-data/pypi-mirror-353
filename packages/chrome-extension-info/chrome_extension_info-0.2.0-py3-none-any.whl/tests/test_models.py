"""Tests for data models."""

import pytest
from chrome_extension_info.models import ExtensionMetadata, SearchResult


class TestExtensionMetadata:
    """Test cases for ExtensionMetadata model."""
    
    def test_initialization_minimal(self):
        """Test creating metadata with minimal fields."""
        metadata = ExtensionMetadata(id="test123")
        assert metadata.id == "test123"
        assert metadata.name is None
        assert metadata.user_count is None
        assert metadata.tags == []
        assert metadata.screenshots == []
    
    def test_initialization_full(self):
        """Test creating metadata with all fields."""
        metadata = ExtensionMetadata(
            id="test123",
            name="Test Extension",
            description="A test extension",
            version="1.0.0",
            developer="Test Dev",
            user_count=10000,
            rating=4.5,
            rating_count=100,
            category="Productivity",
            tags=["test", "example"],
            icon_url="https://example.com/icon.png",
            featured=True
        )
        
        assert metadata.id == "test123"
        assert metadata.name == "Test Extension"
        assert metadata.description == "A test extension"
        assert metadata.version == "1.0.0"
        assert metadata.developer == "Test Dev"
        assert metadata.user_count == 10000
        assert metadata.rating == 4.5
        assert metadata.rating_count == 100
        assert metadata.category == "Productivity"
        assert metadata.tags == ["test", "example"]
        assert metadata.icon_url == "https://example.com/icon.png"
        assert metadata.featured is True
    
    def test_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = ExtensionMetadata(
            id="test123",
            name="Test Extension",
            version="1.0.0",
            user_count=5000,
            rating=4.2
        )
        
        result = metadata.to_dict()
        
        assert isinstance(result, dict)
        assert result['id'] == "test123"
        assert result['name'] == "Test Extension"
        assert result['version'] == "1.0.0"
        assert result['user_count'] == 5000
        assert result['rating'] == 4.2
        assert result['description'] is None
        assert result['tags'] == []
    
    def test_str_representation(self):
        """Test string representation of metadata."""
        # Test with minimal data
        metadata1 = ExtensionMetadata(id="test123")
        assert str(metadata1) == "Unknown (test123)"
        
        # Test with name only
        metadata2 = ExtensionMetadata(id="test123", name="Test Extension")
        assert str(metadata2) == "Test Extension (test123)"
        
        # Test with full data
        metadata3 = ExtensionMetadata(
            id="test123",
            name="Test Extension",
            version="1.0.0",
            user_count=10000,
            rating=4.5
        )
        assert str(metadata3) == "Test Extension (test123) - v1.0.0 - 10,000 users - ★4.5"


class TestSearchResult:
    """Test cases for SearchResult model."""
    
    def test_initialization(self):
        """Test creating a search result."""
        ext1 = ExtensionMetadata(id="ext1", name="Extension 1")
        ext2 = ExtensionMetadata(id="ext2", name="Extension 2")
        
        result = SearchResult(
            extensions=[ext1, ext2],
            total_results=50,
            query="test query"
        )
        
        assert len(result.extensions) == 2
        assert result.total_results == 50
        assert result.query == "test query"
    
    def test_len(self):
        """Test length of search result."""
        ext1 = ExtensionMetadata(id="ext1")
        ext2 = ExtensionMetadata(id="ext2")
        result = SearchResult(extensions=[ext1, ext2])
        
        assert len(result) == 2
    
    def test_iteration(self):
        """Test iterating over search result."""
        ext1 = ExtensionMetadata(id="ext1", name="Extension 1")
        ext2 = ExtensionMetadata(id="ext2", name="Extension 2")
        result = SearchResult(extensions=[ext1, ext2])
        
        names = [ext.name for ext in result]
        assert names == ["Extension 1", "Extension 2"]
    
    def test_indexing(self):
        """Test accessing extensions by index."""
        ext1 = ExtensionMetadata(id="ext1", name="Extension 1")
        ext2 = ExtensionMetadata(id="ext2", name="Extension 2")
        result = SearchResult(extensions=[ext1, ext2])
        
        assert result[0].id == "ext1"
        assert result[1].id == "ext2"
        
        with pytest.raises(IndexError):
            _ = result[2]