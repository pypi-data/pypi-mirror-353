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
from shoebill_ai.infrastructure.workflows.advanced_workflow_execution_engine import AdvancedWorkflowExecutionEngine

class MockTextAgent(TextAgent):
    """A mock text agent that returns a known result."""

    def process(self, input_data, context=None):
        """Override the process method to return a known result."""
        return {
            "response": "This is a mock response from the agent.",
            "input_received": input_data
        }

class TestWorkflowExecutionEngine:
    """Test cases for the workflow execution engine."""

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
        
        # Register the mock agent with the agent registry
        orchestrator.agent_registry.register(mock_agent)
        
        return orchestrator, mock_agent

    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self, agent_orchestrator):
        """Test execution of a simple workflow with input -> agent -> output."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Simple Workflow",
            description="A simple workflow for testing execution"
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
        assert "execution_id" in result
        assert "summary" in result
        
        # Verify the output contains the agent's response
        assert "result" in result["results"]
        agent_output = result["results"]["result"]
        assert "response" in agent_output
        assert agent_output["response"] == "This is a mock response from the agent."
        assert "input_received" in agent_output
        assert agent_output["input_received"]["text"] == "This is a test input."

    @pytest.mark.asyncio
    async def test_multi_agent_workflow_execution(self, agent_orchestrator):
        """Test execution of a workflow with multiple agents in sequence."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Multi-Agent Workflow",
            description="A workflow with multiple agents for testing execution"
        )
        
        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )
        
        agent_node1 = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node 1",
            agent_id=mock_agent.id
        )
        
        agent_node2 = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node 2",
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
            target_node_id=agent_node1.id
        )
        
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node1.id,
            target_node_id=agent_node2.id
        )
        
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node2.id,
            target_node_id=output_node.id
        )
        
        # Execute the workflow
        input_data = {"text": "This is a test input for multiple agents."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )
        
        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "execution_id" in result
        assert "summary" in result
        
        # Verify the output contains the agent's response
        assert "result" in result["results"]
        agent_output = result["results"]["result"]
        assert "response" in agent_output
        assert agent_output["response"] == "This is a mock response from the agent."
        assert "input_received" in agent_output
        
        # The second agent should have received the output from the first agent
        assert "response" in agent_output["input_received"]
        assert agent_output["input_received"]["response"] == "This is a mock response from the agent."

    @pytest.mark.asyncio
    async def test_workflow_execution_with_custom_output_key(self, agent_orchestrator):
        """Test execution of a workflow with a custom output key."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Custom Output Key",
            description="A workflow with a custom output key for testing execution"
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
        
        # Add output node with custom output key
        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node",
            output_key="custom_result"  # Custom output key
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
        input_data = {"text": "This is a test input for custom output key."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )
        
        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        
        # Verify the output contains the agent's response with the custom key
        assert "custom_result" in result["results"]
        agent_output = result["results"]["custom_result"]
        assert "response" in agent_output
        assert agent_output["response"] == "This is a mock response from the agent."

    @pytest.mark.asyncio
    async def test_workflow_execution_with_multiple_outputs(self, agent_orchestrator):
        """Test execution of a workflow with multiple output nodes."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Multiple Outputs",
            description="A workflow with multiple output nodes for testing execution"
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
        input_data = {"text": "This is a test input for multiple outputs."}
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
        
        agent_output1 = result["results"]["result1"]
        agent_output2 = result["results"]["result2"]
        
        assert "response" in agent_output1
        assert agent_output1["response"] == "This is a mock response from the agent."
        
        assert "response" in agent_output2
        assert agent_output2["response"] == "This is a mock response from the agent."

    @pytest.mark.asyncio
    async def test_workflow_execution_context(self, agent_orchestrator):
        """Test the workflow execution context during workflow execution."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow for Context Testing",
            description="A workflow for testing execution context"
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
        input_data = {"text": "This is a test input for context testing."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )
        
        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        
        # Verify the execution summary
        assert "summary" in result
        summary = result["summary"]
        
        assert "execution_time" in summary
        assert summary["execution_time"] > 0
        
        assert "node_execution_times" in summary
        assert len(summary["node_execution_times"]) == 3  # Input, agent, and output nodes
        
        assert "execution_path" in summary
        assert len(summary["execution_path"]) == 3  # Input, agent, and output nodes
        
        # Verify the execution path order
        execution_path = summary["execution_path"]
        assert execution_path[0] == input_node.id
        assert execution_path[1] == agent_node.id
        assert execution_path[2] == output_node.id

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])