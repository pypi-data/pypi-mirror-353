from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional


class NodeType(Enum):
    """
    Enum representing the types of workflow nodes.
    """
    AGENT = auto()
    FUNCTION = auto()
    INPUT = auto()
    OUTPUT = auto()
    SUBWORKFLOW = auto()
    CONDITION = auto()  # Conditional branching node
    FOREACH = auto()    # Loop over a collection
    LOOP = auto()       # General purpose loop
    VARIABLE = auto()   # Variable storage node


@dataclass
class WorkflowNode:
    """
    Represents a node in a workflow graph.

    A node can be one of the following types:
    - agent: Represents an AI agent that can process inputs and generate outputs
    - function: Represents a function that can be executed with inputs to produce outputs
    - input: Represents an input to the workflow
    - output: Represents an output from the workflow
    """
    node_id: str
    name: str
    node_type: NodeType
    description: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """
        Get the node ID.

        This property provides a more intuitive way to access the node ID.
        It returns the same value as node_id.

        Returns:
            str: The node ID
        """
        return self.node_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the node
        """
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type.name,
            "description": self.description,
            "config": self.config,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowNode':
        """
        Create a node from a dictionary representation.

        Args:
            data: Dictionary representation of the node

        Returns:
            WorkflowNode: The created node
        """
        return cls(
            node_id=data["node_id"],
            name=data["name"],
            node_type=NodeType[data["node_type"]],
            description=data.get("description"),
            config=data.get("config", {}),
            metadata=data.get("metadata", {})
        )

    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get the input schema for this node.

        Returns:
            Dict[str, Any]: The input schema
        """
        return self.config.get("input_schema", {})

    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the output schema for this node.

        Returns:
            Dict[str, Any]: The output schema
        """
        return self.config.get("output_schema", {})
