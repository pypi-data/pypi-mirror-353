"""
Task module.

This module defines the Task and related models for task management.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Dict, Any
from pathlib import Path

class TaskStatus(Enum):
    """Enum representing the status of a task."""
    TODO = auto()
    IN_PROGRESS = auto()
    IN_REVIEW = auto()
    COMPLETED = auto()
    BLOCKED = auto()

@dataclass
class Task:
    """Represents a task in the TaskGuard system."""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: int = 3  # 1=High, 2=Medium, 3=Low
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    progress: float = 0.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_progress(self, progress: float) -> None:
        """Update the progress of the task.
        
        Args:
            progress: Progress value between 0.0 and 1.0
        """
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the task.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary.
        
        Returns:
            Dict: Dictionary representation of the task
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.name,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'tags': self.tags,
            'progress': self.progress,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a Task from a dictionary.
        
        Args:
            data: Dictionary containing task data
            
        Returns:
            Task: New Task instance
        """
        task = cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            status=TaskStatus[data['status']],
            priority=data.get('priority', 3),
            tags=data.get('tags', []),
            progress=data.get('progress', 0.0),
            metadata=data.get('metadata', {})
        )
        return task
