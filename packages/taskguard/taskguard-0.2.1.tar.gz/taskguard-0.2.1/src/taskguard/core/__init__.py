"""
Core functionality for the TaskGuard system.

This module contains the main controller and core functionality
for managing tasks and enforcing best practices.
"""

from taskguard.core.controller import TaskController
from taskguard.core.task import Task, TaskStatus
from taskguard.core.project import Project

__all__ = [
    'TaskController',
    'Task',
    'TaskStatus',
    'Project',
]
