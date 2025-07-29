"""
Project module.

This module defines the Project class which represents a TaskGuard project.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml
import json
import logging

from taskguard.core.task import Task, TaskStatus

logger = logging.getLogger(__name__)

@dataclass
class Project:
    """Represents a TaskGuard project."""
    
    name: str
    root_dir: Path
    tasks: Dict[str, Task] = field(default_factory=dict)
    config: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize project directory structure."""
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir = self.root_dir / 'tasks'
        self.tasks_dir.mkdir(exist_ok=True)
        self.config_file = self.root_dir / 'config.yaml'
        
        # Load config if exists
        if self.config_file.exists():
            self._load_config()
    
    def _load_config(self) -> None:
        """Load project configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {}
    
    def save_config(self) -> bool:
        """Save project configuration to file.
        
        Returns:
            bool: True if config was saved successfully, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def add_task(self, task: Task) -> bool:
        """Add a task to the project.
        
        Args:
            task: Task to add
            
        Returns:
            bool: True if task was added successfully, False otherwise
        """
        if task.id in self.tasks:
            logger.warning(f"Task with ID {task.id} already exists")
            return False
            
        self.tasks[task.id] = task
        return self._save_task(task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Optional[Task]: The task if found, None otherwise
        """
        if task_id in self.tasks:
            return self.tasks[task_id]
        
        # Try to load from disk
        task_file = self.tasks_dir / f"{task_id}.json"
        if task_file.exists():
            try:
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                    task = Task.from_dict(task_data)
                    self.tasks[task_id] = task
                    return task
            except Exception as e:
                logger.error(f"Failed to load task {task_id}: {e}")
                
        return None
    
    def update_task(self, task: Task) -> bool:
        """Update a task in the project.
        
        Args:
            task: Task to update
            
        Returns:
            bool: True if task was updated successfully, False otherwise
        """
        if task.id not in self.tasks:
            logger.warning(f"Task with ID {task.id} does not exist")
            return False
            
        self.tasks[task.id] = task
        return self._save_task(task)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task from the project.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            bool: True if task was deleted successfully, False otherwise
        """
        if task_id not in self.tasks:
            logger.warning(f"Task with ID {task_id} does not exist")
            return False
            
        # Delete from memory
        del self.tasks[task_id]
        
        # Delete from disk
        task_file = self.tasks_dir / f"{task_id}.json"
        if task_file.exists():
            try:
                task_file.unlink()
                return True
            except Exception as e:
                logger.error(f"Failed to delete task file {task_file}: {e}")
                return False
        
        return True
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """List all tasks, optionally filtered by status.
        
        Args:
            status: Optional status to filter by
            
        Returns:
            List[Task]: List of tasks matching the filter
        """
        tasks = list(self.tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return tasks
    
    def _save_task(self, task: Task) -> bool:
        """Save a task to disk.
        
        Args:
            task: Task to save
            
        Returns:
            bool: True if task was saved successfully, False otherwise
        """
        task_file = self.tasks_dir / f"{task.id}.json"
        try:
            with open(task_file, 'w') as f:
                json.dump(task.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save task {task.id}: {e}")
            return False
