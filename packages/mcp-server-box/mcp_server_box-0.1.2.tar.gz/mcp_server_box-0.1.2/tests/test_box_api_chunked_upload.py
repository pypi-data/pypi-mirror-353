"""
Tests for the Box chunked upload implementation for large files.
"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch

from box_chunked_upload_tool import (
    box_chunked_upload_tool,
    box_chunked_upload_new_version_tool,
    format_file_size
)


def test_format_file_size():
    """Test the file size formatting utility function."""
    assert format_file_size(500) == "500.00 B"
    assert format_file_size(1500) == "1.46 KB"
    assert format_file_size(1500000) == "1.43 MB"
    assert format_file_size(1500000000) == "1.40 GB"
    assert format_file_size(1500000000000) == "1.36 TB"


@pytest.mark.asyncio
async def test_chunked_upload_file_not_found(mock_context):
    """Test handling of a nonexistent file."""
    # Setup
    mock_context.request_context.lifespan_context.client = MagicMock()
    
    # Call the function with a file that doesn't exist
    result = await box_chunked_upload_tool(
        mock_context,
        file_path="/nonexistent/file.mp4",
        folder_id="12345"
    )
    
    # Check results
    result_json = json.loads(result)
    assert result_json["status"] == "error"
    assert "not found" in result_json["message"]


@pytest.mark.asyncio
@patch('os.path.isfile')
@patch('os.path.getsize')
@patch('os.path.expanduser')
async def test_chunked_upload_file_too_small(mock_expanduser, mock_getsize, mock_isfile, mock_context):
    """Test handling of a file that's too small for chunked upload."""
    # Setup
    mock_isfile.return_value = True
    mock_getsize.return_value = 10 * 1024 * 1024  # 10MB, below the 20MB minimum
    mock_expanduser.return_value = "/path/to/mock_file.mp4"
    mock_context.request_context.lifespan_context.client = MagicMock()
    
    # Call the function
    result = await box_chunked_upload_tool(
        mock_context,
        file_path="~/mock_file.mp4",
        folder_id="12345"
    )
    
    # Check results
    result_json = json.loads(result)
    assert result_json["status"] == "warning"
    assert "smaller than 20MB" in result_json["message"]
    assert result_json["file_size"] == 10 * 1024 * 1024


@pytest.mark.asyncio
@patch('os.path.isfile')
@patch('os.path.getsize')
@patch('os.path.expanduser')
@patch('os.path.basename')
async def test_chunked_upload_api_exception(mock_basename, mock_expanduser, mock_getsize, mock_isfile, mock_context, box_api_exception):
    """Test handling of a Box API exception."""
    # Setup
    from boxsdk.exception import BoxAPIException
    
    mock_isfile.return_value = True
    mock_getsize.return_value = 50 * 1024 * 1024  # 50MB
    mock_expanduser.return_value = "/path/to/mock_file.mp4"
    mock_basename.return_value = "mock_file.mp4"
    
    # Create mock client and folder
    mock_client = MagicMock()
    mock_folder = MagicMock()
    mock_client.folder.return_value = mock_folder
    
    # Make the folder's get_chunked_uploader raise a BoxAPIException
    mock_chunked_uploader = MagicMock()
    mock_folder.get_chunked_uploader.return_value = mock_chunked_uploader
    mock_chunked_uploader.start.side_effect = box_api_exception("file_size_too_small", "File size too small for chunked upload")
    
    mock_context.request_context.lifespan_context.client = mock_client
    
    # Call the function
    result = await box_chunked_upload_tool(
        mock_context,
        file_path="~/mock_file.mp4",
        folder_id="12345"
    )
    
    # Check results
    result_json = json.loads(result)
    assert result_json["status"] == "error"
    assert "too small" in result_json["message"]
    assert result_json["code"] == "file_size_too_small"


