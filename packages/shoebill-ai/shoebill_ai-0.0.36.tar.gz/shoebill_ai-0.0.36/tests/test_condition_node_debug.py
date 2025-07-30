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
        print(f"MockTextAgent.process called with input_data: {input_data}")
        return {
            "response": "This is a mock response from the agent.",
            "input_received": input_data
        }

def mock_function(input_data):
    """A mock function that returns a known result."""
    print(f"mock_function called with input_data: {input_data}")
    return {
        "response": "This is a response from the mock function.",
        "input_received": input_data
    }

@pytest.fixture
def agent_orchestrator():
    """Create and return an agent orchestrator with a mock agent and functions."""
    orchestrator = AgentOrchestrator(api_url="http://localhost:11434")

    # Create a mock text agent
    mock_agent = MockTextAgent(
        agent_id=str(uuid.uuid4()),
        name="Mock Text Agent",
        description="A mock agent for workflow testing"
    )

    # Register the mock agent with the agent registry
    orchestrator.agent_registry.register(mock_agent)

    # Register mock functions
    orchestrator.register_function(
        function=mock_function,
        function_id="mock_function",
        name="Mock Function",
        description="A mock function for workflow testing"
    )

    return orchestrator, mock_agent

@pytest.mark.asyncio
async def test_condition_node_debug(agent_orchestrator):
    """Test a condition node in a workflow with debug logging."""
    orchestrator, mock_agent = agent_orchestrator

    # Create a new workflow
    workflow = orchestrator.create_workflow(
        name="Condition Node Debug Test",
        description="A workflow for debugging condition nodes"
    )

    # Add nodes
    input_node = orchestrator.add_input_node(
        workflow_id=workflow.id,
        name="Input Node"
    )

    # Add a condition node that checks if the input text equals a specific value
    condition_node = orchestrator.add_condition_node(
        workflow_id=workflow.id,
        name="Condition Node",
        condition="== This is a test input.",
        value_type="string"
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

    # Update the condition node to include the true and false branches
    workflow = orchestrator.get_workflow(workflow.id)
    condition_node = workflow.nodes[condition_node.id]
    condition_node.config['true_branch'] = [agent_node_true.id]
    condition_node.config['false_branch'] = [function_node_false.id]
    print(f"Condition node config: {condition_node.config}")
    orchestrator.workflow_service.update_workflow(workflow)

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
    print(f"Executing workflow with input_data: {input_data}")
    result = await orchestrator.execute_workflow(
        workflow_id=workflow.id,
        input_data=input_data
    )

    # Print the execution result
    print(f"Execution result: {result}")
    
    # Verify the execution result
    assert result is not None
    assert result["status"] == "completed"
    assert "results" in result
    assert "result" in result["results"]

    # The condition should be true, so the agent node should have been executed
    output = result["results"]["result"]
    print(f"Output: {output}")
    assert "response" in output
    # The response should be from the agent
    assert output["response"] == "This is a mock response from the agent."

    # Execute the workflow with input that doesn't match the condition
    input_data = {"text": "This is a different input."}
    print(f"Executing workflow with input_data: {input_data}")
    result = await orchestrator.execute_workflow(
        workflow_id=workflow.id,
        input_data=input_data
    )

    # Print the execution result
    print(f"Execution result: {result}")
    
    # Verify the execution result
    assert result is not None
    assert result["status"] == "completed"
    assert "results" in result
    assert "result" in result["results"]

    # The condition should be false, so the function node should have been executed
    output = result["results"]["result"]
    print(f"Output: {output}")
    assert "response" in output
    assert output["response"] == "This is a response from the mock function."

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])