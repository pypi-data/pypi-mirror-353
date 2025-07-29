"""
Tests for the recursive folder upload functionality.
"""
import os
import tempfile
import uuid
import json
import pytest
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path


class MockContext:
    """Mock MCP Context class for testing."""
    def __init__(self, mock_client):
        class MockRequestContext:
            def __init__(self, mock_client):
                class MockLifespanContext:
                    def __init__(self, mock_client):
                        self.client = mock_client
                self.lifespan_context = MockLifespanContext(mock_client)
        self.request_context = MockRequestContext(mock_client)


@pytest.fixture
def mock_box_client():
    """Create a mock Box client for testing."""
    mock_client = MagicMock()
    
    # Mock folder object
    mock_folder = MagicMock()
    mock_folder.id = "12345"
    mock_folder.name = "test_folder"
    mock_folder.get.return_value = mock_folder
    
    # Mock file object
    mock_file = MagicMock()
    mock_file.id = "67890"
    mock_file.name = "test_file.txt"
    
    # Set up client method returns
    mock_client.folder.return_value = mock_folder
    mock_client.file.return_value = mock_file
    
    # Mock the update_contents method on the file
    mock_file.update_contents.return_value = mock_file
    
    return mock_client


@pytest.mark.asyncio
async def test_box_upload_folder_recursive_tool_basic():
    """Test the basic functionality of the folder upload tool."""
    from src.box_folder_upload_tool import box_upload_folder_tool
    from src.box_folder_upload_tool import file_upload, create_box_folder
    
    # Create a temporary directory structure for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files and subdirectories
        main_dir = Path(temp_dir)
        sub_dir = main_dir / "subdir"
        sub_dir.mkdir()
        
        # Create test files
        (main_dir / "file1.txt").write_text("Test file 1")
        (main_dir / "file2.txt").write_text("Test file 2")
        (sub_dir / "file3.txt").write_text("Test file 3")
        
        # Mock the Box client and create a context
        mock_client = MagicMock()
        mock_context = MockContext(mock_client)
        
        # Mock the core functions used by box_upload_folder_tool
        with patch('src.box_folder_upload_tool.file_upload') as mock_file_upload, \
             patch('src.box_folder_upload_tool.create_box_folder') as mock_create_folder:
            
            # Configure the mocks
            mock_file_upload.return_value = {"id": "123", "name": "file.txt", "action": "uploaded"}
            mock_create_folder.return_value = {"id": "456", "name": "folder", "action": "created"}
            
            # Run the function
            result = await box_upload_folder_tool(
                mock_context,
                temp_dir,
                "0"
            )
            
            # Parse the result
            result_data = json.loads(result)
            
            # Verify basic structure
            assert result_data["status"] == "success"
            assert result_data["source_folder"] == temp_dir
            assert result_data["destination_folder_id"] == "0"
            
            # Verify statistics - we should have uploaded 3 files and created 1 folder
            assert mock_file_upload.call_count == 3
            assert mock_create_folder.call_count == 1
            assert "details" in result_data


@pytest.mark.asyncio
async def test_box_upload_folder_recursive_tool_filters():
    """Test filtering capabilities of the folder upload tool."""
    from src.box_folder_upload_tool import box_upload_folder_tool
    
    # Create a temporary directory structure with various file types
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files and subdirectories
        main_dir = Path(temp_dir)
        
        # Create test files with different extensions
        (main_dir / "file1.txt").write_text("Test file 1")
        (main_dir / "file2.pdf").write_text("Test PDF file")
        (main_dir / "file3.jpg").write_text("Test image file")
        (main_dir / "file4.doc").write_text("Test doc file")
        (main_dir / ".hidden_file").write_text("Hidden file")
        
        # Mock the Box client and create a context
        mock_client = MagicMock()
        mock_context = MockContext(mock_client)
        
        # Mock the core functions used by box_upload_folder_tool
        with patch('src.box_folder_upload_tool.file_upload') as mock_file_upload, \
             patch('src.box_folder_upload_tool.create_box_folder') as mock_create_folder:
            
            # Configure the mocks
            mock_file_upload.return_value = {"id": "123", "name": "file.txt", "action": "uploaded"}
            mock_create_folder.return_value = {"id": "456", "name": "folder", "action": "created"}
            
            # Test include patterns - only include PDF and JPG files
            result = await box_upload_folder_tool(
                mock_context,
                temp_dir,
                "0",
                include_patterns=["*.pdf", "*.jpg"]
            )
            
            # Parse the result
            result_data = json.loads(result)
            
            # Should only have uploaded 2 files (PDF and JPG)
            assert mock_file_upload.call_count == 2
            assert result_data["status"] == "success"
            
            # Reset the mocks
            mock_file_upload.reset_mock()
            mock_create_folder.reset_mock()
            
            # Test exclude patterns - exclude hidden files and PDFs
            result = await box_upload_folder_tool(
                mock_context,
                temp_dir,
                "0",
                exclude_patterns=[".hidden*", "*.pdf"]
            )
            
            # Parse the result
            result_data = json.loads(result)
            
            # Should have uploaded 3 files (not the hidden file or PDF)
            assert mock_file_upload.call_count == 3
            assert result_data["status"] == "success"


