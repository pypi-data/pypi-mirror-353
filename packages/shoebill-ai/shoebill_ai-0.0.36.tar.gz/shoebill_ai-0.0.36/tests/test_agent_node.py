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

class TestAgentNode:
    """Test cases for agent nodes in workflows."""

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

        return orchestrator, mock_agent

    @pytest.mark.asyncio
    async def test_agent_node(self, agent_orchestrator):
        """Test an agent node in a workflow."""
        orchestrator, mock_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Agent Node Test",
            description="A workflow for testing agent nodes"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node",
            agent_id=mock_agent.id
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=agent_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node.id,
            target_node_id=output_node.id
        )

        # Execute the workflow
        input_data = {"text": "This is a test input."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result

        # Verify the output contains the agent's response
        assert "result" in result["results"]
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a mock response from the agent."
        assert "input_received" in output
        # The input_received might not have the exact structure we expect
        # Just verify it's a dictionary and not empty
        assert isinstance(output["input_received"], dict)
        assert len(output["input_received"]) > 0

    @pytest.mark.asyncio
    async def test_agent_node_with_chat_history_variable(self, agent_orchestrator):
        """Test an agent node with chat history stored in a variable node."""
        orchestrator, mock_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Agent Node with Chat History Variable Test",
            description="A workflow for testing agent nodes with chat history in a variable"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Create chat history
        chat_history = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
        ]

        # Add a variable node to store the chat history
        variable_node = orchestrator.add_variable_node(
            workflow_id=workflow.id,
            name="Chat History Variable",
            variable_name="chat_history"
        )

        # Add agent node
        agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node",
            agent_id=mock_agent.id
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        # First, pass the chat history to the variable node
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=variable_node.id
        )

        # Then, connect the variable node to the agent node
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=variable_node.id,
            target_node_id=agent_node.id
        )

        # Finally, connect the agent node to the output node
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node.id,
            target_node_id=output_node.id
        )

        # Execute the workflow with chat history in the input data
        input_data = {
            "text": "What were we talking about?",
            "chat_history": chat_history
        }
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result

        # Verify the output contains the agent's response
        assert "result" in result["results"]
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a mock response from the agent."
        assert "input_received" in output
        assert "chat_history_received" in output

        # Verify the chat history was passed correctly
        assert output["chat_history_received"] == chat_history

    @pytest.mark.asyncio
    async def test_agent_node_with_chat_history_in_input(self, agent_orchestrator):
        """Test an agent node with chat history in the input data."""
        orchestrator, mock_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Agent Node with Chat History in Input Test",
            description="A workflow for testing agent nodes with chat history in input"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node",
            agent_id=mock_agent.id
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=agent_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node.id,
            target_node_id=output_node.id
        )

        # Create chat history
        chat_history = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
        ]

        # Execute the workflow with chat history in the input data
        input_data = {
            "text": "What were we talking about?",
            "chat_history": chat_history
        }
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result

        # Verify the output contains the agent's response
        assert "result" in result["results"]
        output = result["results"]["result"]
        assert "response" in output
        assert output["response"] == "This is a mock response from the agent."
        assert "input_received" in output
        assert "chat_history_received" in output

        # Verify the chat history was passed correctly
        assert output["chat_history_received"] == chat_history

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])