@pytest.mark.asyncio
@patch('os.path.isfile')
@patch('os.path.getsize')
@patch('os.path.expanduser')
@patch('os.path.basename')
async def test_successful_chunked_upload(mock_basename, mock_expanduser, mock_getsize, mock_isfile, mock_context):
    """Test a successful chunked upload."""
    # Setup
    mock_isfile.return_value = True
    mock_getsize.return_value = 100 * 1024 * 1024  # 100MB
    mock_expanduser.return_value = "/path/to/large_video.mp4"
    mock_basename.return_value = "large_video.mp4"
    
    # Create mock client, folder, and chunked uploader
    mock_client = MagicMock()
    mock_folder = MagicMock()
    mock_client.folder.return_value = mock_folder
    
    # Create a mock uploaded file
    mock_file = MagicMock()
    mock_file.id = "file_123456"
    mock_file.name = "large_video.mp4"
    mock_file.type = "file"
    
    # Set up the chunked uploader to return our mock file
    mock_chunked_uploader = MagicMock()
    mock_folder.get_chunked_uploader.return_value = mock_chunked_uploader
    mock_chunked_uploader.start.return_value = mock_file
    
    mock_context.request_context.lifespan_context.client = mock_client
    
    # Call the function
    result = await box_chunked_upload_tool(
        mock_context,
        file_path="~/large_video.mp4",
        folder_id="12345"
    )
    
    # Check results
    result_json = json.loads(result)
    assert result_json["status"] == "success"
    assert result_json["file_id"] == "file_123456"
    assert result_json["file_name"] == "large_video.mp4"
    assert result_json["size_bytes"] == 100 * 1024 * 1024
    assert result_json["size_readable"] == "100.00 MB"
    assert result_json["type"] == "file"
    assert result_json["parent_folder_id"] == "12345"
    
    # Verify the mock was called correctly
    mock_client.folder.assert_called_once_with("12345")
    mock_folder.get_chunked_uploader.assert_called_once_with("/path/to/large_video.mp4", rename_file=False)
    mock_chunked_uploader.start.assert_called_once()


@pytest.mark.asyncio
@patch('os.path.isfile')
@patch('os.path.getsize')
@patch('os.path.expanduser')
@patch('os.path.basename')
async def test_chunked_upload_new_version(mock_basename, mock_expanduser, mock_getsize, mock_isfile, mock_context):
    """Test chunked upload of a new file version."""
    # Setup
    mock_isfile.return_value = True
    mock_getsize.return_value = 100 * 1024 * 1024  # 100MB
    mock_expanduser.return_value = "/path/to/large_video_v2.mp4"
    mock_basename.return_value = "large_video_v2.mp4"
    
    # Create mock client and file
    mock_client = MagicMock()
    mock_file_obj = MagicMock()
    mock_client.file.return_value = mock_file_obj
    
    # Create a mock uploaded file version
    mock_file_version = MagicMock()
    mock_file_version.id = "file_123456"
    mock_file_version.name = "large_video_v2.mp4"
    mock_file_version.type = "file"
    
    # Set up the chunked uploader to return our mock file
    mock_chunked_uploader = MagicMock()
    mock_file_obj.get_chunked_uploader.return_value = mock_chunked_uploader
    mock_chunked_uploader.start.return_value = mock_file_version
    
    mock_context.request_context.lifespan_context.client = mock_client
    
    # Call the function
    result = await box_chunked_upload_new_version_tool(
        mock_context,
        file_path="~/large_video_v2.mp4",
        file_id="old_file_id",
        new_file_name="updated_video.mp4"
    )
    
    # Check results
    result_json = json.loads(result)
    assert result_json["status"] == "success"
    assert result_json["file_id"] == "file_123456"
    assert result_json["file_name"] == "large_video_v2.mp4"
    assert result_json["size_bytes"] == 100 * 1024 * 1024
    assert result_json["size_readable"] == "100.00 MB"
    assert result_json["type"] == "file"
    
    # Verify the mock was called correctly
    mock_client.file.assert_called_once_with("old_file_id")
    mock_file_obj.get_chunked_uploader.assert_called_once_with("/path/to/large_video_v2.mp4", rename_file=True)
    mock_chunked_uploader.start.assert_called_once()


# Fixtures

@pytest.fixture
def mock_context():
    """Create a mock context for testing."""
    context = MagicMock()
    lifespan_context = MagicMock()
    context.request_context.lifespan_context = lifespan_context
    return context


@pytest.fixture
def box_api_exception():
    """Create a BoxAPIException factory."""
    from boxsdk.exception import BoxAPIException
    
    def _create_exception(code, message, status=400):
        exception = BoxAPIException({
            'code': code,
            'message': message,
            'status': status
        })
        exception.code = code
        return exception
    
    return _create_exception