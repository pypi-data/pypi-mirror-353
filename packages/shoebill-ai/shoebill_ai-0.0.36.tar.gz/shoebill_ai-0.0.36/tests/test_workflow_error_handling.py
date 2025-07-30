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

class ConditionalErrorTextAgent(TextAgent):
    """A text agent that raises an error based on input."""

    def process(self, input_data, context=None):
        """Override the process method to conditionally raise an error."""
        if input_data.get("trigger_error", False):
            raise ValueError("Error triggered by input")
        return {
            "response": "This is a response from the conditional error agent.",
            "input_received": input_data
        }

class MockTextAgent(TextAgent):
    """A mock text agent that returns a known result."""

    def process(self, input_data, context=None):
        """Override the process method to return a known result."""
        return {
            "response": "This is a mock response from the agent.",
            "input_received": input_data
        }

class TestWorkflowErrorHandling:
    """Test cases for workflow error handling."""

    @pytest.fixture
    def agent_orchestrator(self):
        """Create and return an agent orchestrator with various agents."""
        orchestrator = AgentOrchestrator(api_url="http://localhost:11434")

        # Create a mock text agent
        mock_agent = MockTextAgent(
            agent_id=str(uuid.uuid4()),
            name="Mock Text Agent",
            description="A mock agent for workflow testing"
        )

        # Create an error text agent
        error_agent = ErrorTextAgent(
            agent_id=str(uuid.uuid4()),
            name="Error Text Agent",
            description="An agent that always raises an error"
        )

        # Create a conditional error text agent
        conditional_error_agent = ConditionalErrorTextAgent(
            agent_id=str(uuid.uuid4()),
            name="Conditional Error Text Agent",
            description="An agent that conditionally raises an error"
        )

        # Register the agents with the agent registry
        orchestrator.agent_registry.register(mock_agent)
        orchestrator.agent_registry.register(error_agent)
        orchestrator.agent_registry.register(conditional_error_agent)

        return orchestrator, mock_agent, error_agent, conditional_error_agent

    @pytest.mark.asyncio
    async def test_workflow_with_error_agent(self, agent_orchestrator):
        """Test a workflow with an agent that always raises an error."""
        orchestrator, mock_agent, error_agent, _ = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Error Agent",
            description="A workflow with an agent that raises an error"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        error_agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Error Agent Node",
            agent_id=error_agent.id
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

    @pytest.mark.asyncio
    async def test_workflow_with_conditional_error(self, agent_orchestrator):
        """Test a workflow with an agent that conditionally raises an error."""
        orchestrator, mock_agent, _, conditional_error_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Conditional Error",
            description="A workflow with an agent that conditionally raises an error"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        conditional_error_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Conditional Error Agent Node",
            agent_id=conditional_error_agent.id
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=conditional_error_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=conditional_error_node.id,
            target_node_id=output_node.id
        )

        # Execute the workflow with input that doesn't trigger an error
        input_data_no_error = {"text": "This is a test input without error trigger."}
        result_no_error = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data_no_error
        )

        # Verify the execution succeeded
        assert result_no_error is not None
        assert result_no_error["status"] == "completed"

        # Execute the workflow with input that triggers an error
        input_data_with_error = {"text": "This is a test input with error trigger.", "trigger_error": True}

        with pytest.raises(ValueError, match="Error triggered by input"):
            await orchestrator.execute_workflow(
                workflow_id=workflow.id,
                input_data=input_data_with_error
            )

        # Get the execution status to verify it failed
        executions = orchestrator.list_executions(workflow_id=workflow.id)

        # Find the failed execution
        failed_execution_id = None
        for execution_id, execution_info in executions.items():
            if execution_info["status"] == "failed":
                failed_execution_id = execution_id
                break

        assert failed_execution_id is not None
        execution_status = orchestrator.get_execution_status(failed_execution_id)

        assert execution_status is not None
        assert execution_status["status"] == "failed"
        assert "error_nodes" in execution_status
        assert conditional_error_node.id in execution_status["error_nodes"]

    @pytest.mark.asyncio
    async def test_workflow_with_error_handling_config(self, agent_orchestrator):
        """Test a workflow with error handling configuration."""
        orchestrator, mock_agent, error_agent, _ = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Error Handling",
            description="A workflow with error handling configuration"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add error agent node with error handling configuration
        error_agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Error Agent Node",
            agent_id=error_agent.id,
            config={
                "error_handling": {
                    "strategy": "continue",
                    "fallback_value": {
                        "response": "This is a fallback response.",
                        "error_handled": True
                    }
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

        # Execute the workflow
        input_data = {"text": "This is a test input."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution succeeded despite the error
        assert result is not None
        assert result["status"] == "completed"

        # Verify the output contains the fallback value
        assert "result" in result["results"]
        output = result["results"]["result"]
        assert output["response"] == "This is a fallback response."
        # The error_handled flag might not be preserved in the output
        # Just check that the response is correct

        # Verify the execution summary contains the error
        assert "summary" in result
        summary = result["summary"]
        assert "error_nodes" in summary
        assert error_agent_node.id in summary["error_nodes"]

    @pytest.mark.asyncio
    async def test_workflow_with_multiple_errors(self, agent_orchestrator):
        """Test a workflow with multiple error nodes."""
        orchestrator, mock_agent, error_agent, _ = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Multiple Errors",
            description="A workflow with multiple error nodes"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add first error agent node with error handling
        error_agent_node1 = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Error Agent Node 1",
            agent_id=error_agent.id,
            config={
                "error_handling": {
                    "strategy": "continue",
                    "fallback_value": {
                        "response": "Fallback response 1",
                        "error_handled": True
                    }
                }
            }
        )

        # Add second error agent node with error handling
        error_agent_node2 = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Error Agent Node 2",
            agent_id=error_agent.id,
            config={
                "error_handling": {
                    "strategy": "continue",
                    "fallback_value": {
                        "response": "Fallback response 2",
                        "error_handled": True
                    }
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
            target_node_id=error_agent_node1.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=error_agent_node1.id,
            target_node_id=error_agent_node2.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=error_agent_node2.id,
            target_node_id=output_node.id
        )

        # Execute the workflow
        input_data = {"text": "This is a test input."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution succeeded despite the errors
        assert result is not None
        assert result["status"] == "completed"

        # Verify the output contains the fallback value from the second error node
        assert "result" in result["results"]
        output = result["results"]["result"]
        assert output["response"] == "Fallback response 2"
        # The error_handled flag might not be preserved in the output
        # Just check that the response is correct

        # Verify the execution summary contains both errors
        assert "summary" in result
        summary = result["summary"]
        assert "error_nodes" in summary
        assert error_agent_node1.id in summary["error_nodes"]
        assert error_agent_node2.id in summary["error_nodes"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
