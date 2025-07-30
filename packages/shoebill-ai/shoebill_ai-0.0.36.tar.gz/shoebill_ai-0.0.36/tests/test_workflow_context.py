import asyncio
import sys
import os
import uuid
from datetime import datetime
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from shoebill_ai.domain.workflows.workflow_execution_context import WorkflowExecutionContext

class TestWorkflowContext:
    """Test cases for the workflow execution context."""

    def test_context_creation(self):
        """Test creating a workflow execution context."""
        workflow_id = str(uuid.uuid4())
        input_data = {"text": "This is test input data."}
        
        # Create a context
        context = WorkflowExecutionContext.create(workflow_id, input_data)
        
        # Verify the context was created correctly
        assert context is not None
        assert context.workflow_id == workflow_id
        assert context.input_data == input_data
        assert context.execution_id is not None
        assert context.status == "created"
        assert context.start_time is None
        assert context.end_time is None
        assert len(context.node_results) == 0
        assert len(context.node_errors) == 0
        assert len(context.results) == 0
        assert len(context.variables) == 0

    def test_context_execution_lifecycle(self):
        """Test the lifecycle of a workflow execution context."""
        workflow_id = str(uuid.uuid4())
        
        # Create a context
        context = WorkflowExecutionContext.create(workflow_id)
        assert context.status == "created"
        assert context.start_time is None
        assert context.end_time is None
        
        # Start execution
        context.start_execution()
        assert context.status == "running"
        assert context.start_time is not None
        assert context.end_time is None
        
        # Complete execution
        context.complete_execution("completed")
        assert context.status == "completed"
        assert context.start_time is not None
        assert context.end_time is not None
        
        # Verify execution time
        execution_time = context.get_execution_time()
        assert execution_time >= 0

    def test_node_results(self):
        """Test setting and getting node results."""
        workflow_id = str(uuid.uuid4())
        context = WorkflowExecutionContext.create(workflow_id)
        
        # Set node results
        node_id1 = str(uuid.uuid4())
        node_id2 = str(uuid.uuid4())
        
        result1 = {"response": "Result from node 1"}
        result2 = {"response": "Result from node 2"}
        
        context.set_node_result(node_id1, result1)
        context.set_node_result(node_id2, result2)
        
        # Get node results
        retrieved_result1 = context.get_node_result(node_id1)
        retrieved_result2 = context.get_node_result(node_id2)
        
        assert retrieved_result1 == result1
        assert retrieved_result2 == result2
        
        # Try to get a non-existent node result
        non_existent_node_id = str(uuid.uuid4())
        with pytest.raises(KeyError):
            context.get_node_result(non_existent_node_id)

    def test_node_errors(self):
        """Test setting and checking node errors."""
        workflow_id = str(uuid.uuid4())
        context = WorkflowExecutionContext.create(workflow_id)
        
        # Set node errors
        node_id1 = str(uuid.uuid4())
        node_id2 = str(uuid.uuid4())
        
        error1 = ValueError("Test error 1")
        error2 = RuntimeError("Test error 2")
        
        context.set_error(node_id1, error1)
        context.set_error(node_id2, error2, "Test traceback")
        
        # Check if nodes have errors
        assert context.has_error(node_id1) is True
        assert context.has_error(node_id2) is True
        
        # Get node errors
        retrieved_error1 = context.get_error(node_id1)
        retrieved_error2 = context.get_error(node_id2)
        
        assert retrieved_error1["error"] == error1
        assert retrieved_error2["error"] == error2
        assert retrieved_error2["traceback"] == "Test traceback"
        
        # Check a node without an error
        non_error_node_id = str(uuid.uuid4())
        assert context.has_error(non_error_node_id) is False
        
        # Try to get a non-existent node error
        with pytest.raises(KeyError):
            context.get_error(non_error_node_id)

    def test_results(self):
        """Test setting and getting results."""
        workflow_id = str(uuid.uuid4())
        context = WorkflowExecutionContext.create(workflow_id)
        
        # Set results
        context.set_result("result1", "Value 1")
        context.set_result("result2", {"key": "Value 2"})
        
        # Get results
        retrieved_result1 = context.get_result("result1")
        retrieved_result2 = context.get_result("result2")
        
        assert retrieved_result1 == "Value 1"
        assert retrieved_result2 == {"key": "Value 2"}
        
        # Try to get a non-existent result
        with pytest.raises(KeyError):
            context.get_result("non_existent_result")

    def test_variables(self):
        """Test setting and getting variables."""
        workflow_id = str(uuid.uuid4())
        context = WorkflowExecutionContext.create(workflow_id)
        
        # Set variables
        context.set_variable("var1", "Value 1")
        context.set_variable("var2", {"key": "Value 2"})
        
        # Get variables
        retrieved_var1 = context.get_variable("var1")
        retrieved_var2 = context.get_variable("var2")
        
        assert retrieved_var1 == "Value 1"
        assert retrieved_var2 == {"key": "Value 2"}
        
        # Get a non-existent variable with default
        non_existent_var = context.get_variable("non_existent_var", "default_value")
        assert non_existent_var == "default_value"
        
        # Get a non-existent variable without default
        non_existent_var2 = context.get_variable("non_existent_var2")
        assert non_existent_var2 is None

    def test_current_node(self):
        """Test setting and getting the current node."""
        workflow_id = str(uuid.uuid4())
        context = WorkflowExecutionContext.create(workflow_id)
        
        # Initially, current_node_id should be None
        assert context.current_node_id is None
        
        # Set current node
        node_id = str(uuid.uuid4())
        context.set_current_node(node_id)
        
        # Verify current node was set
        assert context.current_node_id == node_id
        
        # Set a different current node
        new_node_id = str(uuid.uuid4())
        context.set_current_node(new_node_id)
        
        # Verify current node was updated
        assert context.current_node_id == new_node_id

    def test_execution_summary(self):
        """Test getting the execution summary."""
        workflow_id = str(uuid.uuid4())
        context = WorkflowExecutionContext.create(workflow_id)
        
        # Start execution
        context.start_execution()
        
        # Set current node and add some results
        node_id1 = str(uuid.uuid4())
        node_id2 = str(uuid.uuid4())
        
        context.set_current_node(node_id1)
        context.set_node_result(node_id1, {"response": "Result from node 1"})
        
        context.set_current_node(node_id2)
        context.set_node_result(node_id2, {"response": "Result from node 2"})
        
        # Set an error
        error_node_id = str(uuid.uuid4())
        context.set_error(error_node_id, ValueError("Test error"))
        
        # Complete execution
        context.complete_execution("completed")
        
        # Get execution summary
        summary = context.get_execution_summary()
        
        # Verify summary contents
        assert summary is not None
        assert "execution_id" in summary
        assert summary["execution_id"] == context.execution_id
        assert "workflow_id" in summary
        assert summary["workflow_id"] == workflow_id
        assert "status" in summary
        assert summary["status"] == "completed"
        assert "start_time" in summary
        assert "end_time" in summary
        assert "execution_time" in summary
        assert summary["execution_time"] >= 0
        assert "execution_path" in summary
        assert node_id1 in summary["execution_path"]
        assert node_id2 in summary["execution_path"]
        assert "node_execution_times" in summary
        assert len(summary["node_execution_times"]) == 2
        assert "error_nodes" in summary
        assert error_node_id in summary["error_nodes"]

    def test_context_serialization(self):
        """Test serializing and deserializing a workflow execution context."""
        workflow_id = str(uuid.uuid4())
        input_data = {"text": "This is test input data."}
        
        # Create a context
        context = WorkflowExecutionContext.create(workflow_id, input_data)
        
        # Add some data to the context
        context.start_execution()
        
        node_id = str(uuid.uuid4())
        context.set_current_node(node_id)
        context.set_node_result(node_id, {"response": "Test result"})
        
        context.set_result("output", "Test output")
        context.set_variable("var", "Test variable")
        
        context.complete_execution("completed")
        
        # Serialize to dict
        context_dict = context.to_dict()
        
        # Deserialize from dict
        deserialized_context = WorkflowExecutionContext.from_dict(context_dict)
        
        # Verify the deserialized context matches the original
        assert deserialized_context.workflow_id == context.workflow_id
        assert deserialized_context.execution_id == context.execution_id
        assert deserialized_context.status == context.status
        assert deserialized_context.input_data == context.input_data
        assert deserialized_context.current_node_id == context.current_node_id
        assert deserialized_context.node_results == context.node_results
        assert deserialized_context.results == context.results
        assert deserialized_context.variables == context.variables

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])