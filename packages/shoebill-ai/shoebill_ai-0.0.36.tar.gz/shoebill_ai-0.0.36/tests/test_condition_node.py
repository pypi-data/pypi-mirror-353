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

class MockTextAgent(TextAgent):
    """A mock text agent that returns a known result."""

    def process(self, input_data, context=None):
        """Override the process method to return a known result."""
        # Ensure input_data has the expected structure
        if not isinstance(input_data, dict):
            # If input_data doesn't have the expected structure, use the original input data from the context
            if context and isinstance(context, dict) and "input_data" in context:
                input_data = context["input_data"]

        # Handle nested input structure (e.g., {'input': {'text': '...', 'chat_history': [...]}})
        if 'input' in input_data and isinstance(input_data['input'], dict):
            nested_input = input_data['input']
            # Check if chat_history is in the nested input
            if 'chat_history' in nested_input:
                chat_history = nested_input['chat_history']
            else:
                chat_history = []
        else:
            # Check if chat_history is provided at the top level
            chat_history = input_data.get('chat_history', [])

        # Include chat_history in the response if it exists
        response = {
            "response": "This is a mock response from the agent.",
            "input_received": input_data
        }

        if chat_history:
            response["chat_history_received"] = chat_history

        return response

def mock_function(input_data):
    """A mock function that returns a known result."""
    # Ensure input_data has the expected structure
    if not isinstance(input_data, dict) or "text" not in input_data:
        # If input_data doesn't have the expected structure, use a default value
        input_data = {"text": "This is a test input."}

    return {
        "response": "This is a response from the mock function.",
        "input_received": input_data
    }

class TestConditionNode:
    """Test cases for condition nodes in workflows."""

    @pytest.fixture
    def agent_orchestrator(self):
        """Create and return an agent orchestrator with a mock agent."""
        orchestrator = AgentOrchestrator(api_url="http://localhost:11434")

        # Create a mock text agent
        mock_agent = MockTextAgent(
            agent_id=str(uuid.uuid4()),
            name="Mock Text Agent",
            description="A mock agent for workflow testing"
        )

        # Register the agent with the agent registry
        orchestrator.agent_registry.register(mock_agent)

        # Register the mock function
        orchestrator.function_registry.register("mock_function", mock_function)

        return orchestrator, mock_agent

    @pytest.mark.asyncio
    async def test_condition_node(self, agent_orchestrator):
        """Test a condition node in a workflow."""
        orchestrator, mock_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Condition Node Test",
            description="A workflow for testing condition nodes"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add nodes for true and false branches
        agent_node_true = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node (True Branch)",
            agent_id=mock_agent.id
        )

        function_node_false = orchestrator.add_function_node(
            workflow_id=workflow.id,
            name="Function Node (False Branch)",
            function_id="mock_function"
        )

        # Add a condition node that checks if the input text equals a specific value
        # and directly specify the true and false branches
        condition_node = orchestrator.add_condition_node(
            workflow_id=workflow.id,
            name="Condition Node",
            condition="== This is a test input.",
            value_type="string",
            true_branch=[agent_node_true.id],
            false_branch=[function_node_false.id]
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=condition_node.id
        )

        # The condition node already includes the true and false branches

        # Add edges from condition node to branch nodes
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=condition_node.id,
            target_node_id=agent_node_true.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=condition_node.id,
            target_node_id=function_node_false.id
        )

        # Add edges from branch nodes to output
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node_true.id,
            target_node_id=output_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=function_node_false.id,
            target_node_id=output_node.id
        )

        # Execute the workflow with input that matches the condition
        input_data = {"text": "This is a test input."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The condition should be true, so the agent node should have been executed
        output = result["results"]["result"]
        assert "response" in output
        # The response should be from the agent
        assert output["response"] == "This is a mock response from the agent."

        # Execute the workflow with input that doesn't match the condition
        input_data = {"text": "This is a different input."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The condition should be false, so the function node should have been executed
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a response from the mock function."

    @pytest.mark.asyncio
    async def test_condition_node_with_multiple_inputs(self, agent_orchestrator):
        """Test a condition node with multiple inputs in a workflow."""
        orchestrator, mock_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Condition Node Multiple Inputs Test",
            description="A workflow for testing condition nodes with multiple inputs"
        )

        # Add nodes
        input_node1 = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node 1"
        )

        input_node2 = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node 2"
        )

        # Add nodes for true and false branches
        agent_node_true = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node (True Branch)",
            agent_id=mock_agent.id
        )

        function_node_false = orchestrator.add_function_node(
            workflow_id=workflow.id,
            name="Function Node (False Branch)",
            function_id="mock_function"
        )

        # Add a condition node that compares values from two different inputs
        # and directly specify the true and false branches
        condition_node = orchestrator.add_condition_node(
            workflow_id=workflow.id,
            name="Condition Node",
            condition="==",
            value_type="string",
            true_branch=[agent_node_true.id],
            false_branch=[function_node_false.id]
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node1.id,
            target_node_id=condition_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node2.id,
            target_node_id=condition_node.id
        )

        # The condition node already includes the true and false branches

        # Add edges from condition node to branch nodes
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=condition_node.id,
            target_node_id=agent_node_true.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=condition_node.id,
            target_node_id=function_node_false.id
        )

        # Add edges from branch nodes to output
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node_true.id,
            target_node_id=output_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=function_node_false.id,
            target_node_id=output_node.id
        )

        # Execute the workflow with inputs that match the condition
        input_data = {"value1": "test", "value2": "test"}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The condition should be true, so the agent node should have been executed
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a mock response from the agent."

        # Execute the workflow with inputs that don't match the condition
        input_data = {"value1": "test", "value2": "different"}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The condition should be false, so the function node should have been executed
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a response from the mock function."

    @pytest.mark.asyncio
    async def test_condition_node_with_numerical_values(self, agent_orchestrator):
        """Test a condition node with numerical values in a workflow."""
        orchestrator, mock_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Condition Node Numerical Test",
            description="A workflow for testing condition nodes with numerical values"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add nodes for true and false branches
        agent_node_true = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node (True Branch)",
            agent_id=mock_agent.id
        )

        function_node_false = orchestrator.add_function_node(
            workflow_id=workflow.id,
            name="Function Node (False Branch)",
            function_id="mock_function"
        )

        # Add a condition node that checks if the input number is greater than a specific value
        condition_node = orchestrator.add_condition_node(
            workflow_id=workflow.id,
            name="Condition Node",
            condition="> 50",
            value_type="number",
            true_branch=[agent_node_true.id],
            false_branch=[function_node_false.id],
            config={"field_name": "number"}  # Specify the field to compare
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=condition_node.id
        )

        # Add edges from condition node to branch nodes
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=condition_node.id,
            target_node_id=agent_node_true.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=condition_node.id,
            target_node_id=function_node_false.id
        )

        # Add edges from branch nodes to output
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node_true.id,
            target_node_id=output_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=function_node_false.id,
            target_node_id=output_node.id
        )

        # Execute the workflow with input that satisfies the condition (number > 50)
        input_data = {"number": 75}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The condition should be true, so the agent node should have been executed
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a mock response from the agent."

        # Execute the workflow with input that doesn't satisfy the condition (number <= 50)
        input_data = {"number": 25}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The condition should be false, so the function node should have been executed
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a response from the mock function."

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
