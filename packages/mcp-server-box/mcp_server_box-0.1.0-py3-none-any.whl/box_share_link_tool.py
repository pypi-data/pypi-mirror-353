"""
Box shared link management tools.

This module provides functionality to create, get, and remove shared links for Box files.
"""
import json
from typing import Dict, Optional

from mcp.server.fastmcp import Context


async def box_create_share_link_tool(
    ctx: Context,
    file_id: str,
    access: str = "open",
    password: Optional[str] = None,
    unshared_at: Optional[str] = None,
    vanity_name: Optional[str] = None,
    can_download: bool = True,
) -> str:
    """Create a shared link for a Box file.

    Args:
        ctx (Context): The MCP context.
        file_id (str): The ID of the file to share.
        access (str, optional): The level of access. Options: 'open', 'company', 'collaborators'. Defaults to "open".
        password (str, optional): Optional password to protect the link.
        unshared_at (str, optional): The date when the link should expire (ISO-8601 format).
        vanity_name (str, optional): Defines a custom vanity name for the shared link.
        can_download (bool, optional): Whether the file can be downloaded. Defaults to True.

    Returns:
        str: The shared link information as JSON string
    """
    # No import needed

    # Get the Box client
    box_client = ctx.request_context.lifespan_context.client

    # Prepare shared link parameters
    shared_link_params = {
        "access": access
    }

    # Add optional parameters if provided
    if password is not None:
        shared_link_params["password"] = password

    if unshared_at is not None:
        shared_link_params["unshared_at"] = unshared_at

    if vanity_name is not None:
        shared_link_params["vanity_name"] = vanity_name

    # Add download permissions
    shared_link_params["permissions"] = {
        "can_download": can_download
    }

    try:
        # Create the shared link
        updated_file = box_client.files.update_file_by_id(
            file_id=file_id,
            shared_link=shared_link_params
        )

        # Return the shared link information
        if updated_file.shared_link:
            result = {
                "url": updated_file.shared_link.url,
                "download_url": updated_file.shared_link.download_url,
                "vanity_url": updated_file.shared_link.vanity_url,
                "effective_access": updated_file.shared_link.effective_access,
                "is_password_enabled": updated_file.shared_link.is_password_enabled,
                "unshared_at": str(updated_file.shared_link.unshared_at) if updated_file.shared_link.unshared_at else None,
                "download_count": updated_file.shared_link.download_count,
                "preview_count": updated_file.shared_link.preview_count,
            }
            return json.dumps(result)
        else:
            return json.dumps({"error": "Failed to create shared link"})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def box_get_shared_link_tool(ctx: Context, file_id: str) -> str:
    """Get an existing shared link for a Box file.

    Args:
        ctx (Context): The MCP context.
        file_id (str): The ID of the file.

    Returns:
        str: The shared link information or a message that no shared link exists.
    """
    # No import needed

    # Get the Box client
    box_client = ctx.request_context.lifespan_context.client
    
    try:
        # Get the file
        file = box_client.files.get_file_by_id(file_id)
        
        # Check if a shared link exists
        if file.shared_link:
            result = {
                "url": file.shared_link.url,
                "download_url": file.shared_link.download_url,
                "vanity_url": file.shared_link.vanity_url,
                "effective_access": file.shared_link.effective_access,
                "is_password_enabled": file.shared_link.is_password_enabled,
                "unshared_at": str(file.shared_link.unshared_at) if file.shared_link.unshared_at else None,
                "download_count": file.shared_link.download_count,
                "preview_count": file.shared_link.preview_count,
            }
            return json.dumps(result)
        else:
            return json.dumps({"message": "No shared link exists for this file"})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def box_remove_shared_link_tool(ctx: Context, file_id: str) -> str:
    """Remove a shared link from a Box file.

    Args:
        ctx (Context): The MCP context.
        file_id (str): The ID of the file.

    Returns:
        str: Confirmation message.
    """
    # No import needed

    # Get the Box client
    box_client = ctx.request_context.lifespan_context.client
    
    try:
        # Remove the shared link by setting it to null
        updated_file = box_client.files.update_file_by_id(
            file_id=file_id,
            shared_link=None
        )
        
        # Check if the operation was successful
        if updated_file.shared_link is None:
            return json.dumps({"message": "Shared link removed successfully"})
        else:
            return json.dumps({"error": "Failed to remove shared link"})
    except Exception as e:
        return json.dumps({"error": str(e)})