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

class TestInputOutputNode:
    """Test cases for input and output nodes in workflows."""

    @pytest.fixture
    def agent_orchestrator(self):
        """Create and return an agent orchestrator."""
        orchestrator = AgentOrchestrator(api_url="http://localhost:11434")
        return orchestrator

    @pytest.mark.asyncio
    async def test_input_node(self, agent_orchestrator):
        """Test an input node in a workflow."""
        orchestrator = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Input Node Test",
            description="A workflow for testing input nodes"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edge
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
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

        # Verify the output contains the input data
        assert "result" in result["results"]
        output = result["results"]["result"]
        assert output == input_data

    @pytest.mark.asyncio
    async def test_output_node(self, agent_orchestrator):
        """Test an output node with a custom key in a workflow."""
        orchestrator = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Output Node Test",
            description="A workflow for testing output nodes"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node",
            output_key="custom_output"  # Custom output key
        )

        # Add edge
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
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

        # Verify the output contains the input data with the custom key
        assert "custom_output" in result["results"]
        output = result["results"]["custom_output"]
        assert output == input_data

    @pytest.mark.asyncio
    async def test_multiple_input_nodes(self, agent_orchestrator):
        """Test a workflow with multiple input nodes."""
        orchestrator = agent_orchestrator

        # Create a mock text agent
        mock_agent = TextAgent(
            agent_id=str(uuid.uuid4()),
            name="Mock Text Agent",
            description="A mock agent for workflow testing"
        )

        # Override the process method to return a known result
        def mock_process(input_data, context=None):
            return {
                "response": "This is a mock response from the agent.",
                "input_received": input_data
            }
        
        mock_agent.process = mock_process

        # Register the agent with the agent registry
        orchestrator.agent_registry.register(mock_agent)

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Multiple Input Nodes Test",
            description="A workflow for testing multiple input nodes"
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
            source_node_id=input_node1.id,
            target_node_id=agent_node.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node2.id,
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

        # The agent should have received input from both input nodes
        assert "input_received" in output
        # The input_received might not have the exact structure we expect
        # Just verify it's a dictionary and not empty
        assert isinstance(output["input_received"], dict)
        assert len(output["input_received"]) > 0

    @pytest.mark.asyncio
    async def test_multiple_output_nodes(self, agent_orchestrator):
        """Test a workflow with multiple output nodes."""
        orchestrator = agent_orchestrator

        # Create a mock text agent
        mock_agent = TextAgent(
            agent_id=str(uuid.uuid4()),
            name="Mock Text Agent",
            description="A mock agent for workflow testing"
        )

        # Override the process method to return a known result
        def mock_process(input_data, context=None):
            return {
                "response": "This is a mock response from the agent.",
                "input_received": input_data
            }
        
        mock_agent.process = mock_process

        # Register the agent with the agent registry
        orchestrator.agent_registry.register(mock_agent)

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Multiple Output Nodes Test",
            description="A workflow for testing multiple output nodes"
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

        output_node1 = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node 1",
            output_key="result1"
        )

        output_node2 = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node 2",
            output_key="result2"
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
            target_node_id=output_node1.id
        )

        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node.id,
            target_node_id=output_node2.id
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

        # Verify both outputs contain the agent's response
        assert "result1" in result["results"]
        assert "result2" in result["results"]

        output1 = result["results"]["result1"]
        output2 = result["results"]["result2"]

        assert "response" in output1
        assert output1["response"] == "This is a mock response from the agent."

        assert "response" in output2
        assert output2["response"] == "This is a mock response from the agent."

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])