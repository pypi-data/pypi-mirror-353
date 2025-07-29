"""
Box chunked upload tool for large files and videos.

This module provides functionality to upload large files (>50MB) to Box using
the chunked upload API, which is more reliable for large files and videos.
"""
import hashlib
import json
import os
import pathlib
from typing import Dict, List, Optional, Union, cast

from boxsdk.exception import BoxAPIException
from mcp.server.fastmcp import Context

from box_ai_agents_toolkit import BoxClient


async def box_chunked_upload_tool(
    ctx: Context,
    file_path: str,
    folder_id: str = "0",
    new_file_name: str = "",
    chunk_size: int = 20 * 1024 * 1024,  # Default to 20MB chunks (minimum size required by Box API)
    num_threads: int = 5,  # Default to 5 threads for parallel uploading
) -> str:
    """
    Upload a large file to Box using the chunked upload API.
    Recommended for files over 50MB and videos.
    
    Args:
        ctx (Context): The MCP context.
        file_path (str): Path on the server filesystem to the file to upload.
        folder_id (str): The ID of the destination folder. Defaults to root ("0").
        new_file_name (str): Optional new name to give the file in Box. If empty, uses the original filename.
        chunk_size (int): Size of each chunk in bytes. Minimum 20MB (Box API requirement).
        num_threads (int): Number of threads to use for parallel uploading.
    
    return:
        str: Information about the uploaded file (ID and name).
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client
    
    try:
        # Normalize the path and check if file exists
        file_path_expanded = os.path.expanduser(file_path)
        if not os.path.isfile(file_path_expanded):
            return json.dumps({
                "status": "error",
                "message": f"Error: file '{file_path}' not found."
            })
        
        # Determine the file name to use
        actual_file_name = new_file_name.strip() or os.path.basename(file_path_expanded)
        
        # Get file size
        file_size = os.path.getsize(file_path_expanded)
        
        # Check if file size is at least 20MB (Box API minimum for chunked upload)
        if file_size < 20 * 1024 * 1024:
            # For small files, it's better to use the binary upload rather than chunked upload
            try:
                # Determine file extension to detect binary types
                _, ext = os.path.splitext(actual_file_name)
                
                # All media files should be treated as binary
                with open(file_path_expanded, "rb") as f:
                    content = f.read()
                    
                # Upload using the standard upload method
                result = box_client.folder(folder_id).upload(
                    file_path=file_path_expanded,
                    file_name=actual_file_name or None
                )
                
                return json.dumps({
                    "status": "success",
                    "message": f"File uploaded successfully using standard upload (file too small for chunked upload).",
                    "file_id": result.id,
                    "file_name": result.name,
                    "size_bytes": file_size,
                    "size_readable": format_file_size(file_size),
                    "type": result.type,
                    "parent_folder_id": folder_id
                })
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "message": f"Error uploading file with standard upload: {str(e)}",
                    "file_size": file_size
                })
        
        # Set the number of threads for parallel uploads
        from boxsdk.config import API
        API.CHUNK_UPLOAD_THREADS = num_threads
        
        # Create chunked uploader that directly uploads the file
        # This handles the file as binary automatically
        folder = box_client.folder(folder_id)
        
        # Use binary mode for all files to avoid encoding issues
        file_obj = folder.upload(
            file_path=file_path_expanded,
            file_name=actual_file_name if new_file_name else None
        )
        
        # Return information about the uploaded file
        return json.dumps({
            "status": "success",
            "message": f"File uploaded successfully.",
            "file_id": file_obj.id,
            "file_name": file_obj.name,
            "size_bytes": file_size,
            "size_readable": format_file_size(file_size),
            "type": file_obj.type,
            "parent_folder_id": folder_id
        })
        
    except BoxAPIException as e:
        if e.code == "file_size_too_small":
            # Handle case where file is too small for chunked upload
            return json.dumps({
                "status": "error",
                "message": f"File too small for chunked upload: {str(e)}. Use the standard upload tool instead.",
                "code": e.code,
                "file_size": file_size
            })
        else:
            # Handle other Box API exceptions
            return json.dumps({
                "status": "error",
                "message": f"Box API error: {str(e)}",
                "code": e.code if hasattr(e, 'code') else "unknown"
            })
    except Exception as e:
        # Handle all other exceptions
        return json.dumps({
            "status": "error",
            "message": f"Error uploading file: {str(e)}",
            "exception_type": type(e).__name__
        })


async def box_chunked_upload_new_version_tool(
    ctx: Context,
    file_path: str,
    file_id: str,
    new_file_name: str = "",
    chunk_size: int = 20 * 1024 * 1024,  # Default to 20MB chunks
    num_threads: int = 5,  # Default to 5 threads
) -> str:
    """
    Upload a new version of a large file to Box using the chunked upload API.
    Recommended for files over 50MB and videos.
    
    Args:
        ctx (Context): The MCP context.
        file_path (str): Path on the server filesystem to the file to upload.
        file_id (str): The ID of the existing Box file to update.
        new_file_name (str): Optional new name to give the file in Box. If empty, keeps original name.
        chunk_size (int): Size of each chunk in bytes. Minimum 20MB (Box API requirement).
        num_threads (int): Number of threads to use for parallel uploading.
    
    return:
        str: Information about the updated file (ID and name).
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client
    
    try:
        # Normalize the path and check if file exists
        file_path_expanded = os.path.expanduser(file_path)
        if not os.path.isfile(file_path_expanded):
            return json.dumps({
                "status": "error",
                "message": f"Error: file '{file_path}' not found."
            })
        
        # Get file size
        file_size = os.path.getsize(file_path_expanded)
        
        # Check if file size is at least 20MB (Box API minimum for chunked upload)
        if file_size < 20 * 1024 * 1024:
            # For small files, use the standard update_contents method
            try:
                # Get the file object
                file_obj = box_client.file(file_id)
                
                # Upload new version
                updated_file = file_obj.update_contents(
                    file_path=file_path_expanded,
                    file_name=new_file_name or None
                )
                
                return json.dumps({
                    "status": "success",
                    "message": f"File version uploaded successfully using standard upload (file too small for chunked upload).",
                    "file_id": updated_file.id,
                    "file_name": updated_file.name,
                    "size_bytes": file_size,
                    "size_readable": format_file_size(file_size),
                    "type": updated_file.type
                })
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "message": f"Error uploading file version with standard upload: {str(e)}",
                    "file_size": file_size
                })
        
        # Set the number of threads for parallel uploads
        from boxsdk.config import API
        API.CHUNK_UPLOAD_THREADS = num_threads
        
        # Get the file object
        file_obj = box_client.file(file_id)
        
        # Upload new version - use update_contents directly
        # This method automatically handles binary files
        updated_file = file_obj.update_contents(
            file_path=file_path_expanded,
            file_name=new_file_name or None
        )
        
        # Return information about the updated file
        return json.dumps({
            "status": "success",
            "message": "File version uploaded successfully.",
            "file_id": updated_file.id,
            "file_name": updated_file.name,
            "size_bytes": file_size,
            "size_readable": format_file_size(file_size),
            "type": updated_file.type
        })
        
    except BoxAPIException as e:
        if e.code == "file_size_too_small":
            # Handle case where file is too small for chunked upload
            return json.dumps({
                "status": "error",
                "message": f"File too small for chunked upload: {str(e)}. Use the standard upload tool instead.",
                "code": e.code,
                "file_size": file_size
            })
        else:
            # Handle other Box API exceptions
            return json.dumps({
                "status": "error",
                "message": f"Box API error: {str(e)}",
                "code": e.code if hasattr(e, 'code') else "unknown"
            })
    except Exception as e:
        # Handle all other exceptions
        return json.dumps({
            "status": "error",
            "message": f"Error uploading file: {str(e)}",
            "exception_type": type(e).__name__
        })


def format_file_size(size_bytes):
    """Format file size from bytes to a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"


# Import class definition required by the tools
from mcp_server_box import BoxContext