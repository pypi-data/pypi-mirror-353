"""Integration protocols for type-safe interfaces."""

from typing import Protocol, Dict, Any, List, Optional, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class CIPlatformIntegrationProtocol(Protocol):
    """Protocol for CI platform integrations."""
    
    @abstractmethod
    def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook event from CI platform."""
        ...
    
    @abstractmethod
    def analyze_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze failure data from CI platform."""
        ...
    
    @abstractmethod
    def update_status(self, repository: str, commit_sha: str, status: Dict[str, Any]) -> None:
        """Update status on CI platform."""
        ...


@runtime_checkable
class ChatPlatformIntegrationProtocol(Protocol):
    """Protocol for chat platform integrations."""
    
    @abstractmethod
    def send_message(self, channel: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send a message to the chat platform."""
        ...
    
    @abstractmethod
    def format_failure_message(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format failure data for the platform."""
        ...


@runtime_checkable
class EditorIntegrationProtocol(Protocol):
    """Protocol for editor integrations."""
    
    @abstractmethod
    def highlight_failures(self, failures: List[Dict[str, Any]]) -> None:
        """Highlight failures in the editor."""
        ...
    
    @abstractmethod
    def navigate_to_line(self, file_path: str, line_number: int) -> None:
        """Navigate to a specific line in a file."""
        ...
    
    @abstractmethod
    def show_hover_info(self, file_path: str, line_number: int) -> Optional[str]:
        """Show hover information for a specific location."""
        ...