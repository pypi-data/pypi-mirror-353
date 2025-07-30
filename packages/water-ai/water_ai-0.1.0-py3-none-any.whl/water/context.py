from typing import Any, Dict, Optional, List
from datetime import datetime
import uuid

from water.types import OutputData

class ExecutionContext:
    """
    Execution context passed to every task containing metadata and execution state.
    
    The context provides access to flow metadata, execution timing, task outputs,
    and execution history. It enables tasks to access data from previous steps
    and maintain state throughout the flow execution.
    """
    
    def __init__(
        self,
        flow_id: str,
        execution_id: Optional[str] = None,
        task_id: Optional[str] = None,
        step_number: int = 0,
        attempt_number: int = 1,
        flow_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize execution context.
        
        Args:
            flow_id: Unique identifier of the executing flow
            execution_id: Unique identifier for this execution instance
            task_id: Current task identifier
            step_number: Current step number in the execution
            attempt_number: Attempt number for retry scenarios
            flow_metadata: Metadata associated with the flow
        """
        self.flow_id = flow_id
        self.execution_id = execution_id or f"exec_{uuid.uuid4().hex[:8]}"
        self.task_id = task_id
        self.step_number = step_number
        self.attempt_number = attempt_number
        self.flow_metadata = flow_metadata or {}
        
        # Timing information
        self.execution_start_time = datetime.utcnow()
        self.step_start_time = datetime.utcnow()
        
        # Task outputs history
        self._task_outputs: Dict[str, OutputData] = {}
        self._step_history: List[Dict[str, Any]] = []
    
    def add_task_output(self, task_id: str, output: OutputData) -> None:
        """
        Record the output of a completed task.
        
        Args:
            task_id: Identifier of the completed task
            output: Output data from the task
        """
        self._task_outputs[task_id] = output
        
        step_info = {
            "step_number": self.step_number,
            "task_id": task_id,
            "output": output,
            "timestamp": datetime.utcnow().isoformat(),
            "attempt_number": self.attempt_number
        }
        self._step_history.append(step_info)
    
    def get_task_output(self, task_id: str) -> Optional[OutputData]:
        """
        Get the output from a previously executed task.
        
        Args:
            task_id: Identifier of the task whose output to retrieve
            
        Returns:
            Task output data, or None if task hasn't executed
        """
        return self._task_outputs.get(task_id)
    
    def get_all_task_outputs(self) -> Dict[str, OutputData]:
        """
        Get all task outputs from this execution.
        
        Returns:
            Dictionary mapping task IDs to their output data
        """
        return self._task_outputs.copy()
    
    def get_step_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete step execution history.
        
        Returns:
            List of step execution records with timestamps and outputs
        """
        return self._step_history.copy()
    
    def create_child_context(
        self, 
        task_id: str, 
        step_number: Optional[int] = None,
        attempt_number: int = 1
    ) -> 'ExecutionContext':
        """
        Create a new context for a child task execution.
        
        Inherits the current context state while updating task-specific fields.
        
        Args:
            task_id: Identifier for the child task
            step_number: Step number for the child execution
            attempt_number: Attempt number for retry scenarios
            
        Returns:
            New ExecutionContext instance for the child task
        """
        child_context = ExecutionContext(
            flow_id=self.flow_id,
            execution_id=self.execution_id,
            task_id=task_id,
            step_number=step_number or (self.step_number + 1),
            attempt_number=attempt_number,
            flow_metadata=self.flow_metadata
        )
        
        # Copy task outputs and history to child
        child_context._task_outputs = self._task_outputs.copy()
        child_context._step_history = self._step_history.copy()
        child_context.execution_start_time = self.execution_start_time
        
        return child_context
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary for serialization.
        
        Returns:
            Dictionary representation of the execution context
        """
        return {
            "flow_id": self.flow_id,
            "execution_id": self.execution_id,
            "task_id": self.task_id,
            "step_number": self.step_number,
            "attempt_number": self.attempt_number,
            "flow_metadata": self.flow_metadata,
            "execution_start_time": self.execution_start_time.isoformat(),
            "step_start_time": self.step_start_time.isoformat(),
            "task_outputs": self._task_outputs,
            "step_history": self._step_history
        }
    
    def __repr__(self) -> str:
        """String representation of the execution context."""
        return (
            f"ExecutionContext(flow_id='{self.flow_id}', "
            f"execution_id='{self.execution_id}', "
            f"task_id='{self.task_id}', "
            f"step={self.step_number}, "
            f"attempt={self.attempt_number})"
        ) 