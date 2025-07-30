import asyncio
import sys
import os
import uuid
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from shoebill_ai.application.workflows.agent_orchestrator import AgentOrchestrator
from shoebill_ai.domain.agents.text_agent import TextAgent
from shoebill_ai.domain.workflows.workflow import Workflow
from shoebill_ai.domain.workflows.workflow_node import WorkflowNode, NodeType
from shoebill_ai.domain.workflows.workflow_edge import WorkflowEdge
from shoebill_ai.domain.workflows.workflow_execution_context import WorkflowExecutionContext

class ErrorTextAgent(TextAgent):
    """A text agent that raises an error when processed."""

    def process(self, input_data, context=None):
        """Override the process method to raise an error."""
        raise ValueError("This agent always fails")

class TestWorkflowErrorHandlingNoFallback:
    """Test cases for workflow error handling without fallback."""

    @pytest.fixture
    def agent_orchestrator(self):
        """Create and return an agent orchestrator with various agents."""
        orchestrator = AgentOrchestrator(api_url="http://localhost:11434")

        # Create an error text agent
        error_agent = ErrorTextAgent(
            agent_id=str(uuid.uuid4()),
            name="Error Text Agent",
            description="An agent that always raises an error"
        )

        # Register the agent with the agent registry
        orchestrator.agent_registry.register(error_agent)

        return orchestrator, error_agent

    @pytest.mark.asyncio
    async def test_workflow_with_error_no_handling(self, agent_orchestrator):
        """Test a workflow with an error where errors don't need to be handled and no fallback is done."""
        orchestrator, error_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Error No Handling",
            description="A workflow with an error that is not handled"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add error agent node with explicit configuration to not handle errors
        error_agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Error Agent Node",
            agent_id=error_agent.id,
            config={
                "error_handling": {
                    "strategy": "fail",  # Explicitly set to fail
                    "handle_errors": False  # Explicitly set to not handle errors
                }
            }
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=error_agent_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=error_agent_node.id,
            target_node_id=output_node.id
        )

        # Execute the workflow and expect it to fail
        input_data = {"text": "This is a test input."}

        with pytest.raises(ValueError, match="This agent always fails"):
            await orchestrator.execute_workflow(
                workflow_id=workflow.id,
                input_data=input_data
            )

        # Get the execution status to verify it failed
        executions = orchestrator.list_executions(workflow_id=workflow.id)
        assert len(executions) > 0

        # Get the most recent execution
        execution_id = list(executions.keys())[0]
        execution_status = orchestrator.get_execution_status(execution_id)

        assert execution_status is not None
        assert execution_status["status"] == "failed"
        assert "error_nodes" in execution_status
        assert error_agent_node.id in execution_status["error_nodes"]

        # Verify that the error was not handled (no fallback was done)
        workflow_context = orchestrator.workflow_service.execution_engine._executions.get(execution_id)
        assert workflow_context is not None
        
        # Check if the error node has a result (it shouldn't if no fallback was done)
        error_node_result = workflow_context.node_results.get(error_agent_node.id, None)
        
        # If the error was not handled, there should be no result for the error node
        # or the result should indicate an error without a fallback value
        if error_node_result is not None:
            assert "_error" in error_node_result
            assert "fallback_applied" not in error_node_result or not error_node_result["fallback_applied"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])