@pytest.mark.asyncio
async def test_file_upload_function():
    """Test the file_upload function that handles upload vs. update."""
    from src.box_folder_upload_tool import file_upload
    from boxsdk.exception import BoxAPIException
    
    # Create a test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("Test content")
        file_path = temp_file.name
        
    try:
        # Case 1: New file upload
        mock_client = MagicMock()
        mock_folder = MagicMock()
        mock_client.folder.return_value = mock_folder
        mock_client.folder().get.return_value = mock_folder
        mock_folder.preflight_check.return_value = None  # No exception, new file
        
        # Mock the box_upload_file function
        with patch('src.box_folder_upload_tool.box_upload_file') as mock_upload:
            mock_upload.return_value = {"id": "123", "name": "file.txt"}
            
            # Call the function
            result = file_upload(mock_client, file_path, "0")
            
            # Verify results
            assert result["action"] == "uploaded"
            assert result["id"] == "123"
            mock_upload.assert_called_once()
        
        # Case 2: File already exists (update)
        mock_client = MagicMock()
        mock_folder = MagicMock()
        mock_file = MagicMock()
        mock_client.folder.return_value = mock_folder
        mock_client.folder().get.return_value = mock_folder
        mock_client.file.return_value = mock_file
        mock_file.update_contents.return_value = mock_file
        mock_file.id = "456"
        mock_file.name = "existing_file.txt"
        
        # Make preflight_check raise an item_name_in_use exception
        mock_error = BoxAPIException(
            status=409,
            code="item_name_in_use",
            message="Item with the same name already exists",
            request_id="123",
            headers={},
            url="",
            method="",
            context_info={"conflicts": {"id": "456"}}
        )
        mock_folder.preflight_check.side_effect = mock_error
        
        # Call the function 
        result = file_upload(mock_client, file_path, "0")
        
        # Verify results
        assert result["action"] == "updated"
        assert result["id"] == "456"
        mock_file.update_contents.assert_called_once_with(file_path)
        
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.unlink(file_path)


@pytest.mark.asyncio
async def test_create_box_folder_function():
    """Test the create_box_folder function that handles folder creation."""
    from src.box_folder_upload_tool import create_box_folder
    from boxsdk.exception import BoxAPIException
    
    # Case 1: New folder creation
    mock_client = MagicMock()
    
    # Mock the box_create_folder function
    with patch('src.box_folder_upload_tool.box_create_folder') as mock_create:
        mock_folder = MagicMock()
        mock_folder.id = "123"
        mock_folder.name = "test_folder"
        mock_create.return_value = mock_folder
        
        # Call the function
        result = create_box_folder(mock_client, "test_folder", "0")
        
        # Verify results
        assert result["action"] == "created"
        assert result["id"] == "123"
        assert result["name"] == "test_folder"
        mock_create.assert_called_once_with(mock_client, "test_folder", "0")
    
    # Case 2: Folder already exists
    mock_client = MagicMock()
    mock_folder = MagicMock()
    mock_client.folder.return_value = mock_folder
    mock_folder.id = "456"
    mock_folder.name = "existing_folder"
    mock_folder.get.return_value = mock_folder
    
    # Mock the box_create_folder function to raise an item_name_in_use exception
    with patch('src.box_folder_upload_tool.box_create_folder') as mock_create:
        mock_error = BoxAPIException(
            status=409,
            code="item_name_in_use",
            message="Item with the same name already exists",
            request_id="123",
            headers={},
            url="",
            method="",
            context_info={"conflicts": [{"id": "456"}]}
        )
        mock_create.side_effect = mock_error
        
        # Call the function
        result = create_box_folder(mock_client, "existing_folder", "0")
        
        # Verify results
        assert result["action"] == "exists"
        assert result["id"] == "456"
        assert result["name"] == "existing_folder"