import os
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any


def get_vscode_settings() -> Dict[str, Any]:
    """Get VS Code settings for Jenkins MCP server"""
    try:
        # Try to find VS Code settings.json
        home = Path.home()
        print("\nLooking for VS Code settings in:")
        settings_paths = [
            # macOS
            home / "Library/Application Support/Code/User/settings.json",
            home / "Library/Application Support/Code - Insiders/User/settings.json",
            # Linux
            home / ".config/Code/User/settings.json",
            home / ".config/Code - Insiders/User/settings.json",
            # Windows
            home / "AppData/Roaming/Code/User/settings.json",
            home / "AppData/Roaming/Code - Insiders/User/settings.json",
        ]
        
        workspace_settings = Path.cwd() / ".vscode/settings.json"
        if workspace_settings.exists():
            settings_paths.insert(0, workspace_settings)
            print(f"Found workspace settings at: {workspace_settings}")
        
        for path in settings_paths:
            print(f"Checking {path}")
            if path.exists():
                print(f"Found settings at: {path}")
                with open(path, 'r') as f:
                    settings = json.load(f)
                    jenkins_settings = settings.get("jenkins-mcp-server", {}).get("jenkins", {})
                    if jenkins_settings:
                        print("Found Jenkins settings in VS Code config")
                        # Don't print sensitive values
                        safe_settings = jenkins_settings.copy()
                        if 'password' in safe_settings:
                            safe_settings['password'] = '****'
                        if 'token' in safe_settings:
                            safe_settings['token'] = '****'
                        print(f"Settings found: {json.dumps(safe_settings, indent=2)}")
                        return jenkins_settings
                    else:
                        print("No Jenkins settings found in this file")
        
        print("No Jenkins settings found in any VS Code settings file")
        return {}
    except Exception as e:
        print(f"Error reading VS Code settings: {e}")
        return {}


class JenkinsSettings(BaseSettings):
    """Jenkins connection settings."""
    jenkins_url: str = "http://localhost:8080"
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None  # API token can be used instead of password
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "JENKINS_",
        "case_sensitive": False,
        "populate_by_name": True,
    }


# Try to get settings from VS Code first
print("\nAttempting to load settings...")
vscode_settings = get_vscode_settings()

# Create settings instance from environment variables
print("\nLoading environment variables...")
jenkins_settings = JenkinsSettings()

# Override with VS Code settings if available
if vscode_settings:
    print("\nOverriding with VS Code settings...")
    if 'url' in vscode_settings:
        print(f"Using URL from VS Code: {vscode_settings['url']}")
        jenkins_settings.jenkins_url = vscode_settings['url']
    if 'username' in vscode_settings:
        print(f"Using username from VS Code: {vscode_settings['username']}")
        jenkins_settings.username = vscode_settings['username']
    if 'token' in vscode_settings:
        print("Using token from VS Code settings")
        jenkins_settings.token = vscode_settings['token']
    if 'password' in vscode_settings:
        print("Using password from VS Code settings")
        jenkins_settings.password = vscode_settings['password']

# Log final configuration
print(f"\nFinal configuration:")
print(f"Jenkins server configured: {jenkins_settings.jenkins_url}")
if jenkins_settings.username:
    print(f"Using authentication for user: {jenkins_settings.username}")
    if jenkins_settings.token:
        print("Authentication method: API Token")
    elif jenkins_settings.password:
        print("Authentication method: Password")
else:
    print("No authentication configured for Jenkins")
