"""
Example of using advanced workflow features: conditional branching, looping, and workflow chaining.

This example demonstrates how to create a workflow that:
1. Uses conditional branching to execute different paths based on a condition
2. Uses looping to process a collection of items
3. Chains workflows together

Usage:
    python -m shoebill_ai.examples.advanced_workflow_example
"""

import asyncio
from typing import Dict, Any, List

from shoebill_ai.domain.workflows.workflow import Workflow
from shoebill_ai.domain.workflows.workflow_node import WorkflowNode, NodeType
from shoebill_ai.infrastructure.workflows.advanced_workflow_execution_engine import AdvancedWorkflowExecutionEngine
from shoebill_ai.domain.agents.interfaces.agent_registry import AgentRegistry
from shoebill_ai.domain.agents.interfaces.function_registry import FunctionRegistry


class SimpleAgentRegistry(AgentRegistry):
    """Simple implementation of AgentRegistry for the example."""
    def get(self, agent_id: str):
        return None


class SimpleFunctionRegistry(FunctionRegistry):
    """Simple implementation of FunctionRegistry for the example."""
    def get(self, function_id: str):
        if function_id == "is_list_checker":
            # Special function to check if items is a list with elements
            def is_list_checker(**kwargs):
                data = kwargs.get("data", {})
                items = data.get("items", None)
                is_valid = isinstance(items, list) and len(items) > 0
                return {
                    "result": "List check completed", 
                    "is_valid_list": "true" if is_valid else "false",
                    "items": items  # Pass through the original items
                }
            return is_list_checker
        else:
            return lambda **kwargs: {"result": f"Function {function_id} executed with {kwargs}"}

    def get_metadata(self, function_id: str):
        return {"name": function_id, "tags": []}


class SimpleWorkflowRepository:
    """Simple implementation of a workflow repository for the example."""
    def __init__(self):
        self.workflows = {}

    def add(self, workflow: Workflow):
        self.workflows[workflow.workflow_id] = workflow

    def get(self, workflow_id: str):
        return self.workflows.get(workflow_id)


