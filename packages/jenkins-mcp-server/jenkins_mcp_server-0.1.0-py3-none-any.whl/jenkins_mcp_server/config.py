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
        
        for path in settings_paths:
            if path.exists():
                with open(path, 'r') as f:
                    settings = json.load(f)
                    jenkins_settings = settings.get("jenkins-mcp-server", {}).get("jenkins", {})
                    if jenkins_settings:
                        return jenkins_settings
        
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


# Try to get settings from VS Code first, then fall back to environment variables
vscode_settings = get_vscode_settings()

# Create settings instance initially from environment variables
jenkins_settings = JenkinsSettings()

# Override with VS Code settings if available (these take precedence)
if vscode_settings:
    # Map common fields
    if vscode_settings.get('url'):
        jenkins_settings.jenkins_url = vscode_settings['url']
    if vscode_settings.get('username'):
        jenkins_settings.username = vscode_settings['username']
    if vscode_settings.get('password'):
        jenkins_settings.password = vscode_settings['password']
    if vscode_settings.get('token'):
        jenkins_settings.token = vscode_settings['token']

# Log connection information (without credentials)
print(f"Jenkins server configured: {jenkins_settings.jenkins_url}")
if jenkins_settings.username:
    print(f"Using authentication for user: {jenkins_settings.username}")
else:
    print("No authentication configured for Jenkins")
