import asyncio
import sys
import os
import uuid

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from shoebill_ai.application.workflows.agent_orchestrator import AgentOrchestrator
from shoebill_ai.domain.agents.text_agent import TextAgent

class MockTextAgent(TextAgent):
    """A mock text agent that returns a known result."""

    def process(self, input_data, context=None):
        """Override the process method to return a known result."""
        print(f"MockTextAgent.process called with input_data: {input_data}")
        # Return a dictionary with a response key
        return {
            "response": "This is a mock response from the agent.",
            "input_received": input_data
        }

class TestWorkflowOutput:
    @pytest.fixture
    def agent_orchestrator(self):
        """Create and return an agent orchestrator with a mock agent."""
        # Initialize the agent orchestrator with a dummy API URL
        orchestrator = AgentOrchestrator(api_url="http://localhost:11434")

        # Create a mock text agent
        mock_agent = MockTextAgent(
            agent_id=str(uuid.uuid4()),
            name="Mock Text Agent",
            description="A mock agent for workflow output testing"
        )

        # Register the mock agent with the agent registry
        orchestrator.agent_registry.register(mock_agent)

        return orchestrator, mock_agent

    @pytest.mark.asyncio
    async def test_workflow_output(self, agent_orchestrator):
        # Unpack the fixture
        orchestrator, mock_agent = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Test Workflow Output",
            description="Testing workflow output handling"
        )

        print(f"Created workflow: {workflow.id}")

        # Add nodes to the workflow
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input"
        )

        mock_agent_node = orchestrator.add_agent_node(
            workflow_id=workflow.id,
            name="Mock Agent",
            agent_id=mock_agent.id,
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output"
        )

        print(f"Added nodes: Input ({input_node.id}), Mock Agent ({mock_agent_node.id}), Output ({output_node.id})")

        # Add edges to the workflow
        edge1 = orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=mock_agent_node.id
        )

        edge2 = orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=mock_agent_node.id,
            target_node_id=output_node.id
        )

        print(f"Added edges: {edge1.id} (source_output={edge1.source_output}, target_input={edge1.target_input})")
        print(f"Added edges: {edge2.id} (source_output={edge2.source_output}, target_input={edge2.target_input})")

        # Execute the workflow
        input_data = {"text": "This is a test input for the graph agent."}
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        print("\nWorkflow execution result:")
        print(f"Execution ID: {result['execution_id']}")
        print(f"Status: {result['status']}")
        print(f"Results: {result['results']}")
        print(f"Summary: {result['summary']}")

        # Check if the result contains the actual output from the agent
        if result['results'].get('result') is None:
            print("\nISSUE DETECTED: The workflow result does not contain the agent's output.")
            print(f"Result structure: {result['results']}")
        else:
            # The result could be a string or a dictionary
            result_value = result['results']['result']
            if isinstance(result_value, dict) and result_value.get('result') is None:
                print("\nISSUE DETECTED: The workflow result does not contain the agent's output.")
                print(f"Result structure: {result['results']}")
            else:
                print("\nSuccess: The workflow result contains the agent's output.")
                print(f"Result structure: {result['results']}")

        return workflow, result

async def main():
    """Run the test directly when the file is executed as a script."""
    # Create the objects that would normally be provided by the fixture
    orchestrator = AgentOrchestrator(api_url="http://localhost:11434")

    # Create a mock text agent
    mock_agent = MockTextAgent(
        agent_id=str(uuid.uuid4()),
        name="Mock Text Agent",
        description="A mock agent for workflow output testing"
    )

    # Register the mock agent with the agent registry
    orchestrator.agent_registry.register(mock_agent)

    # Create a test instance and run the test with the created objects
    test = TestWorkflowOutput()
    await test.test_workflow_output((orchestrator, mock_agent))

if __name__ == "__main__":
    asyncio.run(main())

# This allows pytest to discover and run the test
if __name__ == "test_workflow_output":
    pytest.main(["-xvs", __file__])
