"""Parallel execution engine for tools."""

import asyncio
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
import time

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from src.tools.base import Tool


@dataclass
class ExecutionResult:
    """Result of a tool execution."""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tool': self.tool_name,
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'duration': self.duration
        }


class ParallelExecutor:
    """Execute multiple tool calls in parallel."""
    
    def __init__(self):
        """Initialize parallel executor."""
        self.console = Console()
        logger.debug("Initialized ParallelExecutor")
    
    async def execute_parallel(
        self,
        tool_calls: List[Dict[str, Any]],
        tool_registry: Any,
        show_progress: bool = True
    ) -> List[ExecutionResult]:
        """Execute multiple tool calls in parallel.
        
        Args:
            tool_calls: List of tool call dictionaries with 'name' and 'parameters'
            tool_registry: ToolRegistry instance
            show_progress: Whether to show progress bar
            
        Returns:
            List of execution results
        """
        if not tool_calls:
            return []
        
        logger.info(f"🚀 Executing {len(tool_calls)} tools in parallel")
        
        # Create tasks
        tasks = []
        for call in tool_calls:
            tool_name = call.get('name')
            parameters = call.get('parameters', {})
            
            task = self._execute_single(tool_name, parameters, tool_registry)
            tasks.append(task)
        
        # Execute in parallel with progress
        if show_progress and len(tool_calls) > 1:
            results = await self._execute_with_progress(tasks, tool_calls)
        else:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            results = [self._handle_exception(r, tool_calls[i]['name']) for i, r in enumerate(results)]
        
        # Log summary
        success_count = sum(1 for r in results if r.success)
        logger.info(f"✓ Completed {success_count}/{len(results)} tools successfully")
        
        return results
    
    async def _execute_single(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        tool_registry: Any
    ) -> ExecutionResult:
        """Execute a single tool call.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            tool_registry: ToolRegistry instance
            
        Returns:
            ExecutionResult
        """
        start_time = time.time()
        
        try:
            # Get tool
            tool = tool_registry.get(tool_name)
            if not tool:
                return ExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Tool not found: {tool_name}",
                    duration=time.time() - start_time
                )
            
            # Execute tool
            logger.info(f"🔍 [PARALLEL_EXECUTOR] Executing tool: {tool_name} with parameters: {parameters}")
            print(f"[DEBUG] [PARALLEL_EXECUTOR] Executing tool: {tool_name} with parameters: {parameters}")
            result = await tool.execute(**parameters)
            duration = time.time() - start_time
            
            logger.info(f"🔍 [PARALLEL_EXECUTOR] Tool {tool_name} completed. Result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
            print(f"[DEBUG] [PARALLEL_EXECUTOR] Tool {tool_name} completed. Result type: {type(result)}")
            if isinstance(result, dict):
                print(f"[DEBUG] [PARALLEL_EXECUTOR] Result keys: {list(result.keys())}")
                print(f"[DEBUG] [PARALLEL_EXECUTOR] Result success: {result.get('success')}")
                print(f"[DEBUG] [PARALLEL_EXECUTOR] Result error: {repr(result.get('error', ''))[:100]}")
            
            success = result.get('success', False)
            error = result.get('error') if not success else None
            
            logger.info(f"🔍 [PARALLEL_EXECUTOR] Tool {tool_name} - success: {success}, error: {repr(error)[:100] if error else None}")
            print(f"[DEBUG] [PARALLEL_EXECUTOR] Tool {tool_name} - success: {success}, error: {repr(error)[:100] if error else None}")
            
            return ExecutionResult(
                tool_name=tool_name,
                success=success,
                result=result,
                error=error,
                duration=duration
            )
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"🔴 [PARALLEL_EXECUTOR] Tool execution EXCEPTION: {tool_name} - {e}", exc_info=True)
            print(f"[ERROR] [PARALLEL_EXECUTOR] Tool execution EXCEPTION: {tool_name} - {e}")
            import traceback
            traceback.print_exc()
            return ExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(e),
                duration=duration
            )
    
    def _handle_exception(self, result: Any, tool_name: str) -> ExecutionResult:
        """Handle exception in task result.
        
        Args:
            result: Task result or exception
            tool_name: Name of tool
            
        Returns:
            ExecutionResult
        """
        if isinstance(result, Exception):
            return ExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(result),
                duration=0.0
            )
        return result
    
    async def _execute_with_progress(
        self,
        tasks: List[asyncio.Task],
        tool_calls: List[Dict[str, Any]]
    ) -> List[ExecutionResult]:
        """Execute tasks with rich progress bar.
        
        Args:
            tasks: List of asyncio tasks
            tool_calls: List of tool call dictionaries
            
        Returns:
            List of execution results
        """
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            # Create progress task
            task_id = progress.add_task(
                f"Executing {len(tasks)} tools in parallel...",
                total=len(tasks)
            )
            
            # Execute and collect results
            for coro in asyncio.as_completed(tasks):
                try:
                    result = await coro
                    results.append(result)
                    progress.update(task_id, advance=1)
                except Exception as e:
                    # Find which tool failed
                    tool_name = "unknown"
                    for i, t in enumerate(tasks):
                        if t == coro:
                            tool_name = tool_calls[i]['name']
                            break
                    
                    results.append(ExecutionResult(
                        tool_name=tool_name,
                        success=False,
                        result=None,
                        error=str(e),
                        duration=0.0
                    ))
                    progress.update(task_id, advance=1)
        
        return results
    
    async def execute_sequential(
        self,
        tool_calls: List[Dict[str, Any]],
        tool_registry: Any
    ) -> List[ExecutionResult]:
        """Execute tool calls sequentially (for dependent tasks).
        
        Args:
            tool_calls: List of tool call dictionaries
            tool_registry: ToolRegistry instance
            
        Returns:
            List of execution results
        """
        results = []
        
        for call in tool_calls:
            tool_name = call.get('name')
            parameters = call.get('parameters', {})
            
            logger.info(f"⚙ Executing: {tool_name}")
            result = await self._execute_single(tool_name, parameters, tool_registry)
            results.append(result)
            
            # Stop on first failure if configured
            if not result.success:
                logger.warning(f"Sequential execution stopped due to failure: {tool_name}")
                break
        
        return results
    
    def group_independent_calls(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group tool calls into batches that can be executed in parallel.
        
        Simple heuristic: Terminal calls are sequential, file operations can be parallel.
        
        Args:
            tool_calls: List of tool call dictionaries
            
        Returns:
            List of batches (each batch can be executed in parallel)
        """
        batches = []
        current_batch = []
        
        for call in tool_calls:
            tool_name = call.get('name', '')
            
            # Terminal calls should be sequential
            if tool_name == 'terminal':
                if current_batch:
                    batches.append(current_batch)
                    current_batch = []
                batches.append([call])  # Terminal call in its own batch
            else:
                current_batch.append(call)
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
