"""Tests for Chrome Web Store client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from chrome_extension_info import ChromeWebStoreClient, ExtensionMetadata
from chrome_extension_info.exceptions import ExtensionNotFoundError, ChromeExtensionInfoError


class TestChromeWebStoreClient:
    """Test cases for ChromeWebStoreClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return ChromeWebStoreClient(cache_ttl=60, rate_limit_delay=0.1)
    
    @pytest.fixture
    def mock_html_response(self):
        """Mock HTML response from Chrome Web Store."""
        return """
        <html>
        <head>
            <title>Test Extension - Chrome Web Store</title>
            <meta name="description" content="This is a test extension for ChromePy">
        </head>
        <body>
            <h1>Test Extension</h1>
            <div role="img" aria-label="4.5 out of 5 stars">★★★★☆</div>
            <div>10,000 users</div>
            <a href="/developer/test-dev">Test Developer</a>
        </body>
        </html>
        """
    
    def test_initialization(self, client):
        """Test client initialization."""
        assert client.cache_ttl == 60
        assert client.rate_limit_delay == 0.1
        assert client.session is not None
        assert 'User-Agent' in client.session.headers
    
    def test_rate_limiting(self, client):
        """Test rate limiting enforcement."""
        start_time = time.time()
        client._enforce_rate_limit()
        client._enforce_rate_limit()
        elapsed = time.time() - start_time
        assert elapsed >= client.rate_limit_delay
    
    def test_cache_operations(self, client):
        """Test cache get and save operations."""
        test_data = {'name': 'Test Extension', 'id': 'test123'}
        
        # Test cache miss
        assert client._get_from_cache('test123') is None
        
        # Test cache save and hit
        client._save_to_cache('test123', test_data)
        cached = client._get_from_cache('test123')
        assert cached == test_data
        
        # Test cache expiration
        client._cache['test123']['timestamp'] = time.time() - client.cache_ttl - 1
        assert client._get_from_cache('test123') is None
    
    def test_parse_user_count(self, client):
        """Test parsing of user count strings."""
        assert client._parse_user_count("10,000+ users") == 10000
        assert client._parse_user_count("1,234,567 users") == 1234567
        assert client._parse_user_count("500+") == 500
        assert client._parse_user_count("") == 0
        assert client._parse_user_count("no users") == 0
    
    def test_extract_metadata_from_html(self, client, mock_html_response):
        """Test metadata extraction from HTML."""
        metadata = client._extract_metadata_from_html(mock_html_response, 'test123')
        
        assert metadata['id'] == 'test123'
        assert metadata['name'] == 'Test Extension'
        assert metadata['description'] == 'This is a test extension for ChromePy'
        assert metadata['user_count'] == 10000
        assert metadata['rating'] == 4.5
        assert metadata['developer'] == 'Test Developer'
    
    @patch('requests.Session.get')
    def test_get_extension_success(self, mock_get, client, mock_html_response):
        """Test successful extension fetching."""
        mock_response = Mock()
        mock_response.text = mock_html_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = client.get_extension('test123')
        
        assert isinstance(result, ExtensionMetadata)
        assert result.id == 'test123'
        assert result.name == 'Test Extension'
        assert result.description == 'This is a test extension for ChromePy'
        
        # Verify caching
        cached = client._get_from_cache('test123')
        assert cached is not None
    
    @patch('requests.Session.get')
    def test_get_extension_not_found(self, mock_get, client):
        """Test extension not found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception()
        mock_get.return_value = mock_response
        
        with pytest.raises(ExtensionNotFoundError):
            client.get_extension('nonexistent')
    
    @patch('requests.Session.get')
    def test_get_extension_network_error(self, mock_get, client):
        """Test network error handling."""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(ChromeExtensionInfoError) as exc_info:
            client.get_extension('test123')
        
        assert "Error fetching extension data" in str(exc_info.value)
    
    def test_get_extension_by_url(self, client):
        """Test extracting extension ID from URL."""
        # Test standard URL format
        with patch.object(client, 'get_extension') as mock_get:
            mock_get.return_value = ExtensionMetadata(id='aapbdbdomjkkjkaonfhkkikfgjllcleb')
            
            url = "https://chrome.google.com/webstore/detail/google-translate/aapbdbdomjkkjkaonfhkkikfgjllcleb"
            client.get_extension_by_url(url)
            mock_get.assert_called_with('aapbdbdomjkkjkaonfhkkikfgjllcleb')
        
        # Test invalid URL
        with pytest.raises(ChromeExtensionInfoError):
            client.get_extension_by_url("https://invalid-url.com")
    
    def test_search_not_implemented(self, client):
        """Test that search raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            client.search_extensions("test query")