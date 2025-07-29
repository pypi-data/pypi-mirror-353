import pytest
import json
import os
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_box_client():
    mock_client = MagicMock()
    # Mock a file object with a shared link
    mock_file = MagicMock()
    mock_file.id = "12345"
    mock_file.name = "test_file.pdf"
    
    # Mock the shared link object
    mock_shared_link = MagicMock()
    mock_shared_link.url = "https://app.box.com/s/abcdef123456"
    mock_shared_link.download_url = "https://app.box.com/shared/static/abcdef123456.pdf"
    mock_shared_link.vanity_url = None
    mock_shared_link.effective_access = "open"
    mock_shared_link.is_password_enabled = False
    mock_shared_link.unshared_at = None
    mock_shared_link.download_count = 0
    mock_shared_link.preview_count = 0
    
    # Attach the shared link to the file
    mock_file.shared_link = mock_shared_link
    
    # Set up the mock client response
    mock_client.files.get_file_by_id.return_value = mock_file
    mock_client.files.update_file_by_id.return_value = mock_file
    
    return mock_client


class MockContext:
    def __init__(self, mock_client):
        class MockRequestContext:
            def __init__(self, mock_client):
                class MockLifespanContext:
                    def __init__(self, mock_client):
                        self.client = mock_client
                self.lifespan_context = MockLifespanContext(mock_client)
        self.request_context = MockRequestContext(mock_client)


@pytest.mark.asyncio
async def test_box_create_share_link_tool(mock_box_client):
    from src.box_share_link_tool import box_create_share_link_tool
    
    # Create a mock context with our mock client
    mock_context = MockContext(mock_box_client)
    
    # Call the function
    result = await box_create_share_link_tool(
        ctx=mock_context, 
        file_id="12345",
        access="open",
        can_download=True
    )
    
    # Verify the response
    result_data = json.loads(result)
    assert "url" in result_data
    assert result_data["url"] == "https://app.box.com/s/abcdef123456"
    assert result_data["effective_access"] == "open"
    assert result_data["is_password_enabled"] is False
    
    # Verify the call to Box API
    mock_box_client.files.update_file_by_id.assert_called_once_with(
        file_id="12345",
        shared_link={"access": "open", "permissions": {"can_download": True}}
    )


@pytest.mark.asyncio
async def test_box_get_shared_link_tool(mock_box_client):
    from src.box_share_link_tool import box_get_shared_link_tool
    
    # Create a mock context with our mock client
    mock_context = MockContext(mock_box_client)
    
    # Call the function
    result = await box_get_shared_link_tool(ctx=mock_context, file_id="12345")
    
    # Verify the response
    result_data = json.loads(result)
    assert "url" in result_data
    assert result_data["url"] == "https://app.box.com/s/abcdef123456"
    
    # Verify the call to Box API
    mock_box_client.files.get_file_by_id.assert_called_once_with("12345")


@pytest.mark.asyncio
async def test_box_remove_shared_link_tool(mock_box_client):
    from src.box_share_link_tool import box_remove_shared_link_tool
    
    # Create a mock context with our mock client
    mock_context = MockContext(mock_box_client)
    
    # Configure mock for removal case (file with no shared link)
    file_without_link = MagicMock()
    file_without_link.id = "12345"
    file_without_link.shared_link = None
    mock_box_client.files.update_file_by_id.return_value = file_without_link
    
    # Call the function
    result = await box_remove_shared_link_tool(ctx=mock_context, file_id="12345")
    
    # Verify the response
    result_data = json.loads(result)
    assert "message" in result_data
    assert result_data["message"] == "Shared link removed successfully"
    
    # Verify the call to Box API
    mock_box_client.files.update_file_by_id.assert_called_once_with(
        file_id="12345",
        shared_link=None
    )


@pytest.mark.asyncio
async def test_box_create_share_link_tool_advanced_options(mock_box_client):
    from src.box_share_link_tool import box_create_share_link_tool
    
    # Create a mock context with our mock client
    mock_context = MockContext(mock_box_client)
    
    # Call the function with advanced options
    result = await box_create_share_link_tool(
        ctx=mock_context, 
        file_id="12345",
        access="company",
        password="SecurePassword123",
        unshared_at="2023-12-31T23:59:59Z",
        vanity_name="my-document",
        can_download=False
    )
    
    # Verify the call to Box API with the correct parameters
    mock_box_client.files.update_file_by_id.assert_called_once()
    call_args = mock_box_client.files.update_file_by_id.call_args[1]
    
    # Check file_id
    assert call_args["file_id"] == "12345"
    
    # Check shared_link parameters
    shared_link_params = call_args["shared_link"]
    assert shared_link_params["access"] == "company"
    assert shared_link_params["password"] == "SecurePassword123"
    assert shared_link_params["unshared_at"] == "2023-12-31T23:59:59Z"
    assert shared_link_params["vanity_name"] == "my-document"
    assert shared_link_params["permissions"]["can_download"] is False