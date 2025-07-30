import jenkins
from typing import Dict, List, Optional, Any, Union

from .config import jenkins_settings


class JenkinsClient:
    """Client for interacting with Jenkins API."""
    
    def __init__(self):
        """Initialize the Jenkins client using configuration settings."""
        auth_args = {}
        try:
            if jenkins_settings.username:
                # Prefer token over password if available
                if jenkins_settings.token:
                    auth_args = {
                        'username': jenkins_settings.username,
                        'password': jenkins_settings.token
                    }
                elif jenkins_settings.password:
                    auth_args = {
                        'username': jenkins_settings.username,
                        'password': jenkins_settings.password
                    }
            
            self.server = jenkins.Jenkins(jenkins_settings.jenkins_url, **auth_args)
            # Test connection by getting version info
            version = self.server.get_version()
            print(f"Connected to Jenkins version {version}")
        except Exception as e:
            print(f"Error connecting to Jenkins: {str(e)}")
            print("Please check your Jenkins server settings in VS Code settings.json or .env file")
            # Initialize with a dummy server to avoid crashes
            self.server = None
        
    def get_jobs(self) -> List[Dict[str, Any]]:
        """Get a list of all Jenkins jobs."""
        try:
            if self.server is None:
                return []
            return self.server.get_jobs()
        except Exception as e:
            print(f"Error getting Jenkins jobs: {str(e)}")
            return []
    
    def get_job_info(self, job_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific job."""
        try:
            if self.server is None:
                raise ValueError("Jenkins client not initialized")
            return self.server.get_job_info(job_name)
        except Exception as e:
            print(f"Error getting job info for {job_name}: {str(e)}")
            raise
    
    def get_build_info(self, job_name: str, build_number: int) -> Dict[str, Any]:
        """Get information about a specific build."""
        try:
            if self.server is None:
                raise ValueError("Jenkins client not initialized")
            return self.server.get_build_info(job_name, build_number)
        except Exception as e:
            print(f"Error getting build info for {job_name} #{build_number}: {str(e)}")
            raise
    
    def get_build_console_output(self, job_name: str, build_number: int) -> str:
        """Get console output from a build."""
        try:
            if self.server is None:
                raise ValueError("Jenkins client not initialized")
            return self.server.get_build_console_output(job_name, build_number)
        except Exception as e:
            print(f"Error getting build console for {job_name} #{build_number}: {str(e)}")
            raise
    
    def build_job(self, job_name: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """Trigger a build for a job."""
        return self.server.build_job(job_name, parameters=parameters)
    
    def cancel_queue_item(self, queue_item_id: int) -> None:
        """Cancel a queued build."""
        self.server.cancel_queue_item(queue_item_id)
    
    def stop_build(self, job_name: str, build_number: int) -> None:
        """Stop a running build."""
        self.server.stop_build(job_name, build_number)
    
    def get_queue_info(self) -> List[Dict[str, Any]]:
        """Get information about the queue."""
        return self.server.get_queue_info()
    
    def get_node_info(self, node_name: str) -> Dict[str, Any]:
        """Get information about a specific node."""
        return self.server.get_node_info(node_name)
    
    def get_nodes(self) -> List[Dict[str, str]]:
        """Get a list of all nodes."""
        return self.server.get_nodes()


# Create a singleton instance
jenkins_client = JenkinsClient()