async def main():
    # Create registries and repositories
    agent_registry = SimpleAgentRegistry()
    function_registry = SimpleFunctionRegistry()
    workflow_repository = SimpleWorkflowRepository()

    # Create the execution engine
    engine = AdvancedWorkflowExecutionEngine(
        agent_registry=agent_registry,
        function_registry=function_registry,
        workflow_repository=workflow_repository
    )

    # Create a subworkflow that processes a single item
    subworkflow = Workflow(
        workflow_id="process_item_workflow",
        name="Process Item Workflow",
        description="A workflow that processes a single item"
    )

    # Add an input node to the subworkflow
    input_node = WorkflowNode(
        node_id="input",
        name="Input",
        node_type=NodeType.INPUT,
        description="Input node"
    )
    subworkflow.add_node(input_node)

    # Add a function node to the subworkflow
    process_node = WorkflowNode(
        node_id="process",
        name="Process Item",
        node_type=NodeType.FUNCTION,
        description="Process the item",
        config={
            "function_id": "process_item"
        }
    )
    subworkflow.add_node(process_node)

    # Add an output node to the subworkflow
    output_node = WorkflowNode(
        node_id="output",
        name="Output",
        node_type=NodeType.OUTPUT,
        description="Output node",
        config={
            "output_key": "processed_item"
        }
    )
    subworkflow.add_node(output_node)

    # Connect the nodes in the subworkflow
    subworkflow.add_edge(
        source_node_id="input",
        target_node_id="process",
        source_output="text",
        target_input="item"
    )
    subworkflow.add_edge(
        source_node_id="process",
        target_node_id="output",
        source_output="result",
        target_input="result"
    )

    # Add the subworkflow to the repository
    workflow_repository.add(subworkflow)

    # Create the main workflow
    workflow = Workflow(
        workflow_id="main_workflow",
        name="Main Workflow",
        description="A workflow that demonstrates advanced features"
    )

    # Add an input node to the main workflow
    main_input_node = WorkflowNode(
        node_id="main_input",
        name="Main Input",
        node_type=NodeType.INPUT,
        description="Main input node"
    )
    workflow.add_node(main_input_node)

    # Add a condition node to the main workflow
    # For this example, we need to add a function node to check if items is a list
    is_list_node = WorkflowNode(
        node_id="is_list",
        name="Check If Items Is List",
        node_type=NodeType.FUNCTION,
        description="Check if the input items is a list",
        config={
            "function_id": "is_list_checker"
        }
    )
    workflow.add_node(is_list_node)

    # Connect the input to the is_list node
    workflow.add_edge(
        source_node_id="main_input",
        target_node_id="is_list",
        source_output="text",
        target_input="data"
    )

    # Add a condition node to the main workflow
    condition_node = WorkflowNode(
        node_id="condition",
        name="Check Condition",
        node_type=NodeType.CONDITION,
        description="Check if the input items is a list with elements",
        config={
            "condition": {
                "left_value": "is_valid_list",  # This will be set by the is_list_checker function
                "operator": "==",
                "right_value": "true"
            },
            "true_branch": ["foreach"],
            "false_branch": ["error"]
        }
    )
    workflow.add_node(condition_node)

    # Add a foreach node to the main workflow
    foreach_node = WorkflowNode(
        node_id="foreach",
        name="Process Each Item",
        node_type=NodeType.FOREACH,
        description="Process each item in the list",
        config={
            "collection_key": "items",
            "item_key": "item",
            "body_nodes": ["subworkflow"],
            "parallel": False,
            "store_results": True,
            "aggregate_results": True
        }
    )
    workflow.add_node(foreach_node)

    # Add a subworkflow node to the main workflow
    subworkflow_node = WorkflowNode(
        node_id="subworkflow",
        name="Process Item Subworkflow",
        node_type=NodeType.SUBWORKFLOW,
        description="Process a single item using the subworkflow",
        config={
            "subworkflow_id": "process_item_workflow"
        }
    )
    workflow.add_node(subworkflow_node)

    # Add an error node to the main workflow
    error_node = WorkflowNode(
        node_id="error",
        name="Error",
        node_type=NodeType.FUNCTION,
        description="Handle error",
        config={
            "function_id": "handle_error"
        }
    )
    workflow.add_node(error_node)

    # Add an output node to the main workflow
    main_output_node = WorkflowNode(
        node_id="main_output",
        name="Main Output",
        node_type=NodeType.OUTPUT,
        description="Main output node",
        config={
            "output_key": "final_result"
        }
    )
    workflow.add_node(main_output_node)

    # Connect the nodes in the main workflow
    # Pass both the validation result and the items to the condition node
    workflow.add_edge(
        source_node_id="is_list",
        target_node_id="condition",
        source_output="is_valid_list",
        target_input="is_valid_list"
    )
    workflow.add_edge(
        source_node_id="is_list",
        target_node_id="condition",
        source_output="items",
        target_input="items"
    )

    # Pass the items from the condition node to the foreach node
    workflow.add_edge(
        source_node_id="condition",
        target_node_id="foreach",
        source_output="items",
        target_input="items"
    )
    workflow.add_edge(
        source_node_id="foreach",
        target_node_id="main_output",
        source_output="results",
        target_input="result"
    )
    workflow.add_edge(
        source_node_id="error",
        target_node_id="main_output",
        source_output="result",
        target_input="result"
    )

    # Execute the workflow with sample input
    input_data = {
        "items": [
            {"name": "Item 1", "value": 10},
            {"name": "Item 2", "value": 20},
            {"name": "Item 3", "value": 30}
        ]
    }

    result = await engine.execute_workflow(workflow, input_data)
    print("Workflow execution result:")
    print(result)

    # Execute the workflow with invalid input to test the condition
    invalid_input = {
        "items": "not a list"
    }

    result = await engine.execute_workflow(workflow, invalid_input)
    print("\nWorkflow execution with invalid input:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
