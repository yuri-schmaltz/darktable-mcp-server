
import sys
import os
import shutil
from pathlib import Path

# Ensure host directory is in path
sys.path.insert(0, os.path.abspath("host"))

# Force re-import to pick up changes
import common
from common import _find_appimage, _suggested_darktable_cli, McpClient, DT_SERVER_CMD

print("--- Testing AppImage Detection ---")
appimage = _find_appimage()
print(f"AppImage found: {appimage}")

if appimage:
    print("--- Testing AppImage Mounting (McpClient) ---")
    client_info = {"name": "test", "version": "1.0"}
    
    # Instantiate McpClient
    client = McpClient(
        DT_SERVER_CMD, 
        "2024-11-05", 
        client_info, 
        appimage_path=appimage
    )
    
    # Check if msg_id exists (this was the bug)
    print(f"Initial msg_id: {client.msg_id}")
    next_id = client._next_id()
    print(f"Next ID: {next_id}")

    # Cleanup
    client.close()
    client._cleanup_appimage()
