import asyncio
import sys
import os
import uuid

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
        return {
            "response": "This is a mock response from the agent.",
            "input_received": input_data
        }

class TestWorkflowValidation:
    """Test cases for workflow validation logic."""

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

    def test_valid_workflow(self, agent_orchestrator):
        """Test validation of a valid workflow."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Valid Workflow",
            description="A valid workflow for testing validation"
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
        
        # Add edges to create a valid workflow
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
        
        # Validate the workflow
        updated_workflow = orchestrator.get_workflow(workflow.id)
        try:
            updated_workflow.validate()
            validation_passed = True
        except Exception as e:
            validation_passed = False
            
        assert validation_passed, "Workflow validation should pass for a valid workflow"

    def test_workflow_with_cycle(self, agent_orchestrator):
        """Test validation of a workflow with a cycle."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Cycle",
            description="A workflow with a cycle for testing validation"
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
        
        # Add edges to create a cycle
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
            target_node_id=agent_node1.id  # This creates a cycle
        )
        
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node2.id,
            target_node_id=output_node.id
        )
        
        # Validate the workflow
        updated_workflow = orchestrator.get_workflow(workflow.id)
        with pytest.raises(ValueError, match="Workflow contains cycles"):
            updated_workflow.validate()

    def test_workflow_with_disconnected_nodes(self, agent_orchestrator):
        """Test validation of a workflow with disconnected nodes."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow with Disconnected Nodes",
            description="A workflow with disconnected nodes for testing validation"
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
            name="Agent Node 2 (Disconnected)",
            agent_id=mock_agent.id
        )
        
        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )
        
        # Add edges but leave agent_node2 disconnected
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=agent_node1.id
        )
        
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node1.id,
            target_node_id=output_node.id
        )
        
        # Validate the workflow
        updated_workflow = orchestrator.get_workflow(workflow.id)
        with pytest.raises(ValueError, match="Workflow contains disconnected nodes"):
            updated_workflow.validate()

    def test_workflow_without_input_node(self, agent_orchestrator):
        """Test validation of a workflow without an input node."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow without Input Node",
            description="A workflow without an input node for testing validation"
        )
        
        # Add nodes (no input node)
        agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node",
            agent_id=mock_agent.id
        )
        
        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )
        
        # Add edge
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node.id,
            target_node_id=output_node.id
        )
        
        # Validate the workflow
        updated_workflow = orchestrator.get_workflow(workflow.id)
        with pytest.raises(ValueError, match="Workflow must have at least one input node"):
            updated_workflow.validate()

    def test_workflow_without_output_node(self, agent_orchestrator):
        """Test validation of a workflow without an output node."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Workflow without Output Node",
            description="A workflow without an output node for testing validation"
        )
        
        # Add nodes (no output node)
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )
        
        agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node",
            agent_id=mock_agent.id
        )
        
        # Add edge
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=agent_node.id
        )
        
        # Validate the workflow
        updated_workflow = orchestrator.get_workflow(workflow.id)
        with pytest.raises(ValueError, match="Workflow must have at least one output node"):
            updated_workflow.validate()

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])