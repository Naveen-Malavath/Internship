"""Task decomposition and planning."""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class SubTask:
    """Represents a subtask in a plan."""
    id: str
    description: str
    tool: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # IDs of tasks that must complete first
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def can_execute(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are satisfied.
        
        Args:
            completed_tasks: Set of completed task IDs
            
        Returns:
            True if task can be executed
        """
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'description': self.description,
            'tool': self.tool,
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'status': self.status.value,
            'result': self.result,
            'error': self.error
        }


@dataclass
class TaskPlan:
    """Represents a complete task execution plan."""
    goal: str
    subtasks: List[SubTask]
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    
    def get_executable_tasks(self) -> List[SubTask]:
        """Get all tasks that can be executed now (dependencies satisfied).
        
        Returns:
            List of subtasks ready for execution
        """
        executable = []
        for task in self.subtasks:
            if (task.status == TaskStatus.PENDING and 
                task.can_execute(self.completed_tasks) and
                task.id not in self.failed_tasks):
                executable.append(task)
        return executable
    
    def get_parallel_tasks(self) -> List[SubTask]:
        """Get tasks that can be executed in parallel (no dependencies between them).
        
        Returns:
            List of independent subtasks
        """
        executable = self.get_executable_tasks()
        
        # Group by independence - tasks are parallel if they don't depend on each other
        parallel_tasks = []
        task_ids = {task.id for task in executable}
        
        for task in executable:
            # Check if any of its dependencies are in the executable set
            has_dependency_in_group = any(dep in task_ids for dep in task.dependencies)
            if not has_dependency_in_group:
                parallel_tasks.append(task)
        
        return parallel_tasks
    
    def mark_completed(self, task_id: str, result: Optional[Dict[str, Any]] = None):
        """Mark a task as completed.
        
        Args:
            task_id: Task ID
            result: Optional task result
        """
        for task in self.subtasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED
                task.result = result
                self.completed_tasks.add(task_id)
                logger.info(f"✓ Task completed: {task.description}")
                break
    
    def mark_failed(self, task_id: str, error: str):
        """Mark a task as failed.
        
        Args:
            task_id: Task ID
            error: Error message
        """
        for task in self.subtasks:
            if task.id == task_id:
                task.status = TaskStatus.FAILED
                task.error = error
                self.failed_tasks.add(task_id)
                logger.error(f"✗ Task failed: {task.description} - {error}")
                break
    
    def mark_in_progress(self, task_id: str):
        """Mark a task as in progress.
        
        Args:
            task_id: Task ID
        """
        for task in self.subtasks:
            if task.id == task_id:
                task.status = TaskStatus.IN_PROGRESS
                logger.info(f"⚙ Task started: {task.description}")
                break
    
    def is_complete(self) -> bool:
        """Check if all tasks are completed or failed.
        
        Returns:
            True if plan is complete
        """
        return all(
            task.status in {TaskStatus.COMPLETED, TaskStatus.FAILED}
            for task in self.subtasks
        )
    
    def get_progress(self) -> Dict[str, int]:
        """Get execution progress.
        
        Returns:
            Dictionary with counts of tasks in each status
        """
        progress = {
            'total': len(self.subtasks),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'pending': sum(1 for t in self.subtasks if t.status == TaskStatus.PENDING),
            'in_progress': sum(1 for t in self.subtasks if t.status == TaskStatus.IN_PROGRESS)
        }
        progress['percentage'] = int((progress['completed'] / progress['total']) * 100) if progress['total'] > 0 else 0
        return progress
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            'goal': self.goal,
            'subtasks': [task.to_dict() for task in self.subtasks],
            'progress': self.get_progress()
        }


class TaskPlanner:
    """Plans and decomposes complex tasks."""
    
    def __init__(self):
        """Initialize task planner."""
        logger.debug("Initialized TaskPlanner")
    
    def create_plan(self, goal: str, llm_response: str) -> Optional[TaskPlan]:
        """Create a task plan from LLM response.
        
        This is a simple implementation. In production, you'd use the LLM
        to generate a structured plan.
        
        Args:
            goal: The overall goal
            llm_response: LLM's response with tool calls
            
        Returns:
            TaskPlan if plan can be created
        """
        # For now, return None - let orchestrator handle tool calls directly
        # This can be enhanced to parse LLM responses and create structured plans
        return None
    
    def create_manual_plan(self, goal: str, subtasks: List[Dict[str, Any]]) -> TaskPlan:
        """Create a task plan manually.
        
        Args:
            goal: Overall goal
            subtasks: List of subtask dictionaries with keys: id, description, tool, parameters, dependencies
            
        Returns:
            TaskPlan object
        """
        tasks = []
        for st in subtasks:
            task = SubTask(
                id=st.get('id', f"task_{len(tasks)}"),
                description=st['description'],
                tool=st.get('tool'),
                parameters=st.get('parameters', {}),
                dependencies=st.get('dependencies', [])
            )
            tasks.append(task)
        
        plan = TaskPlan(goal=goal, subtasks=tasks)
        logger.info(f"Created plan with {len(tasks)} subtasks for: {goal}")
        return plan
