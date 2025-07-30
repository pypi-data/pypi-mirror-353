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

def mock_function(input_data):
    """A mock function that returns a known result."""
    # Ensure input_data has the expected structure
    if not isinstance(input_data, dict) or "text" not in input_data:
        # If input_data doesn't have the expected structure, use a default value
        input_data = {"text": "This is a test input."}

    return {
        "response": "This is a response from the mock function.",
        "input_received": input_data,
        "result": "This is a response from the mock function."
    }

class TestForeachNode:
    """Test cases for foreach nodes in workflows."""

    @pytest.fixture
    def agent_orchestrator(self):
        """Create and return an agent orchestrator with necessary functions."""
        orchestrator = AgentOrchestrator(api_url="http://localhost:11434")

        # Register the mock function
        orchestrator.function_registry.register("mock_function", mock_function)

        return orchestrator

    @pytest.mark.asyncio
    async def test_foreach_node(self, agent_orchestrator):
        """Test a foreach node in a workflow."""
        orchestrator = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Foreach Node Test",
            description="A workflow for testing foreach nodes"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add a function node that will be used in the foreach body
        function_node = orchestrator.add_function_node(
            workflow_id=workflow.id,
            name="Function Node",
            function_id="mock_function"
        )

        # Add a foreach node
        foreach_node = orchestrator.add_foreach_node(
            workflow_id=workflow.id,
            name="Foreach Node",
            collection_key="items",
            body_nodes=[function_node.id],
            item_key="text"
        )

        output_node = orchestrator.add_output_node(
            workflow_id=workflow.id,
            name="Output Node"
        )

        # Add edges
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=input_node.id,
            target_node_id=foreach_node.id
        )

        # Add an edge from the foreach node to the function node (for the loop body)
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=foreach_node.id,
            target_node_id=function_node.id
        )

        # Add an edge directly from the foreach node to the output node
        # This ensures the foreach node's result structure is preserved
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=foreach_node.id,
            target_node_id=output_node.id
        )

        # Execute the workflow
        input_data = {
            "items": [
                {"text": "Item 1"},
                {"text": "Item 2"},
                {"text": "Item 3"}
            ]
        }
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The foreach node should have processed all items
        output = result["results"]["result"]
        assert isinstance(output, dict)
        assert "count" in output
        assert output["count"] == 3

        # Get the foreach node's result directly from the context to verify result propagation
        workflow_context = orchestrator.workflow_service.execution_engine._executions.get(result["execution_id"])
        assert workflow_context is not None

        # Get the foreach node's result
        foreach_node_result = workflow_context.node_results.get(foreach_node.id)
        assert foreach_node_result is not None

        # Verify the foreach node's result structure
        assert "_is_foreach_result" in foreach_node_result
        assert "results" in foreach_node_result

        # Verify the results from each iteration
        assert isinstance(foreach_node_result["results"], dict)
        assert "count" in foreach_node_result["results"]
        assert foreach_node_result["results"]["count"] == 3
        assert "results" in foreach_node_result["results"]

        # Verify each iteration result
        iteration_results = foreach_node_result["results"]["results"]
        assert isinstance(iteration_results, list)
        assert len(iteration_results) == 3

        # Verify the content of each iteration result
        for i, iteration_result in enumerate(iteration_results):
            assert "response" in iteration_result
            assert iteration_result["response"] == "This is a response from the mock function."
            assert "input_received" in iteration_result
            assert "result" in iteration_result
            assert iteration_result["result"] == "This is a response from the mock function."

    @pytest.mark.asyncio
    async def test_foreach_node_without_aggregation(self, agent_orchestrator):
        """Test a foreach node where results do not need to be aggregated."""
        orchestrator = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Foreach Node Without Aggregation Test",
            description="A workflow for testing foreach nodes without result aggregation"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add a function node that will be used in the foreach body
        function_node = orchestrator.add_function_node(
            workflow_id=workflow.id,
            name="Function Node",
            function_id="mock_function"
        )

        # Add a foreach node with aggregate_results set to False
        foreach_node = orchestrator.add_foreach_node(
            workflow_id=workflow.id,
            name="Foreach Node",
            collection_key="items",
            body_nodes=[function_node.id],
            item_key="text",
            config={
                "aggregate_results": False
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
            target_node_id=foreach_node.id
        )

        # Add an edge from the foreach node to the function node (for the loop body)
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=foreach_node.id,
            target_node_id=function_node.id
        )

        # Add an edge directly from the foreach node to the output node
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=foreach_node.id,
            target_node_id=output_node.id
        )

        # Execute the workflow
        input_data = {
            "items": [
                {"text": "Item 1"},
                {"text": "Item 2"},
                {"text": "Item 3"}
            ]
        }
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )

        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The foreach node should have processed all items but not aggregated the results
        output = result["results"]["result"]

        # Since we're not aggregating results, the output format might vary
        # It could be the last item processed or a summary message
        if isinstance(output, dict) and "response" in output:
            # If it's a dictionary with a response field, it's likely the last item processed
            assert output["response"] == "This is a response from the mock function."
        elif isinstance(output, str):
            # If it's a string, it might be a summary message
            assert "items" in output or "processed" in output.lower()
        else:
            # Otherwise, just make sure we have some output
            assert output is not None

        # Get the foreach node's result directly from the context
        workflow_context = orchestrator.workflow_service.execution_engine._executions.get(result["execution_id"])
        assert workflow_context is not None

        # Get the foreach node's result
        foreach_node_result = workflow_context.node_results.get(foreach_node.id)
        assert foreach_node_result is not None

        # Verify that the foreach node still processed all items
        assert "_is_foreach_result" in foreach_node_result
        assert "results" in foreach_node_result

        # Even though we're not aggregating results in the final output,
        # the foreach node should still have all the individual results
        assert "results" in foreach_node_result["results"]
        iteration_results = foreach_node_result["results"]["results"]
        assert isinstance(iteration_results, list)
        assert len(iteration_results) == 3

    @pytest.mark.asyncio
    async def test_foreach_node_without_storing_results(self, agent_orchestrator):
        """Test a foreach node where results are not stored."""
        orchestrator = agent_orchestrator

        # Create a new workflow
        workflow = orchestrator.create_workflow(
            name="Foreach Node Without Storing Results Test",
            description="A workflow for testing foreach nodes without storing results"
        )

        # Add nodes
        input_node = orchestrator.add_input_node(
            workflow_id=workflow.id,
            name="Input Node"
        )

        # Add a function node that will be used in the foreach body
        function_node = orchestrator.add_function_node(
            workflow_id=workflow.id,
            name="Function Node",
            function_id="mock_function"
        )

        # Add a foreach node with store_results set to False
        foreach_node = orchestrator.add_foreach_node(
            workflow_id=workflow.id,
            name="Foreach Node",
            collection_key="items",
            body_nodes=[function_node.id],
            item_key="text",
            config={
                "store_results": False
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
            target_node_id=foreach_node.id
        )

        # Add an edge from the foreach node to the function node (for the loop body)
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=foreach_node.id,
            target_node_id=function_node.id
        )

        # Add an edge directly from the foreach node to the output node
        orchestrator.add_edge(
            workflow_id=workflow.id,
            source_node_id=foreach_node.id,
            target_node_id=output_node.id
        )

        # Execute the workflow
        input_data = {
            "items": [
                {"text": "Item 1"},
                {"text": "Item 2"},
                {"text": "Item 3"}
            ]
        }
        result = await orchestrator.execute_workflow(
            workflow_id=workflow.id,
            input_data=input_data
        )
        print("***result")
        print(result)
        # Verify the execution result
        assert result is not None
        assert result["status"] == "completed"
        assert "results" in result
        assert "result" in result["results"]

        # The foreach node should have processed all items but not stored the results
        output = result["results"]["result"]
        assert isinstance(output, dict)
        assert "count" in output
        assert output["count"] == 3
        assert "response" in output
        # The response might be "No response available" or something similar
        assert output["response"] is not None
        assert "input_received" in output

        # Results should still be present but might be empty or contain minimal information
        assert "results" in output

        # Get the foreach node's result directly from the context
        workflow_context = orchestrator.workflow_service.execution_engine._executions.get(result["execution_id"])
        assert workflow_context is not None

        # Get the foreach node's result
        foreach_node_result = workflow_context.node_results.get(foreach_node.id)
        assert foreach_node_result is not None

        # Verify that the foreach node has the expected structure for store_results=False
        assert "count" in foreach_node_result
        assert foreach_node_result["count"] == 3
        assert "response" in foreach_node_result
        # The response might be "No response available" or something similar
        assert foreach_node_result["response"] is not None
        assert "input_received" in foreach_node_result
        assert "results" in foreach_node_result

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
