"""Common data types for integrations."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any


class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass


@dataclass
class GitHubEvent:
    """Represents a GitHub webhook event."""
    event_type: str
    action: str
    repository: Dict[str, Any]
    pull_request: Optional[Dict[str, Any]] = None
    workflow_run: Optional[Dict[str, Any]] = None
    check_run: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class ChatMessage:
    """Represents a chat message for notifications."""
    platform: str  # slack, teams, discord
    channel: str
    message: str
    attachments: List[Dict[str, Any]]
    thread_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class CIStatus:
    """Represents CI/CD pipeline status."""
    pipeline_id: str
    status: str  # pending, running, success, failure, cancelled
    stage: str
    job_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    failure_count: int = 0
    test_results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        # Convert datetime objects to ISO strings
        result['start_time'] = self.start_time.isoformat()
        if self.end_time:
            result['end_time'] = self.end_time.isoformat()
        return result


@dataclass
class FailureNotification:
    """Represents a failure notification."""
    id: str
    timestamp: datetime
    source: str  # github, gitlab, jenkins, etc.
    repository: str
    branch: str
    commit_sha: str
    failure_summary: Dict[str, Any]
    notification_channels: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result