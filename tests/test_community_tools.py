
import pytest
from unittest.mock import AsyncMock, patch
from omnicoreagent.community.tavily_search import TavilySearch
from omnicoreagent.community.google_search import GoogleSearch
from omnicoreagent.core.tools.local_tools_registry import Tool, ToolRegistry

@pytest.mark.asyncio
async def test_registry_register_and_merge():
    registry1 = ToolRegistry()
    registry2 = ToolRegistry()
    
    # Test register
    tool = Tool(name="test_tool", description="desc", inputSchema={}, function=lambda: None)
    registry1.register(tool)
    assert registry1.get_tool("test_tool") == tool
    
    # Test merge
    registry2.merge(registry1)
    assert registry2.get_tool("test_tool") == tool

@pytest.mark.asyncio
async def test_tavily_search_initialization():
    with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
        tavily = TavilySearch()
        assert tavily.api_key == "test-key"
        tool = tavily.get_tool()
        assert isinstance(tool, Tool)
        assert tool.name == "tavily_search"

@pytest.mark.asyncio
async def test_tavily_search_execution():
    with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
        tavily = TavilySearch()
        
        mock_response = {"results": [{"title": "Test Result", "url": "http://example.com"}]}
        
        # Create a mock response object
        response_mock = AsyncMock()
        response_mock.json.return_value = mock_response
        response_mock.raise_for_status = AsyncMock() # Wait, raise_for_status is sync in httpx, but if we use AsyncMock for client it might be tricky.
        # Actually, let's use a MagicMock for the response, but the client.post call must be async.
        
        response_obj = AsyncMock()
        # json() is a regular method, not async
        response_obj.json = lambda: mock_response
        # raise_for_status() is a regular method
        response_obj.raise_for_status = lambda: None
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = response_obj
            
            result = await tavily._search("test query")
            
            # Verify standardized response format
            assert isinstance(result, dict)
            assert result["status"] == "success"
            assert result["data"] == mock_response
            assert "Test Result" in result["message"]
            mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_google_search_initialization():
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key", "GOOGLE_CSE_ID": "test-cse-id"}):
        google = GoogleSearch()
        assert google.api_key == "test-key"
        assert google.cse_id == "test-cse-id"
        tool = google.get_tool()
        assert isinstance(tool, Tool)
        assert tool.name == "google_search"

@pytest.mark.asyncio
async def test_google_search_execution():
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key", "GOOGLE_CSE_ID": "test-cse-id"}):
        google = GoogleSearch()
        
        mock_response = {"items": [{"title": "Test Result", "link": "http://example.com"}]}
        
        response_obj = AsyncMock()
        response_obj.json = lambda: mock_response
        response_obj.raise_for_status = lambda: None
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = response_obj
            
            result = await google._search("test query")
            
            # Verify standardized response format
            assert isinstance(result, dict)
            assert result["status"] == "success"
            assert result["data"] == mock_response
            assert "Found 1 results" in result["message"]
            mock_get.assert_called_once()
