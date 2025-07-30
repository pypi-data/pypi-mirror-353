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

class TestWorkflowCreation:
    """Test cases for workflow creation, adding nodes and edges."""

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

    def test_create_workflow(self, agent_orchestrator):
        """Test creating a workflow."""
        orchestrator, _ = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Test Workflow",
            description="A test workflow"
        )
        
        # Verify the workflow was created correctly
        assert workflow is not None
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert len(workflow.nodes) == 0
        assert len(workflow.edges) == 0
        
        # Verify the workflow can be retrieved
        retrieved_workflow = orchestrator.get_workflow(workflow.id)
        assert retrieved_workflow is not None
        assert retrieved_workflow.id == workflow.id
        assert retrieved_workflow.name == workflow.name
        assert retrieved_workflow.description == workflow.description

    def test_add_nodes(self, agent_orchestrator):
        """Test adding nodes to a workflow."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Test Workflow with Nodes",
            description="A test workflow with nodes"
        )
        
        # Add an input node
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )
        
        # Add an agent node
        agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Agent Node",
            agent_id=mock_agent.id
        )
        
        # Add an output node
        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )
        
        # Verify the nodes were added correctly
        updated_workflow = orchestrator.get_workflow(workflow.id)
        assert len(updated_workflow.nodes) == 3
        
        # Verify the node types
        nodes_by_id = {node.id: node for node in updated_workflow.nodes.values()}
        assert nodes_by_id[input_node.id].node_type == NodeType.INPUT
        assert nodes_by_id[agent_node.id].node_type == NodeType.AGENT
        assert nodes_by_id[output_node.id].node_type == NodeType.OUTPUT
        
        # Verify the node names
        assert nodes_by_id[input_node.id].name == "Input Node"
        assert nodes_by_id[agent_node.id].name == "Agent Node"
        assert nodes_by_id[output_node.id].name == "Output Node"

    def test_add_edges(self, agent_orchestrator):
        """Test adding edges to a workflow."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Test Workflow with Edges",
            description="A test workflow with edges"
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
        edge1 = orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=agent_node.id
        )
        
        edge2 = orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=agent_node.id,
            target_node_id=output_node.id
        )
        
        # Verify the edges were added correctly
        updated_workflow = orchestrator.get_workflow(workflow.id)
        assert len(updated_workflow.edges) == 2
        
        # Verify the edge connections
        edges_by_id = {edge.id: edge for edge in updated_workflow.edges.values()}
        assert edges_by_id[edge1.id].source_node_id == input_node.id
        assert edges_by_id[edge1.id].target_node_id == agent_node.id
        assert edges_by_id[edge2.id].source_node_id == agent_node.id
        assert edges_by_id[edge2.id].target_node_id == output_node.id

    def test_workflow_validation(self, agent_orchestrator):
        """Test workflow validation."""
        orchestrator, mock_agent = agent_orchestrator
        
        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Test Workflow Validation",
            description="A test workflow for validation"
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

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])