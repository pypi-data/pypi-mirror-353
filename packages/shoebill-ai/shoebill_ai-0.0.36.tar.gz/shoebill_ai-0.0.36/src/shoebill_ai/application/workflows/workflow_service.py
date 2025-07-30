from typing import Dict, List, Any, Optional, Type
import uuid

from ...domain.workflows.interfaces.workflow_repository import WorkflowRepository
from ...domain.workflows.workflow import Workflow
from ...domain.workflows.workflow_node import WorkflowNode, NodeType
from ...domain.workflows.workflow_edge import WorkflowEdge
from ...domain.workflows.interfaces.workflow_execution_engine import WorkflowExecutionEngine
from ...domain.workflows.node_io_registry import NodeIORegistry
from ...domain.agents.base_agent import BaseAgent


class WorkflowService:
    """
    Application service for managing workflows.

    This service provides high-level operations for creating, updating, and executing workflows.
    """

    def __init__(self, 
                 workflow_repository: WorkflowRepository,
                 execution_engine: WorkflowExecutionEngine):
        """
        Initialize the workflow service.

        Args:
            workflow_repository: Repository for storing and retrieving workflows
            execution_engine: Engine for executing workflows
        """
        self.workflow_repository = workflow_repository
        self.execution_engine = execution_engine

    def create_workflow(self, name: str, description: Optional[str] = None, parent_workflow_id: Optional[str] = None) -> Workflow:
        """
        Create a new workflow.

        Args:
            name: The name of the workflow
            description: Optional description of the workflow
            parent_workflow_id: Optional ID of the parent workflow (for subworkflows)

        Returns:
            The created workflow
        """
        workflow = Workflow.create(name, description, parent_workflow_id)
        self.workflow_repository.save(workflow)
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by its ID.

        Args:
            workflow_id: The ID of the workflow to retrieve

        Returns:
            The workflow if found, None otherwise
        """
        return self.workflow_repository.get(workflow_id)

    def update_workflow(self, workflow: Workflow) -> None:
        """
        Update a workflow.

        Args:
            workflow: The workflow to update
        """
        self.workflow_repository.save(workflow)

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.

        Args:
            workflow_id: The ID of the workflow to delete

        Returns:
            True if the workflow was deleted, False otherwise
        """
        return self.workflow_repository.delete(workflow_id)

    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all workflows.

        Returns:
            Dict mapping workflow IDs to workflow metadata
        """
        return self.workflow_repository.list_workflows()

    def add_node(self, 
                 workflow_id: str, 
                 name: str, 
                 node_type: NodeType, 
                 config: Dict[str, Any] = None,
                 description: Optional[str] = None) -> Optional[WorkflowNode]:
        """
        Add a node to a workflow.

        Args:
            workflow_id: The ID of the workflow
            name: The name of the node
            node_type: The type of the node (must be one of: AGENT, FUNCTION, INPUT, OUTPUT)
            config: Optional configuration for the node
            description: Optional description of the node

        Returns:
            The created node if successful, None otherwise
        """
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            return None

        # All node types are now supported
        # This includes AGENT, FUNCTION, INPUT, OUTPUT, CONDITION, FOREACH, LOOP, and SUBWORKFLOW

        node = WorkflowNode(
            node_id=str(uuid.uuid4()),
            name=name,
            node_type=node_type,
            description=description,
            config=config or {}
        )

        workflow.add_node(node)
        self.workflow_repository.save(workflow)

        return node

    def add_edge(self, 
                 workflow_id: str, 
                 source_node_id: str, 
                 target_node_id: str,
                 source_output: Optional[str] = None,
                 target_input: Optional[str] = None) -> Optional[WorkflowEdge]:
        """
        Add an edge to a workflow.

        Args:
            workflow_id: The ID of the workflow
            source_node_id: The ID of the source node
            target_node_id: The ID of the target node
            source_output: Optional name of the output from the source node
            target_input: Optional name of the input to the target node

        Returns:
            The created edge if successful, None otherwise
        """
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            return None

        # Verify that the source and target nodes exist
        if source_node_id not in workflow.nodes:
            raise ValueError(f"Source node {source_node_id} does not exist in the workflow")
        if target_node_id not in workflow.nodes:
            raise ValueError(f"Target node {target_node_id} does not exist in the workflow")

        source_node = workflow.nodes[source_node_id]
        target_node = workflow.nodes[target_node_id]

        # Determine default source output if not provided
        if source_output is None:
            # Get the output schema for the source node
            output_schema = source_node.get_output_schema()

            # If there's only one output in the schema, use it
            if len(output_schema) == 1:
                source_output = next(iter(output_schema.keys()))
            else:
                # Otherwise use the default from the registry
                # For simplicity, we're not determining the agent type
                source_output = NodeIORegistry.get_default_output_key(source_node.node_type)

        # Determine default target input if not provided
        if target_input is None:
            # Get the input schema for the target node
            input_schema = target_node.get_input_schema()

            # If there's only one input in the schema, use it
            if len(input_schema) == 1:
                target_input = next(iter(input_schema.keys()))
            else:
                # Otherwise use the default from the registry
                # For simplicity, we're not determining the agent type
                target_input = NodeIORegistry.get_default_input_key(target_node.node_type)

        edge = WorkflowEdge(
            edge_id=str(uuid.uuid4()),
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            source_output=source_output,
            target_input=target_input
        )

        workflow.add_edge(edge)
        self.workflow_repository.save(workflow)

        return edge

    def remove_node(self, workflow_id: str, node_id: str) -> bool:
        """
        Remove a node from a workflow.

        Args:
            workflow_id: The ID of the workflow
            node_id: The ID of the node to remove

        Returns:
            True if the node was removed, False otherwise
        """
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            return False

        if node_id not in workflow.nodes:
            return False

        workflow.remove_node(node_id)
        self.workflow_repository.save(workflow)

        return True

    def remove_edge(self, workflow_id: str, edge_id: str) -> bool:
        """
        Remove an edge from a workflow.

        Args:
            workflow_id: The ID of the workflow
            edge_id: The ID of the edge to remove

        Returns:
            True if the edge was removed, False otherwise
        """
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            return False

        if edge_id not in workflow.edges:
            return False

        workflow.remove_edge(edge_id)
        self.workflow_repository.save(workflow)

        return True

    def validate_workflow(self, workflow_id: str) -> List[str]:
        """
        Validate a workflow.

        Args:
            workflow_id: The ID of the workflow to validate

        Returns:
            List of validation errors, empty if the workflow is valid
        """
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            return ["Workflow not found"]

        try:
            workflow.validate()
            return []  # No errors if validation passes
        except ValueError as e:
            # Convert the exception message to a list of errors
            return [str(e)]

    async def execute_workflow(self, 
                         workflow_id: str, 
                         input_data: Dict[str, Any] = None,
                         max_iterations: int = 100) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: The ID of the workflow to execute
            input_data: Optional input data for the workflow
            max_iterations: Maximum number of iterations to prevent infinite loops

        Returns:
            Dict[str, Any]: The execution results containing:
                - execution_id: The unique ID of this execution
                - status: The execution status (completed, failed, or cancelled)
                - results: The workflow output values from output nodes
                - summary: A summary of the execution including timing information

        Raises:
            ValueError: If the workflow is not found
        """
        workflow = self.workflow_repository.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Validate the workflow before execution
        try:
            workflow.validate()
        except ValueError as e:
            raise ValueError(f"Workflow validation failed: {str(e)}")

        return await self.execution_engine.execute_workflow(workflow, input_data, max_iterations)

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution.

        Args:
            execution_id: The ID of the execution

        Returns:
            Optional[Dict[str, Any]]: The execution status containing:
                - execution_id: The unique ID of this execution
                - workflow_id: The ID of the workflow that was executed
                - status: The execution status (completed, failed, or cancelled)
                - start_time: The time when execution started
                - end_time: The time when execution ended (or None if still running)
                - execution_time: The total execution time in seconds
                - current_node_id: The ID of the currently executing node (if active)
                - execution_path: The sequence of nodes that were executed
                - error_count: The number of errors that occurred during execution
                - has_errors: Whether any errors occurred during execution
                - is_active: Whether the execution is still active
            Returns None if the execution is not found.
        """
        return self.execution_engine.get_execution_status(execution_id)

    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running workflow execution.

        Args:
            execution_id: The ID of the execution to cancel

        Returns:
            True if the execution was cancelled, False otherwise
        """
        return self.execution_engine.cancel_execution(execution_id)

    def list_executions(self, workflow_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all executions, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping execution IDs to execution summaries.
            Each summary contains:
                - execution_id: The unique ID of the execution
                - workflow_id: The ID of the workflow that was executed
                - status: The execution status (completed, failed, or cancelled)
                - start_time: The time when execution started
                - end_time: The time when execution ended (or None if still running)
                - execution_time: The total execution time in seconds
                - is_active: Whether the execution is still active
        """
        return self.execution_engine.list_executions(workflow_id)
