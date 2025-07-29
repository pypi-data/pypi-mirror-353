"""
Task Controller module.

This module provides the main TaskController class which manages tasks,
enforces focus, and handles the overall workflow of the TaskGuard system.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging

from taskguard.core.task import Task, TaskStatus
from taskguard.core.project import Project
from taskguard.llm.interface import LLMInterface
from taskguard.security.validator import SecurityValidator

logger = logging.getLogger(__name__)

@dataclass
class TaskController:
    """Main controller for managing tasks and enforcing best practices."""
    
    project: Project
    llm: LLMInterface
    security_validator: SecurityValidator
    current_task: Optional[Task] = None
    task_history: List[Task] = field(default_factory=list)
    
    def start_task(self, task_id: str) -> bool:
        """Start working on a specific task.
        
        Args:
            task_id: ID of the task to start
            
        Returns:
            bool: True if task was started successfully, False otherwise
        """
        task = self.project.get_task(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return False
            
        if self.current_task and self.current_task.status == TaskStatus.IN_PROGRESS:
            logger.warning(f"Already working on task {self.current_task.id}")
            return False
            
        self.current_task = task
        self.current_task.status = TaskStatus.IN_PROGRESS
        logger.info(f"Started task: {task.title} ({task.id})")
        return True
    
    def complete_task(self) -> bool:
        """Mark the current task as completed.
        
        Returns:
            bool: True if task was completed successfully, False otherwise
        """
        if not self.current_task:
            logger.warning("No active task to complete")
            return False
            
        self.current_task.status = TaskStatus.COMPLETED
        self.task_history.append(self.current_task)
        logger.info(f"Completed task: {self.current_task.title}")
        self.current_task = None
        return True
    
    def check_best_practices(self, file_path: Path) -> Dict:
        """Check a file against best practices.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            Dict: Dictionary containing check results and recommendations
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {"error": "File not found"}
            
        # Use LLM to analyze the file
        analysis = self.llm.analyze_code(file_path)
        
        # Validate security concerns
        security_issues = self.security_validator.validate(analysis.get('code', ''))
        
        return {
            'best_practices': analysis.get('best_practices', []),
            'security_issues': security_issues,
            'suggestions': analysis.get('suggestions', [])
        }
    
    def get_task_status(self) -> Dict:
        """Get the status of the current task.
        
        Returns:
            Dict: Dictionary containing task status information
        """
        if not self.current_task:
            return {"status": "idle", "current_task": None}
            
        return {
            "status": "active",
            "current_task": {
                "id": self.current_task.id,
                "title": self.current_task.title,
                "status": self.current_task.status.value,
                "progress": self.current_task.progress
            }
        }
