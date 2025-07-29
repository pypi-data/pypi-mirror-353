"""Query API for MedRecord."""

from __future__ import annotations

from enum import Enum
from typing import Callable, Dict, List, Optional, Sequence, Tuple, TypeAlias, Union

from medmodels._medmodels import (
    PyEdgeAttributesTreeOperand,
    PyEdgeDirection,
    PyEdgeIndexOperand,
    PyEdgeIndicesOperand,
    PyEdgeMultipleAttributesOperand,
    PyEdgeMultipleValuesOperand,
    PyEdgeOperand,
    PyEdgeSingleAttributeOperand,
    PyEdgeSingleValueOperand,
    PyNodeAttributesTreeOperand,
    PyNodeIndexOperand,
    PyNodeIndicesOperand,
    PyNodeMultipleAttributesOperand,
    PyNodeMultipleValuesOperand,
    PyNodeOperand,
    PyNodeSingleAttributeOperand,
    PyNodeSingleValueOperand,
)
from medmodels.medrecord.types import (
    EdgeIndex,
    Group,
    MedRecordAttribute,
    MedRecordValue,
    NodeIndex,
)

PyQueryReturnOperand: TypeAlias = Union[
    PyNodeAttributesTreeOperand,
    PyEdgeAttributesTreeOperand,
    PyNodeMultipleAttributesOperand,
    PyEdgeMultipleAttributesOperand,
    PyNodeSingleAttributeOperand,
    PyEdgeSingleAttributeOperand,
    PyEdgeIndicesOperand,
    PyEdgeIndexOperand,
    PyNodeIndicesOperand,
    PyNodeIndexOperand,
    PyNodeMultipleValuesOperand,
    PyEdgeMultipleValuesOperand,
    PyNodeSingleValueOperand,
    PyEdgeSingleValueOperand,
    Sequence["PyQueryReturnOperand"],
]

#: A type alias for a query return operand.
QueryReturnOperand: TypeAlias = Union[
    "NodeAttributesTreeOperand",
    "EdgeAttributesTreeOperand",
    "NodeMultipleAttributesOperand",
    "EdgeMultipleAttributesOperand",
    "NodeSingleAttributeOperand",
    "EdgeSingleAttributeOperand",
    "EdgeIndicesOperand",
    "EdgeIndexOperand",
    "NodeIndicesOperand",
    "NodeIndexOperand",
    "NodeMultipleValuesOperand",
    "EdgeMultipleValuesOperand",
    "NodeSingleValueOperand",
    "EdgeSingleValueOperand",
    Sequence["QueryReturnOperand"],
]

NodeAttributesTreeQueryResult: TypeAlias = Dict[NodeIndex, List[MedRecordAttribute]]
EdgeAttributesTreeQueryResult: TypeAlias = Dict[EdgeIndex, List[MedRecordAttribute]]

NodeMultipleAttributesQueryResult: TypeAlias = Dict[NodeIndex, MedRecordAttribute]
EdgeMultipleAttributesQueryResult: TypeAlias = Dict[EdgeIndex, MedRecordAttribute]

NodeSingleAttributeQueryResult: TypeAlias = Union[
    Optional[Tuple[NodeIndex, MedRecordAttribute]],
    Optional[MedRecordAttribute],
]
EdgeSingleAttributeQueryResult: TypeAlias = Union[
    Optional[Tuple[EdgeIndex, MedRecordAttribute]],
    Optional[MedRecordAttribute],
]

EdgeIndicesQueryResult: TypeAlias = List[EdgeIndex]

EdgeIndexQueryResult: TypeAlias = Optional[EdgeIndex]

NodeIndicesQueryResult: TypeAlias = List[NodeIndex]

NodeIndexQueryResult: TypeAlias = Optional[NodeIndex]

NodeMultipleValuesQueryResult: TypeAlias = Dict[NodeIndex, MedRecordValue]
EdgeMultipleValuesQueryResult: TypeAlias = Dict[EdgeIndex, MedRecordValue]

NodeSingleValueQueryResult: TypeAlias = Union[
    Optional[Tuple[NodeIndex, MedRecordValue]],
    Optional[MedRecordValue],
]
EdgeSingleValueQueryResult: TypeAlias = Union[
    Optional[Tuple[EdgeIndex, MedRecordValue]],
    Optional[MedRecordValue],
]

#: A type alias for a query result.
QueryResult: TypeAlias = Union[
    NodeAttributesTreeQueryResult,
    EdgeAttributesTreeQueryResult,
    NodeMultipleAttributesQueryResult,
    EdgeMultipleAttributesQueryResult,
    NodeSingleAttributeQueryResult,
    EdgeSingleAttributeQueryResult,
    EdgeIndicesQueryResult,
    EdgeIndexQueryResult,
    NodeIndicesQueryResult,
    NodeIndexQueryResult,
    NodeMultipleValuesQueryResult,
    EdgeMultipleValuesQueryResult,
    NodeSingleValueQueryResult,
    EdgeSingleValueQueryResult,
    List["QueryResult"],
]

NodeQuery: TypeAlias = Callable[["NodeOperand"], QueryReturnOperand]
NodeQueryComponent: TypeAlias = Callable[["NodeOperand"], None]
NodeIndicesQuery: TypeAlias = Callable[["NodeOperand"], "NodeIndicesOperand"]
NodeIndexQuery: TypeAlias = Callable[["NodeOperand"], "NodeIndexOperand"]

EdgeQuery: TypeAlias = Callable[["EdgeOperand"], QueryReturnOperand]
EdgeQueryComponent: TypeAlias = Callable[["EdgeOperand"], None]
EdgeIndicesQuery: TypeAlias = Callable[["EdgeOperand"], "EdgeIndicesOperand"]
EdgeIndexQuery: TypeAlias = Callable[["EdgeOperand"], "EdgeIndexOperand"]

SingleValueComparisonOperand: TypeAlias = Union[
    MedRecordValue, "NodeSingleValueOperand", "EdgeSingleValueOperand"
]
SingleValueArithmeticOperand: TypeAlias = SingleValueComparisonOperand
MultipleValuesComparisonOperand: TypeAlias = Union[
    List[MedRecordValue], "NodeMultipleValuesOperand", "EdgeMultipleValuesOperand"
]


def _py_single_value_comparison_operand_from_single_value_comparison_operand(
    single_value_comparison_operand: SingleValueComparisonOperand,
) -> Union[MedRecordValue, PyNodeSingleValueOperand, PyEdgeSingleValueOperand]:
    if isinstance(single_value_comparison_operand, NodeSingleValueOperand):
        return single_value_comparison_operand._single_value_operand
    if isinstance(single_value_comparison_operand, EdgeSingleValueOperand):
        return single_value_comparison_operand._single_value_operand
    return single_value_comparison_operand


def _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
    multiple_values_comparison_operand: MultipleValuesComparisonOperand,
) -> Union[
    List[MedRecordValue], PyNodeMultipleValuesOperand, PyEdgeMultipleValuesOperand
]:
    if isinstance(multiple_values_comparison_operand, NodeMultipleValuesOperand):
        return multiple_values_comparison_operand._multiple_values_operand
    if isinstance(multiple_values_comparison_operand, EdgeMultipleValuesOperand):
        return multiple_values_comparison_operand._multiple_values_operand
    return multiple_values_comparison_operand


SingleAttributeComparisonOperand: TypeAlias = Union[
    MedRecordAttribute,
    "NodeSingleAttributeOperand",
    "EdgeSingleAttributeOperand",
]
SingleAttributeArithmeticOperand: TypeAlias = SingleAttributeComparisonOperand
MultipleAttributesComparisonOperand: TypeAlias = Union[
    List[MedRecordAttribute],
    "NodeMultipleAttributesOperand",
    "EdgeMultipleAttributesOperand",
]


def _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
    single_attribute_comparison_operand: SingleAttributeComparisonOperand,
) -> Union[
    MedRecordAttribute, PyNodeSingleAttributeOperand, PyEdgeSingleAttributeOperand
]:
    if isinstance(single_attribute_comparison_operand, NodeSingleAttributeOperand):
        return single_attribute_comparison_operand._single_attribute_operand
    if isinstance(single_attribute_comparison_operand, EdgeSingleAttributeOperand):
        return single_attribute_comparison_operand._single_attribute_operand
    return single_attribute_comparison_operand


def _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
    multiple_attributes_comparison_operand: MultipleAttributesComparisonOperand,
) -> Union[
    List[MedRecordAttribute],
    PyNodeMultipleAttributesOperand,
    PyEdgeMultipleAttributesOperand,
]:
    if isinstance(
        multiple_attributes_comparison_operand, NodeMultipleAttributesOperand
    ):
        return multiple_attributes_comparison_operand._multiple_attributes_operand
    if isinstance(
        multiple_attributes_comparison_operand, EdgeMultipleAttributesOperand
    ):
        return multiple_attributes_comparison_operand._multiple_attributes_operand
    return multiple_attributes_comparison_operand


NodeIndexComparisonOperand: TypeAlias = Union["NodeIndexOperand", NodeIndex]
NodeIndexArithmeticOperand: TypeAlias = NodeIndexComparisonOperand
NodeIndicesComparisonOperand: TypeAlias = Union["NodeIndicesOperand", List[NodeIndex]]


def _py_node_index_comparison_operand_from_node_index_comparison_operand(
    node_index_comparison_operand: NodeIndexComparisonOperand,
) -> Union[NodeIndex, PyNodeIndexOperand]:
    if isinstance(node_index_comparison_operand, NodeIndexOperand):
        return node_index_comparison_operand._node_index_operand
    return node_index_comparison_operand


def _py_node_indices_comparison_operand_from_node_indices_comparison_operand(
    node_indices_comparison_operand: NodeIndicesComparisonOperand,
) -> Union[List[NodeIndex], PyNodeIndicesOperand]:
    if isinstance(node_indices_comparison_operand, NodeIndicesOperand):
        return node_indices_comparison_operand._node_indices_operand
    return node_indices_comparison_operand


EdgeIndexComparisonOperand: TypeAlias = Union[
    "EdgeIndexOperand",
    EdgeIndex,
]
EdgeIndexArithmeticOperand: TypeAlias = EdgeIndexComparisonOperand
EdgeIndicesComparisonOperand: TypeAlias = Union[
    "EdgeIndicesOperand",
    List[EdgeIndex],
]


def _py_edge_index_comparison_operand_from_edge_index_comparison_operand(
    edge_index_comparison_operand: EdgeIndexComparisonOperand,
) -> Union[EdgeIndex, PyEdgeIndexOperand]:
    if isinstance(edge_index_comparison_operand, EdgeIndexOperand):
        return edge_index_comparison_operand._edge_index_operand
    return edge_index_comparison_operand


def _py_edge_indices_comparison_operand_from_edge_indices_comparison_operand(
    edge_indices_comparison_operand: EdgeIndicesComparisonOperand,
) -> Union[List[EdgeIndex], PyEdgeIndicesOperand]:
    if isinstance(edge_indices_comparison_operand, EdgeIndicesOperand):
        return edge_indices_comparison_operand._edge_indices_operand
    return edge_indices_comparison_operand


class EdgeDirection(Enum):
    """Enumeration of edge directions."""

    INCOMING = 0
    OUTGOING = 1
    BOTH = 2

    def _into_py_edge_direction(self) -> PyEdgeDirection:
        return (
            PyEdgeDirection.Incoming
            if self == EdgeDirection.INCOMING
            else PyEdgeDirection.Outgoing
            if self == EdgeDirection.OUTGOING
            else PyEdgeDirection.Both
        )


class NodeOperand:
    """Query API for nodes in a MedRecord."""

    _node_operand: PyNodeOperand

    def attribute(self, attribute: MedRecordAttribute) -> NodeMultipleValuesOperand:
        """Returns an operand representing the values of that attribute for the nodes.

        This method is used to query the values of an attribute for the nodes in the
        current node query.

        Args:
            attribute (MedRecordAttribute): The attribute to query.

        Returns:
            NodeMultipleValuesOperand: The operand representing the values of the
                attribute for the nodes in the current node query.
        """
        return NodeMultipleValuesOperand._from_py_multiple_values_operand(
            self._node_operand.attribute(attribute)
        )

    def attributes(self) -> NodeAttributesTreeOperand:
        """Returns an operand representing all the attributes of the nodes queried.

        This method is used to query all the attributes of the nodes in the current node
        query.

        Returns:
            NodeAttributesTreeOperand: The operand representing all the attributes of
                the nodes in the current node query.
        """
        return NodeAttributesTreeOperand._from_py_attributes_tree_operand(
            self._node_operand.attributes()
        )

    def index(self) -> NodeIndicesOperand:
        """Returns an operand representing the indices of the nodes queried.

        This method is used to query the indices of the nodes in the current node query.

        Returns:
            NodeIndicesOperand: The operand representing the indices of the nodes in the
                current node query.
        """
        return NodeIndicesOperand._from_py_node_indices_operand(
            self._node_operand.index()
        )

    def in_group(self, group: Union[Group, List[Group]]) -> None:
        """Queries the nodes that are in all the groups specified.

        Args:
            group (Union[Group, List[Group]]): The group or groups to query.
        """
        self._node_operand.in_group(group)

    def has_attribute(
        self, attribute: Union[MedRecordAttribute, List[MedRecordAttribute]]
    ) -> None:
        """Queries the nodes that have all the attributes specified.

        Args:
            attribute (Union[MedRecordAttribute, List[MedRecordAttribute]]): The
                attribute or attributes to check for.
        """
        self._node_operand.has_attribute(attribute)

    def edges(self, direction: EdgeDirection = EdgeDirection.BOTH) -> EdgeOperand:
        """Get an edges operand for the current node query.

        It is used to query the edges connecting the nodes defined after this node
        operand, having the direction specified.

        Args:
            direction (EdgeDirection): The direction of the edges to consider.
                Defaults to EdgeDirection.BOTH.

        Returns:
            EdgeOperand: The edges connecting the nodes defined after this node operand.

        Example:

            .. highlight:: python
            .. code-block:: python

                node_operand.edges(EdgeDirection.OUTGOING).attribute("weight").greater_than(10)
        """
        return EdgeOperand._from_py_edge_operand(
            self._node_operand.edges(direction._into_py_edge_direction())
        )

    def neighbors(
        self, edge_direction: EdgeDirection = EdgeDirection.OUTGOING
    ) -> NodeOperand:
        """Get a neighbors operand for the current node query.

        It is used to query the nodes that have an edge connecting them to the
        neighbors defined after this node operand.

        Args:
            edge_direction (EdgeDirection): The direction of the edges to consider.
                Defaults to EdgeDirection.OUTGOING.

        Returns:
            NodeOperand: The neighbors of the current node query.

        Example:

            .. highlight:: python
            .. code-block:: python

                node_operand.neighbors(EdgeDirection.OUTGOING).in_group(patients_group)

        """
        return NodeOperand._from_py_node_operand(
            self._node_operand.neighbors(edge_direction._into_py_edge_direction())
        )

    def either_or(
        self,
        either: NodeQueryComponent,
        or_: NodeQueryComponent,
    ) -> None:
        """Apply either-or logic to the current node query.

        It applies the combination of the two queries to the node query. It returns all
        nodes that satisfy either the first query or the second query.

        Args:
            either (NodeQueryComponent): One of the queries to apply.
            or_ (NodeQueryComponent): The other query to apply.

        Example:

            .. highlight:: python
            .. code-block:: python

                node_operand.either_or(
                    lambda node: node.attribute("age").greater_than(10),
                    lambda node: node.attribute("age").less_than(10),
                )
        """
        self._node_operand.either_or(
            lambda node: either(NodeOperand._from_py_node_operand(node)),
            lambda node: or_(NodeOperand._from_py_node_operand(node)),
        )

    def exclude(self, query: NodeQueryComponent) -> None:
        """Exclude nodes based on the query.

        Args:
            query (NodeQueryComponent): The query to apply to exclude nodes.
        """
        self._node_operand.exclude(
            lambda node: query(NodeOperand._from_py_node_operand(node))
        )

    def clone(self) -> NodeOperand:
        """Create a deep clone of the current node query.

        Returns:
            NodeOperand: A deep clone of the current node query.
        """
        return NodeOperand._from_py_node_operand(self._node_operand.deep_clone())

    @classmethod
    def _from_py_node_operand(cls, py_node_operand: PyNodeOperand) -> NodeOperand:
        node_operand = cls()
        node_operand._node_operand = py_node_operand
        return node_operand


class EdgeOperand:
    """Query API for edges in a MedRecord."""

    _edge_operand: PyEdgeOperand

    def attribute(self, attribute: MedRecordAttribute) -> EdgeMultipleValuesOperand:
        """Returns an operand representing the values of that attribute for the edges.

        Args:
            attribute (MedRecordAttribute): The attribute to query.

        Returns:
            EdgeMultipleValuesOperand: The operand representing the values of
                the attribute for the edges in the current edge query.
        """
        return EdgeMultipleValuesOperand._from_py_multiple_values_operand(
            self._edge_operand.attribute(attribute)
        )

    def attributes(self) -> EdgeAttributesTreeOperand:
        """Returns an operand representing all the attributes of the edges queried.

        Returns:
            EdgeAttributesTreeOperand: The operand representing all the attributes of
                the edges in the current edge query.
        """
        return EdgeAttributesTreeOperand._from_py_attributes_tree_operand(
            self._edge_operand.attributes()
        )

    def index(self) -> EdgeIndicesOperand:
        """Returns an operand representing the indices of the edges queried.

        Returns:
            EdgeIndicesOperand: The operand representing the indices of the edges in the
                current edge query.
        """
        return EdgeIndicesOperand._from_edge_indices_operand(self._edge_operand.index())

    def in_group(self, group: Union[Group, List[Group]]) -> None:
        """Queries the edges that are in all the groups specified.

        Args:
            group (Union[Group, List[Group]]): The group or groups to query.
        """
        self._edge_operand.in_group(group)

    def has_attribute(
        self, attribute: Union[MedRecordAttribute, List[MedRecordAttribute]]
    ) -> None:
        """Queries the edges that have all the attributes specified.

        Args:
            attribute (Union[MedRecordAttribute, List[MedRecordAttribute]]): The
                attribute or attributes to check for.
        """
        self._edge_operand.has_attribute(attribute)

    def source_node(self) -> NodeOperand:
        """Get the source node of the edges in an operand to query.

        Returns:
            NodeOperand: The operand to query the source node of the edges.
        """
        return NodeOperand._from_py_node_operand(self._edge_operand.source_node())

    def target_node(self) -> NodeOperand:
        """Get the target node of the edges in an operand to query.

        Returns:
            NodeOperand: The operand to query the target node of the edges.
        """
        return NodeOperand._from_py_node_operand(self._edge_operand.target_node())

    def either_or(
        self,
        either: EdgeQueryComponent,
        or_: EdgeQueryComponent,
    ) -> None:
        """Apply either-or logic to the current edge query.

        This method applies the combination of the two queries to the edge query. It
        returns all edges that satisfy either the first query or the second query.

        Args:
            either (EdgeQueryComponent): One of the queries to apply.
            or_ (EdgeQueryComponent): The other query to apply.

        Example:

            .. highlight:: python
            .. code-block:: python

                edge_operand.either_or(
                    lambda edge: edge.source_node().in_group("group1"),
                    lambda edge: edge.target_node().in_group("group1"),
                )


        """
        self._edge_operand.either_or(
            lambda edge: either(EdgeOperand._from_py_edge_operand(edge)),
            lambda edge: or_(EdgeOperand._from_py_edge_operand(edge)),
        )

    def exclude(self, query: EdgeQueryComponent) -> None:
        """Exclude edges based on the query.

        Args:
            query (EdgeQueryComponent): The query to apply to exclude edges.
        """
        self._edge_operand.exclude(
            lambda edge: query(EdgeOperand._from_py_edge_operand(edge))
        )

    def clone(self) -> EdgeOperand:
        """Create a deep clone of the current edge query.

        Returns:
            EdgeOperand: A deep clone of the current edge query.
        """
        return EdgeOperand._from_py_edge_operand(self._edge_operand.deep_clone())

    @classmethod
    def _from_py_edge_operand(cls, py_edge_operand: PyEdgeOperand) -> EdgeOperand:
        edge_operand = cls()
        edge_operand._edge_operand = py_edge_operand
        return edge_operand


class NodeMultipleValuesOperand:
    """Query API for multiple attribute values in a MedRecord."""

    _multiple_values_operand: PyNodeMultipleValuesOperand

    def max(self) -> NodeSingleValueOperand:
        """Get the maximum value of the multiple values.

        Returns:
            NodeSingleValueOperand: The maximum value of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.max()
        )

    def min(self) -> NodeSingleValueOperand:
        """Get the minimum value of the multiple values.

        Returns:
            NodeSingleValueOperand: The minimum value of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.min()
        )

    def mean(self) -> NodeSingleValueOperand:
        """Get the mean of the multiple values.

        Returns:
            NodeSingleValueOperand: The mean of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.mean()
        )

    def median(self) -> NodeSingleValueOperand:
        """Get the median of the multiple values.

        Returns:
            NodeSingleValueOperand: The median of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.median()
        )

    def mode(self) -> NodeSingleValueOperand:
        """Get the mode of the multiple values.

        Returns:
            NodeSingleValueOperand: The mode of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.mode()
        )

    def std(self) -> NodeSingleValueOperand:
        """Get the standard deviation of the multiple values.

        Returns:
            NodeSingleValueOperand: The standard deviation of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.std()
        )

    def var(self) -> NodeSingleValueOperand:
        """Get the variance of the multiple values.

        Returns:
            NodeSingleValueOperand: The variance of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.var()
        )

    def count(self) -> NodeSingleValueOperand:
        """Get the number of multiple values.

        Returns:
            NodeSingleValueOperand: The number of multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.count()
        )

    def sum(self) -> NodeSingleValueOperand:
        """Get the sum of the multiple values.

        Returns:
            NodeSingleValueOperand: The sum of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.sum()
        )

    def random(self) -> NodeSingleValueOperand:
        """Get a random value of the multiple values.

        Returns:
            NodeSingleValueOperand: A random value of the multiple values.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.random()
        )

    def is_string(self) -> None:
        """Query which multiple values are strings."""
        self._multiple_values_operand.is_string()

    def is_int(self) -> None:
        """Query which multiple values are integers."""
        self._multiple_values_operand.is_int()

    def is_float(self) -> None:
        """Query which multiple values are floats."""
        self._multiple_values_operand.is_float()

    def is_bool(self) -> None:
        """Query which multiple values are booleans."""
        self._multiple_values_operand.is_bool()

    def is_datetime(self) -> None:
        """Query which multiple values are datetimes."""
        self._multiple_values_operand.is_datetime()

    def is_duration(self) -> None:
        """Query which multiple values are durations (timedeltas)."""
        self._multiple_values_operand.is_duration()

    def is_null(self) -> None:
        """Query which multiple values are null (None)."""
        self._multiple_values_operand.is_null()

    def is_max(self) -> None:
        """Query which multiple values are the maximum value."""
        self._multiple_values_operand.is_max()

    def is_min(self) -> None:
        """Query which multiple values are the minimum value."""
        self._multiple_values_operand.is_min()

    def greater_than(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are greater than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.greater_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def greater_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are greater than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.greater_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are less than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.less_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are less than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.less_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def not_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are not equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.not_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def is_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query which multiple values are in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._multiple_values_operand.is_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def is_not_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query which multiple values are not in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._multiple_values_operand.is_not_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def starts_with(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values start with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.starts_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def ends_with(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values end with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.ends_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def contains(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values contain a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.contains(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def add(self, value: SingleValueArithmeticOperand) -> None:
        """Add a value to the multiple values.

        Args:
            value (SingleValueArithmeticOperand): The value to add.
        """
        self._multiple_values_operand.add(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def subtract(self, value: SingleValueArithmeticOperand) -> None:
        """Subtract a value from the multiple values.

        Args:
            value (SingleValueArithmeticOperand): The value to subtract.
        """
        self._multiple_values_operand.sub(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def multiply(self, value: SingleValueArithmeticOperand) -> None:
        """Multiply the multiple values by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to multiply by.
        """
        self._multiple_values_operand.mul(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def divide(self, value: SingleValueArithmeticOperand) -> None:
        """Divide the multiple values by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by.
        """
        self._multiple_values_operand.div(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def modulo(self, value: SingleValueArithmeticOperand) -> None:
        """Compute the modulo of the multiple values.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._multiple_values_operand.mod(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def power(self, value: SingleValueArithmeticOperand) -> None:
        """Raise the multiple values to a power.

        Args:
            value (SingleValueArithmeticOperand): The power to raise the multiple values
                to.
        """
        self._multiple_values_operand.pow(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def round(self) -> None:
        """Round the multiple values."""
        self._multiple_values_operand.round()

    def ceil(self) -> None:
        """Get the respective ceiling value of the multiple values.

        In mathematics and computer science, the ceiling function is the function that
        rounds a number upward to the nearest integer.
        """
        self._multiple_values_operand.ceil()

    def floor(self) -> None:
        """Get the respective floor of the multiple values.

        In mathematics and computer science, the floor function is the function that
        rounds a number downward to the nearest integer.
        """
        self._multiple_values_operand.floor()

    def absolute(self) -> None:
        """Get the absolute value of the multiple values."""
        self._multiple_values_operand.abs()

    def sqrt(self) -> None:
        """Get the square root of the multiple values."""
        self._multiple_values_operand.sqrt()

    def trim(self) -> None:
        """Trim the multiple values.

        The trim method removes leading and trailing whitespace from the multiple
        values.
        """
        self._multiple_values_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the multiple values.

        The trim_start method removes leading whitespace from the multiple values.
        """
        self._multiple_values_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the multiple values.

        The trim_end method removes trailing whitespace from the multiple values.
        """
        self._multiple_values_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the multiple values to lowercase."""
        self._multiple_values_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the multiple values to uppercase."""
        self._multiple_values_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the multiple values.

        The slice method extracts a section of the multiple values.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._multiple_values_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[NodeMultipleValuesOperand], None],
        or_: Callable[[NodeMultipleValuesOperand], None],
    ) -> None:
        """Apply either-or logic to the current multiple values query.

        This method applies the combination of the two queries to the multiple values
        query. It returns all multiple values that satisfy either the first query or the
        second query.

        Args:
            either (Callable[[NodeMultipleValuesOperand], None]): One of the queries to
                apply.
            or_ (Callable[[NodeMultipleValuesOperand], None]): The other query to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                multiple_values_operand.either_or(
                    lambda values: values.is_int(), lambda values: values.is_float()
                )

        """
        self._multiple_values_operand.either_or(
            lambda values: either(
                NodeMultipleValuesOperand._from_py_multiple_values_operand(values)
            ),
            lambda values: or_(
                NodeMultipleValuesOperand._from_py_multiple_values_operand(values)
            ),
        )

    def exclude(self, query: Callable[[NodeMultipleValuesOperand], None]) -> None:
        """Exclude multiple values based on the query.

        Args:
            query (Callable[[NodeMultipleValuesOperand], None]): The query to apply to
                exclude multiple values.
        """
        self._multiple_values_operand.exclude(
            lambda values: query(
                NodeMultipleValuesOperand._from_py_multiple_values_operand(values)
            )
        )

    def clone(self) -> NodeMultipleValuesOperand:
        """Create a deep clone of the current multiple values query.

        Returns:
            NodeMultipleValuesOperand: A deep clone of the current multiple
                values query.
        """
        return NodeMultipleValuesOperand._from_py_multiple_values_operand(
            self._multiple_values_operand.deep_clone()
        )

    @classmethod
    def _from_py_multiple_values_operand(
        cls, py_multiple_values_operand: PyNodeMultipleValuesOperand
    ) -> NodeMultipleValuesOperand:
        multiple_values_operand = cls()
        multiple_values_operand._multiple_values_operand = py_multiple_values_operand
        return multiple_values_operand


class EdgeMultipleValuesOperand:
    """Query API for multiple attribute values in a MedRecord."""

    _multiple_values_operand: PyEdgeMultipleValuesOperand

    def max(self) -> EdgeSingleValueOperand:
        """Get the maximum value of the multiple values.

        Returns:
            EdgeSingleValueOperand: The maximum value of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.max()
        )

    def min(self) -> EdgeSingleValueOperand:
        """Get the minimum value of the multiple values.

        Returns:
            EdgeSingleValueOperand: The minimum value of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.min()
        )

    def mean(self) -> EdgeSingleValueOperand:
        """Get the mean of the multiple values.

        Returns:
            EdgeSingleValueOperand: The mean of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.mean()
        )

    def median(self) -> EdgeSingleValueOperand:
        """Get the median of the multiple values.

        Returns:
            EdgeSingleValueOperand: The median of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.median()
        )

    def mode(self) -> EdgeSingleValueOperand:
        """Get the mode of the multiple values.

        Returns:
            EdgeSingleValueOperand: The mode of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.mode()
        )

    def std(self) -> EdgeSingleValueOperand:
        """Get the standard deviation of the multiple values.

        Returns:
            EdgeSingleValueOperand: The standard deviation of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.std()
        )

    def var(self) -> EdgeSingleValueOperand:
        """Get the variance of the multiple values.

        Returns:
            EdgeSingleValueOperand: The variance of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.var()
        )

    def count(self) -> EdgeSingleValueOperand:
        """Get the number of multiple values.

        Returns:
            EdgeSingleValueOperand: The number of multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.count()
        )

    def sum(self) -> EdgeSingleValueOperand:
        """Get the sum of the multiple values.

        Returns:
            EdgeSingleValueOperand: The sum of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.sum()
        )

    def random(self) -> EdgeSingleValueOperand:
        """Get a random value of the multiple values.

        Returns:
            EdgeSingleValueOperand: A random value of the multiple values.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._multiple_values_operand.random()
        )

    def is_string(self) -> None:
        """Query which multiple values are strings."""
        self._multiple_values_operand.is_string()

    def is_int(self) -> None:
        """Query which multiple values are integers."""
        self._multiple_values_operand.is_int()

    def is_float(self) -> None:
        """Query which multiple values are floats."""
        self._multiple_values_operand.is_float()

    def is_bool(self) -> None:
        """Query which multiple values are booleans."""
        self._multiple_values_operand.is_bool()

    def is_datetime(self) -> None:
        """Query which multiple values are datetimes."""
        self._multiple_values_operand.is_datetime()

    def is_duration(self) -> None:
        """Query which multiple values are durations (timedeltas)."""
        self._multiple_values_operand.is_duration()

    def is_null(self) -> None:
        """Query which multiple values are null (None)."""
        self._multiple_values_operand.is_null()

    def is_max(self) -> None:
        """Query which multiple values are the maximum value."""
        self._multiple_values_operand.is_max()

    def is_min(self) -> None:
        """Query which multiple values are the minimum value."""
        self._multiple_values_operand.is_min()

    def greater_than(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are greater than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.greater_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def greater_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are greater than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.greater_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are less than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.less_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are less than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.less_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def not_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values are not equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.not_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def is_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query which multiple values are in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._multiple_values_operand.is_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def is_not_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query which multiple values are not in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._multiple_values_operand.is_not_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def starts_with(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values start with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.starts_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def ends_with(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values end with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.ends_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def contains(self, value: SingleValueComparisonOperand) -> None:
        """Query which multiple values contain a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._multiple_values_operand.contains(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def add(self, value: SingleValueArithmeticOperand) -> None:
        """Add a value to the multiple values.

        Args:
            value (SingleValueArithmeticOperand): The value to add.
        """
        self._multiple_values_operand.add(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def subtract(self, value: SingleValueArithmeticOperand) -> None:
        """Subtract a value from the multiple values.

        Args:
            value (SingleValueArithmeticOperand): The value to subtract.
        """
        self._multiple_values_operand.sub(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def multiply(self, value: SingleValueArithmeticOperand) -> None:
        """Multiply the multiple values by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to multiply by.
        """
        self._multiple_values_operand.mul(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def divide(self, value: SingleValueArithmeticOperand) -> None:
        """Divide the multiple values by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by.
        """
        self._multiple_values_operand.div(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def modulo(self, value: SingleValueArithmeticOperand) -> None:
        """Compute the modulo of the multiple values.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._multiple_values_operand.mod(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def power(self, value: SingleValueArithmeticOperand) -> None:
        """Raise the multiple values to a power.

        Args:
            value (SingleValueArithmeticOperand): The power to raise the multiple values
                to.
        """
        self._multiple_values_operand.pow(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def round(self) -> None:
        """Round the multiple values."""
        self._multiple_values_operand.round()

    def ceil(self) -> None:
        """Get the respective ceiling value of the multiple values.

        In mathematics and computer science, the ceiling function is the function that
        rounds a number upward to the nearest integer.
        """
        self._multiple_values_operand.ceil()

    def floor(self) -> None:
        """Get the respective floor of the multiple values.

        In mathematics and computer science, the floor function is the function that
        rounds a number downward to the nearest integer.
        """
        self._multiple_values_operand.floor()

    def absolute(self) -> None:
        """Get the absolute value of the multiple values."""
        self._multiple_values_operand.abs()

    def sqrt(self) -> None:
        """Get the square root of the multiple values."""
        self._multiple_values_operand.sqrt()

    def trim(self) -> None:
        """Trim the multiple values.

        The trim method removes leading and trailing whitespace from the multiple
        values.
        """
        self._multiple_values_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the multiple values.

        The trim_start method removes leading whitespace from the multiple values.
        """
        self._multiple_values_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the multiple values.

        The trim_end method removes trailing whitespace from the multiple values.
        """
        self._multiple_values_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the multiple values to lowercase."""
        self._multiple_values_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the multiple values to uppercase."""
        self._multiple_values_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the multiple values.

        The slice method extracts a section of the multiple values.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._multiple_values_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[EdgeMultipleValuesOperand], None],
        or_: Callable[[EdgeMultipleValuesOperand], None],
    ) -> None:
        """Apply either-or logic to the current multiple values query.

        This method applies the combination of the two queries to the multiple values
        query. It returns all multiple values that satisfy either the first query or the
        second query.

        Args:
            either (Callable[[EdgeMultipleValuesOperand], None]): One of the queries to
                apply.
            or_ (Callable[[EdgeMultipleValuesOperand], None]): The other query to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                multiple_values_operand.either_or(
                    lambda values: values.is_int(), lambda values: values.is_float()
                )

        """
        self._multiple_values_operand.either_or(
            lambda values: either(
                EdgeMultipleValuesOperand._from_py_multiple_values_operand(values)
            ),
            lambda values: or_(
                EdgeMultipleValuesOperand._from_py_multiple_values_operand(values)
            ),
        )

    def exclude(self, query: Callable[[EdgeMultipleValuesOperand], None]) -> None:
        """Exclude multiple values based on the query.

        Args:
            query (Callable[[EdgeMultipleValuesOperand], None]): The query to apply to
                exclude multiple values.
        """
        self._multiple_values_operand.exclude(
            lambda values: query(
                EdgeMultipleValuesOperand._from_py_multiple_values_operand(values)
            )
        )

    def clone(self) -> EdgeMultipleValuesOperand:
        """Create a deep clone of the current multiple values query.

        Returns:
            EdgeMultipleValuesOperand: A deep clone of the current multiple
                values query.
        """
        return EdgeMultipleValuesOperand._from_py_multiple_values_operand(
            self._multiple_values_operand.deep_clone()
        )

    @classmethod
    def _from_py_multiple_values_operand(
        cls, py_multiple_values_operand: PyEdgeMultipleValuesOperand
    ) -> EdgeMultipleValuesOperand:
        multiple_values_operand = cls()
        multiple_values_operand._multiple_values_operand = py_multiple_values_operand
        return multiple_values_operand


class NodeSingleValueOperand:
    """Query API for a single value in a MedRecord."""

    _single_value_operand: PyNodeSingleValueOperand

    def is_string(self) -> None:
        """Query if the single value is a string."""
        self._single_value_operand.is_string()

    def is_int(self) -> None:
        """Query if the single value is an integer."""
        self._single_value_operand.is_int()

    def is_float(self) -> None:
        """Query if the single value is a float."""
        self._single_value_operand.is_float()

    def is_bool(self) -> None:
        """Query if the single value is a boolean."""
        self._single_value_operand.is_bool()

    def is_datetime(self) -> None:
        """Query if the single value is a datetime."""
        self._single_value_operand.is_datetime()

    def is_duration(self) -> None:
        """Query if the single value is a duration (timedelta)."""
        self._single_value_operand.is_duration()

    def is_null(self) -> None:
        """Query if the single value is null (None)."""
        self._single_value_operand.is_null()

    def greater_than(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is greater than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.greater_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def greater_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is greater than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.greater_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is less than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.less_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is less than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.less_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def not_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is not equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.not_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def is_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query if the single value is in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._single_value_operand.is_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def is_not_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query if the single value is not in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._single_value_operand.is_not_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def starts_with(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value starts with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.starts_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def ends_with(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value ends with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.ends_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def contains(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value contains a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.contains(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def add(self, value: SingleValueArithmeticOperand) -> None:
        """Add a value to the single value.

        Args:
            value (SingleValueArithmeticOperand): The value to add.
        """
        self._single_value_operand.add(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def subtract(self, value: SingleValueArithmeticOperand) -> None:
        """Subtract a value from the single value.

        Args:
            value (SingleValueArithmeticOperand): The value to subtract.
        """
        self._single_value_operand.sub(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def multiply(self, value: SingleValueArithmeticOperand) -> None:
        """Multiply the single value by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to multiply by.
        """
        self._single_value_operand.mul(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def divide(self, value: SingleValueArithmeticOperand) -> None:
        """Divide the single value by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by.
        """
        self._single_value_operand.div(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def modulo(self, value: SingleValueArithmeticOperand) -> None:
        """Compute the modulo of the single value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._single_value_operand.mod(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def power(self, value: SingleValueArithmeticOperand) -> None:
        """Raise the single value to a power.

        Args:
            value (SingleValueArithmeticOperand): The power to raise the value to.
        """
        self._single_value_operand.pow(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def round(self) -> None:
        """Round the single value."""
        self._single_value_operand.round()

    def ceil(self) -> None:
        """Get the respective ceiling value of the single value.

        In mathematics and computer science, the ceiling function is the function that
        rounds a number upward to the nearest integer.
        """
        self._single_value_operand.ceil()

    def floor(self) -> None:
        """Get the respective floor of the single value."""
        self._single_value_operand.floor()

    def absolute(self) -> None:
        """Get the absolute value of the single value."""
        self._single_value_operand.abs()

    def sqrt(self) -> None:
        """Get the square root of the single value."""
        self._single_value_operand.sqrt()

    def trim(self) -> None:
        """Trim the single value.

        The trim method removes leading and trailing whitespace from the single value.
        """
        self._single_value_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the single value.

        The trim_start method removes leading whitespace from the single value.
        """
        self._single_value_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the single value.

        The trim_end method removes trailing whitespace from the single value.
        """
        self._single_value_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the single value to lowercase."""
        self._single_value_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the single value to uppercase."""
        self._single_value_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the single value.

        The slice method extracts a section of the single value.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._single_value_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[NodeSingleValueOperand], None],
        or_: Callable[[NodeSingleValueOperand], None],
    ) -> None:
        """Apply either-or logic to the current single value query.

        This method applies the combination of the two queries to the single value
        query. It returns all single values that satisfy either the first query or the
        second query.

        Args:
            either (Callable[[NodeSingleValueOperand], None]): One of the queries
                to apply.
            or_ (Callable[[NodeSingleValueOperand], None]): The other query
                to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                single_value_operand.either_or(
                    lambda value: value.is_int(), lambda value: value.is_float()
                )
        """
        self._single_value_operand.either_or(
            lambda value: either(
                NodeSingleValueOperand._from_py_single_value_operand(value)
            ),
            lambda value: or_(
                NodeSingleValueOperand._from_py_single_value_operand(value)
            ),
        )

    def exclude(self, query: Callable[[NodeSingleValueOperand], None]) -> None:
        """Exclude the single value if it satisfies the query.

        Args:
            query (Callable[[NodeSingleValueOperand], None]): The query to apply
                to exclude the value.
        """
        self._single_value_operand.exclude(
            lambda value: query(
                NodeSingleValueOperand._from_py_single_value_operand(value)
            )
        )

    def clone(self) -> NodeSingleValueOperand:
        """Create a deep clone of the current single value query.

        Returns:
            NodeSingleValueOperand: A deep clone of the current single value query.
        """
        return NodeSingleValueOperand._from_py_single_value_operand(
            self._single_value_operand.deep_clone()
        )

    @classmethod
    def _from_py_single_value_operand(
        cls, py_single_value_operand: PyNodeSingleValueOperand
    ) -> NodeSingleValueOperand:
        single_value_operand = cls()
        single_value_operand._single_value_operand = py_single_value_operand
        return single_value_operand


class EdgeSingleValueOperand:
    """Query API for a single value in a MedRecord."""

    _single_value_operand: PyEdgeSingleValueOperand

    def is_string(self) -> None:
        """Query if the single value is a string."""
        self._single_value_operand.is_string()

    def is_int(self) -> None:
        """Query if the single value is an integer."""
        self._single_value_operand.is_int()

    def is_float(self) -> None:
        """Query if the single value is a float."""
        self._single_value_operand.is_float()

    def is_bool(self) -> None:
        """Query if the single value is a boolean."""
        self._single_value_operand.is_bool()

    def is_datetime(self) -> None:
        """Query if the single value is a datetime."""
        self._single_value_operand.is_datetime()

    def is_duration(self) -> None:
        """Query if the single value is a duration (timedelta)."""
        self._single_value_operand.is_duration()

    def is_null(self) -> None:
        """Query if the single value is null (None)."""
        self._single_value_operand.is_null()

    def greater_than(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is greater than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.greater_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def greater_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is greater than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.greater_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is less than a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.less_than(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def less_than_or_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is less than or equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.less_than_or_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def not_equal_to(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value is not equal to a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.not_equal_to(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def is_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query if the single value is in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._single_value_operand.is_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def is_not_in(self, values: MultipleValuesComparisonOperand) -> None:
        """Query if the single value is not in a list of values.

        Args:
            values (MultipleValuesComparisonOperand): The values to compare against.
        """
        self._single_value_operand.is_not_in(
            _py_multiple_values_comparison_operand_from_multiple_values_comparison_operand(
                values
            )
        )

    def starts_with(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value starts with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.starts_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def ends_with(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value ends with a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.ends_with(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def contains(self, value: SingleValueComparisonOperand) -> None:
        """Query if the single value contains a value.

        Args:
            value (SingleValueComparisonOperand): The value to compare against.
        """
        self._single_value_operand.contains(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def add(self, value: SingleValueArithmeticOperand) -> None:
        """Add a value to the single value.

        Args:
            value (SingleValueArithmeticOperand): The value to add.
        """
        self._single_value_operand.add(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def subtract(self, value: SingleValueArithmeticOperand) -> None:
        """Subtract a value from the single value.

        Args:
            value (SingleValueArithmeticOperand): The value to subtract.
        """
        self._single_value_operand.sub(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def multiply(self, value: SingleValueArithmeticOperand) -> None:
        """Multiply the single value by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to multiply by.
        """
        self._single_value_operand.mul(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def divide(self, value: SingleValueArithmeticOperand) -> None:
        """Divide the single value by a value.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by.
        """
        self._single_value_operand.div(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def modulo(self, value: SingleValueArithmeticOperand) -> None:
        """Compute the modulo of the single value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            value (SingleValueArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._single_value_operand.mod(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def power(self, value: SingleValueArithmeticOperand) -> None:
        """Raise the single value to a power.

        Args:
            value (SingleValueArithmeticOperand): The power to raise the value to.
        """
        self._single_value_operand.pow(
            _py_single_value_comparison_operand_from_single_value_comparison_operand(
                value
            )
        )

    def round(self) -> None:
        """Round the single value."""
        self._single_value_operand.round()

    def ceil(self) -> None:
        """Get the respective ceiling value of the single value.

        In mathematics and computer science, the ceiling function is the function that
        rounds a number upward to the nearest integer.
        """
        self._single_value_operand.ceil()

    def floor(self) -> None:
        """Get the respective floor of the single value."""
        self._single_value_operand.floor()

    def absolute(self) -> None:
        """Get the absolute value of the single value."""
        self._single_value_operand.abs()

    def sqrt(self) -> None:
        """Get the square root of the single value."""
        self._single_value_operand.sqrt()

    def trim(self) -> None:
        """Trim the single value.

        The trim method removes leading and trailing whitespace from the single value.
        """
        self._single_value_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the single value.

        The trim_start method removes leading whitespace from the single value.
        """
        self._single_value_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the single value.

        The trim_end method removes trailing whitespace from the single value.
        """
        self._single_value_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the single value to lowercase."""
        self._single_value_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the single value to uppercase."""
        self._single_value_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the single value.

        The slice method extracts a section of the single value.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._single_value_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[EdgeSingleValueOperand], None],
        or_: Callable[[EdgeSingleValueOperand], None],
    ) -> None:
        """Apply either-or logic to the current single value query.

        This method applies the combination of the two queries to the single value
        query. It returns all single values that satisfy either the first query or the
        second query.

        Args:
            either (Callable[[EdgeSingleValueOperand], None]): One of the queries
                to apply.
            or_ (Callable[[EdgeSingleValueOperand], None]): The other query
                to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                single_value_operand.either_or(
                    lambda value: value.is_int(), lambda value: value.is_float()
                )
        """
        self._single_value_operand.either_or(
            lambda value: either(
                EdgeSingleValueOperand._from_py_single_value_operand(value)
            ),
            lambda value: or_(
                EdgeSingleValueOperand._from_py_single_value_operand(value)
            ),
        )

    def exclude(self, query: Callable[[EdgeSingleValueOperand], None]) -> None:
        """Exclude the single value if it satisfies the query.

        Args:
            query (Callable[[EdgeSingleValueOperand], None]): The query to apply
                to exclude the value.
        """
        self._single_value_operand.exclude(
            lambda value: query(
                EdgeSingleValueOperand._from_py_single_value_operand(value)
            )
        )

    def clone(self) -> EdgeSingleValueOperand:
        """Create a deep clone of the current single value query.

        Returns:
            EdgeSingleValueOperand: A deep clone of the current single value query.
        """
        return EdgeSingleValueOperand._from_py_single_value_operand(
            self._single_value_operand.deep_clone()
        )

    @classmethod
    def _from_py_single_value_operand(
        cls, py_single_value_operand: PyEdgeSingleValueOperand
    ) -> EdgeSingleValueOperand:
        single_value_operand = cls()
        single_value_operand._single_value_operand = py_single_value_operand
        return single_value_operand


class NodeAttributesTreeOperand:
    """Query API for all attributes of given nodes/edges.

    This operand is used to query on attribute names, not its values.
    """

    _attributes_tree_operand: PyNodeAttributesTreeOperand

    def max(self) -> NodeMultipleAttributesOperand:
        """Query the attributes which names have the maximum value for each node/edge.

        Returns:
            NodeMultipleAttributesOperand: The attribute name with the maximum value for
                each node/edge.
        """
        return NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.max()
        )

    def min(self) -> NodeMultipleAttributesOperand:
        """Query the attributes which names have the minimum value for each node/edge.

        Returns:
            NodeMultipleAttributesOperand: The attribute name with the minimum value for
                each node/edge.
        """
        return NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.min()
        )

    def count(self) -> NodeMultipleAttributesOperand:
        """Query the number of attributes for each node/edge.

        Returns:
            NodeMultipleAttributesOperand: The number of attributes for each node/edge.
        """
        return NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.count()
        )

    def sum(self) -> NodeMultipleAttributesOperand:
        """Query the sum of the attributes for each node/edge.

        Returns:
            NodeMultipleAttributesOperand: The sum of the attributes for each node/edge.
        """
        return NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.sum()
        )

    def random(self) -> NodeMultipleAttributesOperand:
        """Query a random attribute for each node/edge.

        Returns:
            NodeMultipleAttributesOperand: A random attribute names for each node/edge.
        """
        return NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.random()
        )

    def is_string(self) -> None:
        """Query which attribute names are strings for each node/edge."""
        self._attributes_tree_operand.is_string()

    def is_int(self) -> None:
        """Query which attribute names are integers for each node/edge."""
        self._attributes_tree_operand.is_int()

    def is_max(self) -> None:
        """Query which attribute names are the maximum value for each node/edge."""
        self._attributes_tree_operand.is_max()

    def is_min(self) -> None:
        """Query which attribute names are the minimum value for each node/edge."""
        self._attributes_tree_operand.is_min()

    def greater_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are greater than a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.greater_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def greater_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are greater than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.greater_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are less than a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.less_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are less than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.less_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are equal to a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def not_equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are not equal to a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.not_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def is_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are in a list of values for each node/edge.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names of each node/edge.
        """
        self._attributes_tree_operand.is_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def is_not_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are not in a list of values for each node/edge.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names of each node/edge.
        """
        self._attributes_tree_operand.is_not_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def starts_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names start with a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.starts_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def ends_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names end with a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.ends_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def contains(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names contain a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.contains(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def add(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Add a value to all attribute names for each node/edge.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to add to all
                attribute names of each node/edge.
        """
        self._attributes_tree_operand.add(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def subtract(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Subtract a value from all attribute names for each node/edge.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to subtract from
                all attribute names of each node/edge.
        """
        self._attributes_tree_operand.sub(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def multiply(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Multiply all attribute names for each node/edge by a value.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to multiply by.
        """
        self._attributes_tree_operand.mul(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def modulo(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Compute the modulo of the attribute names for each node/ edge by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._attributes_tree_operand.mod(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def power(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Raise the attribute names to a power for each node/edge.

        Args:
            attribute (SingleAttributeArithmeticOperand): The power to raise the
                attribute names to.
        """
        self._attributes_tree_operand.pow(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def absolute(self) -> None:
        """Get the absolute value of the attribute names."""
        self._attributes_tree_operand.abs()

    def trim(self) -> None:
        """Trim the attribute names for each node/edge.

        The trim method removes leading and trailing whitespace from the attribute
        names.
        """
        self._attributes_tree_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the attribute names for each node/edge.

        The trim_start method removes leading whitespace from the attribute names.
        """
        self._attributes_tree_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the attribute names for each node/edge.

        The trim_end method removes trailing whitespace from the attribute names.
        """
        self._attributes_tree_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the attribute names to lowercase."""
        self._attributes_tree_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the attribute names to uppercase."""
        self._attributes_tree_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the attribute names.

        The slice method extracts a section of the attribute names.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._attributes_tree_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[NodeAttributesTreeOperand], None],
        or_: Callable[[NodeAttributesTreeOperand], None],
    ) -> None:
        """Apply either-or query logic to the current attributes tree.

        This method evaluates two queries on the attributes tree and returns all
        attribute names that satisfy either the first query or the second query for
        each node/edge.

        Args:
            either (Callable[[NodeAttributesTreeOperand], None]): A query function to
                evaluate one condition on the attributes.
            or_ (Callable[[NodeAttributesTreeOperand], None]): A query function to evaluate
                the alternative condition on the attributes.

        Example:
            Example usage of `either_or` logic to filter attributes

            .. highlight:: python
            .. code-block:: python

                attributes_tree_operand.either_or(
                    lambda attributes: attributes.is_int(),  # Query for integer attributes
                    lambda attributes: attributes.is_float(),  # Query for float attributes
                )
        """  # noqa: W505
        self._attributes_tree_operand.either_or(
            lambda attributes: either(
                NodeAttributesTreeOperand._from_py_attributes_tree_operand(attributes)
            ),
            lambda attributes: or_(
                NodeAttributesTreeOperand._from_py_attributes_tree_operand(attributes)
            ),
        )

    def exclude(self, query: Callable[[NodeAttributesTreeOperand], None]) -> None:
        """Exclude attribute names based on the query.

        Exclude attribute names that satisfy the query from the attributes tree.

        Args:
            query (Callable[[NodeAttributesTreeOperand], None]): The query to apply to
                exclude attribute names.
        """
        self._attributes_tree_operand.exclude(
            lambda attributes: query(
                NodeAttributesTreeOperand._from_py_attributes_tree_operand(attributes)
            )
        )

    def clone(self) -> NodeAttributesTreeOperand:
        """Create a deep clone of the current attributes tree query.

        Returns:
            NodeAttributesTreeOperand: A deep clone of the current attributes
                tree query.
        """
        return NodeAttributesTreeOperand._from_py_attributes_tree_operand(
            self._attributes_tree_operand.deep_clone()
        )

    @classmethod
    def _from_py_attributes_tree_operand(
        cls, py_attributes_tree_operand: PyNodeAttributesTreeOperand
    ) -> NodeAttributesTreeOperand:
        attributes_tree_operand = cls()
        attributes_tree_operand._attributes_tree_operand = py_attributes_tree_operand
        return attributes_tree_operand


class EdgeAttributesTreeOperand:
    """Query API for all attributes of given nodes/edges.

    This operand is used to query on attribute names, not its values.
    """

    _attributes_tree_operand: PyEdgeAttributesTreeOperand

    def max(self) -> EdgeMultipleAttributesOperand:
        """Query the attributes which names have the maximum value for each node/edge.

        Returns:
            EdgeMultipleAttributesOperand: The attribute name with the maximum value for
                each node/edge.
        """
        return EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.max()
        )

    def min(self) -> EdgeMultipleAttributesOperand:
        """Query the attributes which names have the minimum value for each node/edge.

        Returns:
            EdgeMultipleAttributesOperand: The attribute name with the minimum value for
                each node/edge.
        """
        return EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.min()
        )

    def count(self) -> EdgeMultipleAttributesOperand:
        """Query the number of attributes for each node/edge.

        Returns:
            EdgeMultipleAttributesOperand: The number of attributes for each node/edge.
        """
        return EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.count()
        )

    def sum(self) -> EdgeMultipleAttributesOperand:
        """Query the sum of the attributes for each node/edge.

        Returns:
            EdgeMultipleAttributesOperand: The sum of the attributes for each node/edge.
        """
        return EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.sum()
        )

    def random(self) -> EdgeMultipleAttributesOperand:
        """Query a random attribute for each node/edge.

        Returns:
            EdgeMultipleAttributesOperand: A random attribute names for each node/edge.
        """
        return EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._attributes_tree_operand.random()
        )

    def is_string(self) -> None:
        """Query which attribute names are strings for each node/edge."""
        self._attributes_tree_operand.is_string()

    def is_int(self) -> None:
        """Query which attribute names are integers for each node/edge."""
        self._attributes_tree_operand.is_int()

    def is_max(self) -> None:
        """Query which attribute names are the maximum value for each node/edge."""
        self._attributes_tree_operand.is_max()

    def is_min(self) -> None:
        """Query which attribute names are the minimum value for each node/edge."""
        self._attributes_tree_operand.is_min()

    def greater_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are greater than a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.greater_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def greater_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are greater than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.greater_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are less than a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.less_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are less than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.less_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are equal to a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def not_equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are not equal to a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.not_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def is_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are in a list of values for each node/edge.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names of each node/edge.
        """
        self._attributes_tree_operand.is_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def is_not_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are not in a list of values for each node/edge.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names of each node/edge.
        """
        self._attributes_tree_operand.is_not_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def starts_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names start with a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.starts_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def ends_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names end with a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.ends_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def contains(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names contain a value for each node/edge.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across all attribute names of each node/edge.
        """
        self._attributes_tree_operand.contains(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def add(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Add a value to all attribute names for each node/edge.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to add to all
                attribute names of each node/edge.
        """
        self._attributes_tree_operand.add(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def subtract(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Subtract a value from all attribute names for each node/edge.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to subtract from
                all attribute names of each node/edge.
        """
        self._attributes_tree_operand.sub(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def multiply(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Multiply all attribute names for each node/edge by a value.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to multiply by.
        """
        self._attributes_tree_operand.mul(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def modulo(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Compute the modulo of the attribute names for each node/ edge by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._attributes_tree_operand.mod(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def power(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Raise the attribute names to a power for each node/edge.

        Args:
            attribute (SingleAttributeArithmeticOperand): The power to raise the
                attribute names to.
        """
        self._attributes_tree_operand.pow(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def absolute(self) -> None:
        """Get the absolute value of the attribute names."""
        self._attributes_tree_operand.abs()

    def trim(self) -> None:
        """Trim the attribute names for each node/edge.

        The trim method removes leading and trailing whitespace from the attribute
        names.
        """
        self._attributes_tree_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the attribute names for each node/edge.

        The trim_start method removes leading whitespace from the attribute names.
        """
        self._attributes_tree_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the attribute names for each node/edge.

        The trim_end method removes trailing whitespace from the attribute names.
        """
        self._attributes_tree_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the attribute names to lowercase."""
        self._attributes_tree_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the attribute names to uppercase."""
        self._attributes_tree_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the attribute names.

        The slice method extracts a section of the attribute names.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._attributes_tree_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[EdgeAttributesTreeOperand], None],
        or_: Callable[[EdgeAttributesTreeOperand], None],
    ) -> None:
        """Apply either-or query logic to the current attributes tree.

        This method evaluates two queries on the attributes tree and returns all
        attribute names that satisfy either the first query or the second query for
        each node/edge.

        Args:
            either (Callable[[EdgeAttributesTreeOperand], None]): A query function to
                evaluate one condition on the attributes.
            or_ (Callable[[EdgeAttributesTreeOperand], None]): A query function to evaluate
                the alternative condition on the attributes.

        Example:
            Example usage of `either_or` logic to filter attributes

            .. highlight:: python
            .. code-block:: python

                attributes_tree_operand.either_or(
                    lambda attributes: attributes.is_int(),  # Query for integer attributes
                    lambda attributes: attributes.is_float(),  # Query for float attributes
                )
        """  # noqa: W505
        self._attributes_tree_operand.either_or(
            lambda attributes: either(
                EdgeAttributesTreeOperand._from_py_attributes_tree_operand(attributes)
            ),
            lambda attributes: or_(
                EdgeAttributesTreeOperand._from_py_attributes_tree_operand(attributes)
            ),
        )

    def exclude(self, query: Callable[[EdgeAttributesTreeOperand], None]) -> None:
        """Exclude attribute names based on the query.

        Exclude attribute names that satisfy the query from the attributes tree.

        Args:
            query (Callable[[EdgeAttributesTreeOperand], None]): The query to apply to
                exclude attribute names.
        """
        self._attributes_tree_operand.exclude(
            lambda attributes: query(
                EdgeAttributesTreeOperand._from_py_attributes_tree_operand(attributes)
            )
        )

    def clone(self) -> EdgeAttributesTreeOperand:
        """Create a deep clone of the current attributes tree query.

        Returns:
            EdgeAttributesTreeOperand: A deep clone of the current attributes
                tree query.
        """
        return EdgeAttributesTreeOperand._from_py_attributes_tree_operand(
            self._attributes_tree_operand.deep_clone()
        )

    @classmethod
    def _from_py_attributes_tree_operand(
        cls, py_attributes_tree_operand: PyEdgeAttributesTreeOperand
    ) -> EdgeAttributesTreeOperand:
        attributes_tree_operand = cls()
        attributes_tree_operand._attributes_tree_operand = py_attributes_tree_operand
        return attributes_tree_operand


class NodeMultipleAttributesOperand:
    """Query API for multiple attributes accross nodes/edges.

    This operand is used to query on multiple attributes names.
    """

    _multiple_attributes_operand: PyNodeMultipleAttributesOperand

    def max(self) -> NodeSingleAttributeOperand:
        """Query the attribute name across nodes/edges with the maximum value.

        Returns:
            NodeSingleAttributeOperand: The maximum attribute name across all
                nodes/edges.
        """
        return NodeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.max()
        )

    def min(self) -> NodeSingleAttributeOperand:
        """Query the attribute name across nodes/edges with the minimum value.

        Returns:
            NodeSingleAttributeOperand: The minimum attribute name across all
                nodes/edges.
        """
        return NodeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.min()
        )

    def count(self) -> NodeSingleAttributeOperand:
        """Query the number of attribute names across nodes/edges.

        Returns:
            NodeSingleAttributeOperand: The number of attribute names across all
                nodes/edges.
        """
        return NodeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.count()
        )

    def sum(self) -> NodeSingleAttributeOperand:
        """Query the sum of the attribute names across nodes/edges.

        Returns:
            NodeSingleAttributeOperand: The sum of the attribute names across all
                nodes/edges.
        """
        return NodeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.sum()
        )

    def random(self) -> NodeSingleAttributeOperand:
        """Query a random attribute name across nodes/edges.

        Returns:
            NodeSingleAttributeOperand: A random attribute name across all nodes/edges.
        """
        return NodeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.random()
        )

    def is_string(self) -> None:
        """Query which attribute names are strings across nodes/edges."""
        self._multiple_attributes_operand.is_string()

    def is_int(self) -> None:
        """Query which attribute names are integers across nodes/edges."""
        self._multiple_attributes_operand.is_int()

    def is_max(self) -> None:
        """Query which attribute names are the maximum value across nodes/edges."""
        self._multiple_attributes_operand.is_max()

    def is_min(self) -> None:
        """Query which attribute names are the minimum value across nodes/edges."""
        self._multiple_attributes_operand.is_min()

    def greater_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are greater than a value across nodes/edges.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.greater_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def greater_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are greater than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.greater_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are less than a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.less_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are less than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.less_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def not_equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are not equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.not_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def is_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names.
        """
        self._multiple_attributes_operand.is_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def is_not_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are not in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names.
        """
        self._multiple_attributes_operand.is_not_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def starts_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names start with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.starts_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def ends_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names end with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.ends_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def contains(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names contain a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.contains(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def add(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Add a value to the attribute names.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to add to the
                attribute names.
        """
        self._multiple_attributes_operand.add(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def subtract(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Subtract a value from the attribute names.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to subtract from
                the attribute names.
        """
        self._multiple_attributes_operand.sub(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def multiply(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Multiply the attribute names by a value.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to multiply by.
        """
        self._multiple_attributes_operand.mul(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def modulo(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Compute the modulo of the attribute names by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._multiple_attributes_operand.mod(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def power(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Raise the attribute names to a power.

        Args:
            attribute (SingleAttributeArithmeticOperand): The power to raise the
                attribute names to.
        """
        self._multiple_attributes_operand.pow(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def absolute(self) -> None:
        """Get the absolute value of the attribute names."""
        self._multiple_attributes_operand.abs()

    def trim(self) -> None:
        """Trim the attribute names.

        The trim method removes leading and trailing whitespace from the attribute
        names.
        """
        self._multiple_attributes_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the attribute names.

        The trim_start method removes leading whitespace from the attribute names.
        """
        self._multiple_attributes_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the attribute names.

        The trim_end method removes trailing whitespace from the attribute names.
        """
        self._multiple_attributes_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the attribute names to lowercase."""
        self._multiple_attributes_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the attribute names to uppercase."""
        self._multiple_attributes_operand.uppercase()

    def to_values(self) -> NodeMultipleValuesOperand:
        """Returns an operand representing the values of the attributes.

        Returns:
            NodeMultipleValuesOperand: An operand representing the values of
                the attributes.
        """
        return NodeMultipleValuesOperand._from_py_multiple_values_operand(
            self._multiple_attributes_operand.to_values()
        )

    def slice(self, start: int, end: int) -> None:
        """Slice the attribute names.

        The slice method extracts a section of the attribute names.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._multiple_attributes_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[NodeMultipleAttributesOperand], None],
        or_: Callable[[NodeMultipleAttributesOperand], None],
    ) -> None:
        """Apply either-or query logic to the current multiple attributes query.

        This method evaluates two queries on the multiple attributes and returns all
        attribute names that satisfy either the first query or the second query.

        Args:
            either (Callable[[NodeMultipleAttributesOperand], None]): A query function
                to evaluate one condition on the multiple attributes.
            or_ (Callable[[NodeMultipleAttributesOperand], None]): A query function to
                evaluate the alternative condition on the multiple attributes.

        Example:
            Example usage of `either_or` logic to filter attributes

            .. highlight:: python
            .. code-block:: python

                multiple_attributes_operand.either_or(
                    lambda attributes: attributes.is_int(),  # Query for integer attributes
                    lambda attributes: attributes.is_float(),  # Query for float attributes
                )
        """  # noqa: W505
        self._multiple_attributes_operand.either_or(
            lambda attributes: either(
                NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
                    attributes
                )
            ),
            lambda attributes: or_(
                NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
                    attributes
                )
            ),
        )

    def exclude(self, query: Callable[[NodeMultipleAttributesOperand], None]) -> None:
        """Exclude attribute names based on the query.

        Exclude attribute names that satisfy the query from the multiple attributes.

        Args:
            query (Callable[[NodeMultipleAttributesOperand], None]): The query to apply
                to exclude attribute names.
        """
        self._multiple_attributes_operand.exclude(
            lambda attributes: query(
                NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
                    attributes
                )
            )
        )

    def clone(self) -> NodeMultipleAttributesOperand:
        """Create a deep clone of the current multiple attributes query.

        Returns:
            NodeMultipleAttributesOperand: A deep clone of the current multiple
                attributes query.
        """
        return NodeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._multiple_attributes_operand.deep_clone()
        )

    @classmethod
    def _from_py_multiple_attributes_operand(
        cls, py_multiple_attributes_operand: PyNodeMultipleAttributesOperand
    ) -> NodeMultipleAttributesOperand:
        multiple_attributes_operand = cls()
        multiple_attributes_operand._multiple_attributes_operand = (
            py_multiple_attributes_operand
        )
        return multiple_attributes_operand


class EdgeMultipleAttributesOperand:
    """Query API for multiple attributes accross nodes/edges.

    This operand is used to query on multiple attributes names.
    """

    _multiple_attributes_operand: PyEdgeMultipleAttributesOperand

    def max(self) -> EdgeSingleAttributeOperand:
        """Query the attribute name across nodes/edges with the maximum value.

        Returns:
            EdgeSingleAttributeOperand: The maximum attribute name across all
                nodes/edges.
        """
        return EdgeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.max()
        )

    def min(self) -> EdgeSingleAttributeOperand:
        """Query the attribute name across nodes/edges with the minimum value.

        Returns:
            EdgeSingleAttributeOperand: The minimum attribute name across all
                nodes/edges.
        """
        return EdgeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.min()
        )

    def count(self) -> EdgeSingleAttributeOperand:
        """Query the number of attribute names across nodes/edges.

        Returns:
            EdgeSingleAttributeOperand: The number of attribute names across all
                nodes/edges.
        """
        return EdgeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.count()
        )

    def sum(self) -> EdgeSingleAttributeOperand:
        """Query the sum of the attribute names across nodes/edges.

        Returns:
            EdgeSingleAttributeOperand: The sum of the attribute names across all
                nodes/edges.
        """
        return EdgeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.sum()
        )

    def random(self) -> EdgeSingleAttributeOperand:
        """Query a random attribute name across nodes/edges.

        Returns:
            EdgeSingleAttributeOperand: A random attribute name across all nodes/edges.
        """
        return EdgeSingleAttributeOperand._from_py_single_attribute_operand(
            self._multiple_attributes_operand.random()
        )

    def is_string(self) -> None:
        """Query which attribute names are strings across nodes/edges."""
        self._multiple_attributes_operand.is_string()

    def is_int(self) -> None:
        """Query which attribute names are integers across nodes/edges."""
        self._multiple_attributes_operand.is_int()

    def is_max(self) -> None:
        """Query which attribute names are the maximum value across nodes/edges."""
        self._multiple_attributes_operand.is_max()

    def is_min(self) -> None:
        """Query which attribute names are the minimum value across nodes/edges."""
        self._multiple_attributes_operand.is_min()

    def greater_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are greater than a value across nodes/edges.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.greater_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def greater_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are greater than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.greater_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are less than a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.less_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query which attribute names are less than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.less_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def not_equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names are not equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.not_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def is_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names.
        """
        self._multiple_attributes_operand.is_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def is_not_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query which attribute names are not in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The list of values to
                compare against across the attribute names.
        """
        self._multiple_attributes_operand.is_not_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def starts_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names start with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.starts_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def ends_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names end with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.ends_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def contains(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query which attribute names contain a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against
                across the attribute names.
        """
        self._multiple_attributes_operand.contains(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def add(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Add a value to the attribute names.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to add to the
                attribute names.
        """
        self._multiple_attributes_operand.add(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def subtract(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Subtract a value from the attribute names.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to subtract from
                the attribute names.
        """
        self._multiple_attributes_operand.sub(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def multiply(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Multiply the attribute names by a value.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to multiply by.
        """
        self._multiple_attributes_operand.mul(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def modulo(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Compute the modulo of the attribute names by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._multiple_attributes_operand.mod(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def power(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Raise the attribute names to a power.

        Args:
            attribute (SingleAttributeArithmeticOperand): The power to raise the
                attribute names to.
        """
        self._multiple_attributes_operand.pow(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def absolute(self) -> None:
        """Get the absolute value of the attribute names."""
        self._multiple_attributes_operand.abs()

    def trim(self) -> None:
        """Trim the attribute names.

        The trim method removes leading and trailing whitespace from the attribute
        names.
        """
        self._multiple_attributes_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the attribute names.

        The trim_start method removes leading whitespace from the attribute names.
        """
        self._multiple_attributes_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the attribute names.

        The trim_end method removes trailing whitespace from the attribute names.
        """
        self._multiple_attributes_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the attribute names to lowercase."""
        self._multiple_attributes_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the attribute names to uppercase."""
        self._multiple_attributes_operand.uppercase()

    def to_values(self) -> EdgeMultipleValuesOperand:
        """Returns an operand representing the values of the attributes.

        Returns:
            EdgeMultipleValuesOperand: An operand representing the values of
                the attributes.
        """
        return EdgeMultipleValuesOperand._from_py_multiple_values_operand(
            self._multiple_attributes_operand.to_values()
        )

    def slice(self, start: int, end: int) -> None:
        """Slice the attribute names.

        The slice method extracts a section of the attribute names.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._multiple_attributes_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[EdgeMultipleAttributesOperand], None],
        or_: Callable[[EdgeMultipleAttributesOperand], None],
    ) -> None:
        """Apply either-or query logic to the current multiple attributes query.

        This method evaluates two queries on the multiple attributes and returns all
        attribute names that satisfy either the first query or the second query.

        Args:
            either (Callable[[EdgeMultipleAttributesOperand], None]): A query function
                to evaluate one condition on the multiple attributes.
            or_ (Callable[[EdgeMultipleAttributesOperand], None]): A query function to
                evaluate the alternative condition on the multiple attributes.

        Example:
            Example usage of `either_or` logic to filter attributes

            .. highlight:: python
            .. code-block:: python

                multiple_attributes_operand.either_or(
                    lambda attributes: attributes.is_int(),  # Query for integer attributes
                    lambda attributes: attributes.is_float(),  # Query for float attributes
                )
        """  # noqa: W505
        self._multiple_attributes_operand.either_or(
            lambda attributes: either(
                EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
                    attributes
                )
            ),
            lambda attributes: or_(
                EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
                    attributes
                )
            ),
        )

    def exclude(self, query: Callable[[EdgeMultipleAttributesOperand], None]) -> None:
        """Exclude attribute names based on the query.

        Exclude attribute names that satisfy the query from the multiple attributes.

        Args:
            query (Callable[[EdgeMultipleAttributesOperand], None]): The query to apply
                to exclude attribute names.
        """
        self._multiple_attributes_operand.exclude(
            lambda attributes: query(
                EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
                    attributes
                )
            )
        )

    def clone(self) -> EdgeMultipleAttributesOperand:
        """Create a deep clone of the current multiple attributes query.

        Returns:
            EdgeMultipleAttributesOperand: A deep clone of the current multiple
                attributes query.
        """
        return EdgeMultipleAttributesOperand._from_py_multiple_attributes_operand(
            self._multiple_attributes_operand.deep_clone()
        )

    @classmethod
    def _from_py_multiple_attributes_operand(
        cls, py_multiple_attributes_operand: PyEdgeMultipleAttributesOperand
    ) -> EdgeMultipleAttributesOperand:
        multiple_attributes_operand = cls()
        multiple_attributes_operand._multiple_attributes_operand = (
            py_multiple_attributes_operand
        )
        return multiple_attributes_operand


class NodeSingleAttributeOperand:
    """Query API for a single attribute name in a MedRecord."""

    _single_attribute_operand: PyNodeSingleAttributeOperand

    def is_string(self) -> None:
        """Query if the single attribute name is a string."""
        self._single_attribute_operand.is_string()

    def is_int(self) -> None:
        """Query if the single attribute name is an integer."""
        self._single_attribute_operand.is_int()

    def greater_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is greater than a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.greater_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def greater_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query if the single attribute name is greater than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.greater_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is less than a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.less_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query if the single attribute name is less than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.less_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def not_equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is not equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.not_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def is_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query if the single attribute name is in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The values to compare
                against.
        """
        self._single_attribute_operand.is_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def is_not_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query if the single attribute name is not in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The values to compare
                against.
        """
        self._single_attribute_operand.is_not_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def starts_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name starts with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.starts_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def ends_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name ends with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.ends_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def contains(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name contains a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.contains(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def add(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Add a value to the single attribute name.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to add.
        """
        self._single_attribute_operand.add(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def subtract(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Subtract a value from the single attribute name.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to subtract.
        """
        self._single_attribute_operand.sub(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def multiply(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Multiply the single attribute name by a value.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to multiply by.
        """
        self._single_attribute_operand.mul(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def modulo(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Compute the modulo of the single attribute name by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._single_attribute_operand.mod(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def power(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Raise the single attribute name to a power.

        Args:
            attribute (SingleAttributeArithmeticOperand): The power to raise the single
                attribute name to.
        """
        self._single_attribute_operand.pow(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def absolute(self) -> None:
        """Get the absolute value of the single attribute name."""
        self._single_attribute_operand.abs()

    def trim(self) -> None:
        """Trim the single attribute name.

        The trim method removes leading and trailing whitespace from the single
        attribute name.
        """
        self._single_attribute_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the single attribute name.

        The trim_start method removes leading whitespace from the single attribute name.
        """
        self._single_attribute_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the single attribute name.

        The trim_end method removes trailing whitespace from the single attribute name.
        """
        self._single_attribute_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the single attribute name to lowercase."""
        self._single_attribute_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the single attribute name to uppercase."""
        self._single_attribute_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the single attribute name.

        The slice method extracts a section of the single attribute name.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._single_attribute_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[NodeSingleAttributeOperand], None],
        or_: Callable[[NodeSingleAttributeOperand], None],
    ) -> None:
        """Apply either-or logic to the current single attribute name query.

        This method evaluates two queries on the single attribute name and returns the
        attribute name that satisfies either the first query or the second query.

        Args:
            either (Callable[[NodeSingleAttributeOperand], None]): One of the queries to
                apply.
            or_ (Callable[[NodeSingleAttributeOperand], None]): The other query
                to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                single_attribute_operand.either_or(
                    lambda attribute: attribute.is_in(["a", "b"]),
                    lambda attribute: attribute.is_in(["A", "B"]),
                )
        """
        self._single_attribute_operand.either_or(
            lambda attribute: either(
                NodeSingleAttributeOperand._from_py_single_attribute_operand(attribute)
            ),
            lambda attribute: or_(
                NodeSingleAttributeOperand._from_py_single_attribute_operand(attribute)
            ),
        )

    def exclude(self, query: Callable[[NodeSingleAttributeOperand], None]) -> None:
        """Exclude the single attribute name if it satisfies the query.

        Args:
            query (Callable[[NodeSingleAttributeOperand], None]): The query to apply to
                exclude the value.
        """
        self._single_attribute_operand.exclude(
            lambda attribute: query(
                NodeSingleAttributeOperand._from_py_single_attribute_operand(attribute)
            )
        )

    def clone(self) -> NodeSingleAttributeOperand:
        """Create a deep clone of the current single attribute name query.

        Returns:
            NodeSingleAttributeOperand: A deep clone of the current single attribute
                name query.
        """
        return NodeSingleAttributeOperand._from_py_single_attribute_operand(
            self._single_attribute_operand.deep_clone()
        )

    @classmethod
    def _from_py_single_attribute_operand(
        cls, py_single_attribute_operand: PyNodeSingleAttributeOperand
    ) -> NodeSingleAttributeOperand:
        single_attribute_operand = cls()
        single_attribute_operand._single_attribute_operand = py_single_attribute_operand
        return single_attribute_operand


class EdgeSingleAttributeOperand:
    """Query API for a single attribute name in a MedRecord."""

    _single_attribute_operand: PyEdgeSingleAttributeOperand

    def is_string(self) -> None:
        """Query if the single attribute name is a string."""
        self._single_attribute_operand.is_string()

    def is_int(self) -> None:
        """Query if the single attribute name is an integer."""
        self._single_attribute_operand.is_int()

    def greater_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is greater than a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.greater_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def greater_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query if the single attribute name is greater than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.greater_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is less than a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.less_than(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def less_than_or_equal_to(
        self, attribute: SingleAttributeComparisonOperand
    ) -> None:
        """Query if the single attribute name is less than or equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.less_than_or_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def not_equal_to(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name is not equal to a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.not_equal_to(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def is_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query if the single attribute name is in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The values to compare
                against.
        """
        self._single_attribute_operand.is_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def is_not_in(self, attributes: MultipleAttributesComparisonOperand) -> None:
        """Query if the single attribute name is not in a list of values.

        Args:
            attributes (MultipleAttributesComparisonOperand): The values to compare
                against.
        """
        self._single_attribute_operand.is_not_in(
            _py_multiple_attributes_comparison_operand_from_multiple_attributes_comparison_operand(
                attributes
            )
        )

    def starts_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name starts with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.starts_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def ends_with(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name ends with a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.ends_with(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def contains(self, attribute: SingleAttributeComparisonOperand) -> None:
        """Query if the single attribute name contains a value.

        Args:
            attribute (SingleAttributeComparisonOperand): The value to compare against.
        """
        self._single_attribute_operand.contains(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def add(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Add a value to the single attribute name.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to add.
        """
        self._single_attribute_operand.add(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def subtract(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Subtract a value from the single attribute name.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to subtract.
        """
        self._single_attribute_operand.sub(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def multiply(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Multiply the single attribute name by a value.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to multiply by.
        """
        self._single_attribute_operand.mul(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def modulo(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Compute the modulo of the single attribute name by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            attribute (SingleAttributeArithmeticOperand): The value to divide by when
                computing the modulo.
        """
        self._single_attribute_operand.mod(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def power(self, attribute: SingleAttributeArithmeticOperand) -> None:
        """Raise the single attribute name to a power.

        Args:
            attribute (SingleAttributeArithmeticOperand): The power to raise the single
                attribute name to.
        """
        self._single_attribute_operand.pow(
            _py_single_attribute_comparison_operand_from_single_attribute_comparison_operand(
                attribute
            )
        )

    def absolute(self) -> None:
        """Get the absolute value of the single attribute name."""
        self._single_attribute_operand.abs()

    def trim(self) -> None:
        """Trim the single attribute name.

        The trim method removes leading and trailing whitespace from the single
        attribute name.
        """
        self._single_attribute_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the single attribute name.

        The trim_start method removes leading whitespace from the single attribute name.
        """
        self._single_attribute_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the single attribute name.

        The trim_end method removes trailing whitespace from the single attribute name.
        """
        self._single_attribute_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the single attribute name to lowercase."""
        self._single_attribute_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the single attribute name to uppercase."""
        self._single_attribute_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the single attribute name.

        The slice method extracts a section of the single attribute name.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._single_attribute_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[EdgeSingleAttributeOperand], None],
        or_: Callable[[EdgeSingleAttributeOperand], None],
    ) -> None:
        """Apply either-or logic to the current single attribute name query.

        This method evaluates two queries on the single attribute name and returns the
        attribute name that satisfies either the first query or the second query.

        Args:
            either (Callable[[EdgeSingleAttributeOperand], None]): One of the queries to
                apply.
            or_ (Callable[[EdgeSingleAttributeOperand], None]): The other query
                to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                single_attribute_operand.either_or(
                    lambda attribute: attribute.is_in(["a", "b"]),
                    lambda attribute: attribute.is_in(["A", "B"]),
                )
        """
        self._single_attribute_operand.either_or(
            lambda attribute: either(
                EdgeSingleAttributeOperand._from_py_single_attribute_operand(attribute)
            ),
            lambda attribute: or_(
                EdgeSingleAttributeOperand._from_py_single_attribute_operand(attribute)
            ),
        )

    def exclude(self, query: Callable[[EdgeSingleAttributeOperand], None]) -> None:
        """Exclude the single attribute name if it satisfies the query.

        Args:
            query (Callable[[EdgeSingleAttributeOperand], None]): The query to apply to
                exclude the value.
        """
        self._single_attribute_operand.exclude(
            lambda attribute: query(
                EdgeSingleAttributeOperand._from_py_single_attribute_operand(attribute)
            )
        )

    def clone(self) -> EdgeSingleAttributeOperand:
        """Create a deep clone of the current single attribute name query.

        Returns:
            EdgeSingleAttributeOperand: A deep clone of the current single attribute
                name query.
        """
        return EdgeSingleAttributeOperand._from_py_single_attribute_operand(
            self._single_attribute_operand.deep_clone()
        )

    @classmethod
    def _from_py_single_attribute_operand(
        cls, py_single_attribute_operand: PyEdgeSingleAttributeOperand
    ) -> EdgeSingleAttributeOperand:
        single_attribute_operand = cls()
        single_attribute_operand._single_attribute_operand = py_single_attribute_operand
        return single_attribute_operand


class NodeIndicesOperand:
    """Query API for node indices in a MedRecord."""

    _node_indices_operand: PyNodeIndicesOperand

    def max(self) -> NodeIndexOperand:
        """Queries and returns the node index operand with the maximum value.

        Returns:
            NodeIndexOperand: The node index operand with the maximum value.
        """
        return NodeIndexOperand._from_py_node_index_operand(
            self._node_indices_operand.max()
        )

    def min(self) -> NodeIndexOperand:
        """Queries and returns the node index operand with the minimum value.

        Returns:
            NodeIndexOperand: The node index operand with the minimum value.
        """
        return NodeIndexOperand._from_py_node_index_operand(
            self._node_indices_operand.min()
        )

    def count(self) -> NodeIndexOperand:
        """Queries and returns the number of node indices.

        Returns:
            NodeIndexOperand: The number of node indices.
        """
        return NodeIndexOperand._from_py_node_index_operand(
            self._node_indices_operand.count()
        )

    def sum(self) -> NodeIndexOperand:
        """Queries and returns the sum of the node indices.

        Returns:
            NodeIndexOperand: The sum of the node indices.
        """
        return NodeIndexOperand._from_py_node_index_operand(
            self._node_indices_operand.sum()
        )

    def random(self) -> NodeIndexOperand:
        """Queries and returns a random node index.

        Returns:
            NodeIndexOperand: A random node index.
        """
        return NodeIndexOperand._from_py_node_index_operand(
            self._node_indices_operand.random()
        )

    def is_string(self) -> None:
        """Query which node indices are strings."""
        self._node_indices_operand.is_string()

    def is_int(self) -> None:
        """Query which node indices are integers."""
        self._node_indices_operand.is_int()

    def is_max(self) -> None:
        """Query which node indices are the maximum value."""
        self._node_indices_operand.is_max()

    def is_min(self) -> None:
        """Query which node indices are the minimum value."""
        self._node_indices_operand.is_min()

    def greater_than(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices are greater than a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.greater_than(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def greater_than_or_equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices are greater than or equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.greater_than_or_equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def less_than(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices are less than a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.less_than(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def less_than_or_equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices are less than or equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.less_than_or_equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices are equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def not_equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices are not equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.not_equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def is_in(self, indices: NodeIndicesComparisonOperand) -> None:
        """Query which node indices are in a list of values.

        Args:
            indices (NodeIndicesComparisonOperand): The values to compare against.
        """
        self._node_indices_operand.is_in(
            _py_node_indices_comparison_operand_from_node_indices_comparison_operand(
                indices
            )
        )

    def is_not_in(self, indices: NodeIndicesComparisonOperand) -> None:
        """Query which node indices are not in a list of values.

        Args:
            indices (NodeIndicesComparisonOperand): The values to compare against.
        """
        self._node_indices_operand.is_not_in(
            _py_node_indices_comparison_operand_from_node_indices_comparison_operand(
                indices
            )
        )

    def starts_with(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices start with a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.starts_with(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def ends_with(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices end with a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.ends_with(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def contains(self, index: NodeIndexComparisonOperand) -> None:
        """Query which node indices contain a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_indices_operand.contains(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def add(self, index: NodeIndexArithmeticOperand) -> None:
        """Add a value to the node indices.

        Args:
            index (NodeIndexArithmeticOperand): The value to add.
        """
        self._node_indices_operand.add(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def subtract(self, index: NodeIndexArithmeticOperand) -> None:
        """Subtract a value from the node indices.

        Args:
            index (NodeIndexArithmeticOperand): The value to subtract.
        """
        self._node_indices_operand.sub(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def multiply(self, index: NodeIndexArithmeticOperand) -> None:
        """Multiply the node indices by a value.

        Args:
            index (NodeIndexArithmeticOperand): The value to multiply by.
        """
        self._node_indices_operand.mul(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def modulo(self, index: NodeIndexArithmeticOperand) -> None:
        """Compute the modulo of the node indices by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            index (NodeIndexArithmeticOperand): The index to divide by when computing
                the modulo.
        """
        self._node_indices_operand.mod(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def power(self, index: NodeIndexArithmeticOperand) -> None:
        """Raise the node indices to a power.

        Args:
            index (NodeIndexArithmeticOperand): The power to raise the node indices to.
        """
        self._node_indices_operand.pow(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def absolute(self) -> None:
        """Get the absolute value of the node indices."""
        self._node_indices_operand.abs()

    def trim(self) -> None:
        """Trim the node indices.

        The trim method removes leading and trailing whitespace from the node indices.
        """
        self._node_indices_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the node indices.

        This method removes leading whitespace from the node indices.
        """
        self._node_indices_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the node indices.

        This method removes trailing whitespace from the node indices.
        """
        self._node_indices_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the node indices to lowercase."""
        self._node_indices_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the node indices to uppercase."""
        self._node_indices_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the node indices.

        The slice method extracts a section of the node indices.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._node_indices_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[NodeIndicesOperand], None],
        or_: Callable[[NodeIndicesOperand], None],
    ) -> None:
        """Apply either-or logic to the current node indices query.

        This method evaluates two queries on the node indices and returns all node
        indices that satisfy either the first query or the second query.

        Args:
            either (Callable[[NodeIndicesOperand], None]): One of the queries to apply.
            or_ (Callable[[NodeIndicesOperand], None]): The other query to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                node_indices_operand.either_or(
                    lambda node_indices: node_indices.is_int(),
                    lambda node_indices: node_indices.is_float(),
                )
        """
        self._node_indices_operand.either_or(
            lambda node_indices: either(
                NodeIndicesOperand._from_py_node_indices_operand(node_indices)
            ),
            lambda node_indices: or_(
                NodeIndicesOperand._from_py_node_indices_operand(node_indices)
            ),
        )

    def exclude(self, query: Callable[[NodeIndicesOperand], None]) -> None:
        """Exclude node indices based on the query.

        Args:
            query (Callable[[NodeIndicesOperand], None]): The query to apply to exclude
                node indices.
        """
        self._node_indices_operand.exclude(
            lambda node_indices: query(
                NodeIndicesOperand._from_py_node_indices_operand(node_indices)
            )
        )

    def clone(self) -> NodeIndicesOperand:
        """Create a deep clone of the current node indices query.

        Returns:
            NodeIndicesOperand: A deep clone of the current node indices query.
        """
        return NodeIndicesOperand._from_py_node_indices_operand(
            self._node_indices_operand.deep_clone()
        )

    @classmethod
    def _from_py_node_indices_operand(
        cls, py_node_indices_operand: PyNodeIndicesOperand
    ) -> NodeIndicesOperand:
        node_indices_operand = cls()
        node_indices_operand._node_indices_operand = py_node_indices_operand
        return node_indices_operand


class NodeIndexOperand:
    """Query API for a node index in a MedRecord."""

    _node_index_operand: PyNodeIndexOperand

    def is_string(self) -> None:
        """Query whether the node index is a string."""
        self._node_index_operand.is_string()

    def is_int(self) -> None:
        """Query whether the node index is an integer."""
        self._node_index_operand.is_int()

    def greater_than(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index is greater than a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.greater_than(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def greater_than_or_equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index is greater than or equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.greater_than_or_equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def less_than(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index is less than a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.less_than(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def less_than_or_equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index is less than or equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.less_than_or_equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index is equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def not_equal_to(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index is not equal to a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.not_equal_to(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def is_in(self, indices: NodeIndicesComparisonOperand) -> None:
        """Query whether the node index is in a list of values.

        Args:
            indices (NodeIndicesComparisonOperand): The values to compare against.
        """
        self._node_index_operand.is_in(
            _py_node_indices_comparison_operand_from_node_indices_comparison_operand(
                indices
            )
        )

    def is_not_in(self, indices: NodeIndicesComparisonOperand) -> None:
        """Query whether the node index is not in a list of values.

        Args:
            indices (NodeIndicesComparisonOperand): The values to compare against.
        """
        self._node_index_operand.is_not_in(
            _py_node_indices_comparison_operand_from_node_indices_comparison_operand(
                indices
            )
        )

    def starts_with(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index starts with a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.starts_with(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def ends_with(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index ends with a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.ends_with(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def contains(self, index: NodeIndexComparisonOperand) -> None:
        """Query whether the node index contains a value.

        Args:
            index (NodeIndexComparisonOperand): The value to compare against.
        """
        self._node_index_operand.contains(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def add(self, index: NodeIndexArithmeticOperand) -> None:
        """Add a value to the node index.

        Args:
            index (NodeIndexArithmeticOperand): The value to add.
        """
        self._node_index_operand.add(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def subtract(self, index: NodeIndexArithmeticOperand) -> None:
        """Subtract a value from the node index.

        Args:
            index (NodeIndexArithmeticOperand): The value to subtract.
        """
        self._node_index_operand.sub(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def multiply(self, index: NodeIndexArithmeticOperand) -> None:
        """Multiply the node index by a value.

        Args:
            index (NodeIndexArithmeticOperand): The value to multiply by.
        """
        self._node_index_operand.mul(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def modulo(self, index: NodeIndexArithmeticOperand) -> None:
        """Compute the modulo of the node index by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            index (NodeIndexArithmeticOperand): The index to divide by when computing
                the modulo.
        """
        self._node_index_operand.mod(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def power(self, index: NodeIndexArithmeticOperand) -> None:
        """Raise the node index to a power.

        Args:
            index (NodeIndexArithmeticOperand): The power to raise the node index to.
        """
        self._node_index_operand.pow(
            _py_node_index_comparison_operand_from_node_index_comparison_operand(index)
        )

    def absolute(self) -> None:
        """Get the absolute value of the node index."""
        self._node_index_operand.abs()

    def trim(self) -> None:
        """Trim the node index.

        The trim method removes leading and trailing whitespace from the node index.
        """
        self._node_index_operand.trim()

    def trim_start(self) -> None:
        """Trim the start of the node index.

        This method removes leading whitespace from the node index.
        """
        self._node_index_operand.trim_start()

    def trim_end(self) -> None:
        """Trim the end of the node index.

        This method removes trailing whitespace from the node index.
        """
        self._node_index_operand.trim_end()

    def lowercase(self) -> None:
        """Convert the node index to lowercase."""
        self._node_index_operand.lowercase()

    def uppercase(self) -> None:
        """Convert the node index to uppercase."""
        self._node_index_operand.uppercase()

    def slice(self, start: int, end: int) -> None:
        """Slice the node index.

        The slice method extracts a section of the node index.

        Args:
            start (int): The start index of the slice.
            end (int): The end index of the slice.
        """
        self._node_index_operand.slice(start, end)

    def either_or(
        self,
        either: Callable[[NodeIndexOperand], None],
        or_: Callable[[NodeIndexOperand], None],
    ) -> None:
        """Apply either-or logic to the current node index query.

        This method evaluates two queries on the node index and returns the node index
        that satisfies either the first query or the second query.

        Args:
            either (Callable[[NodeIndexOperand], None]): One of the queries to apply.
            or_ (Callable[[NodeIndexOperand], None]): The other query to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                node_index_operand.either_or(
                    lambda index: index.is_int(), lambda index: index.is_float()
                )
        """
        self._node_index_operand.either_or(
            lambda node_index: either(
                NodeIndexOperand._from_py_node_index_operand(node_index)
            ),
            lambda node_index: or_(
                NodeIndexOperand._from_py_node_index_operand(node_index)
            ),
        )

    def exclude(self, query: Callable[[NodeIndexOperand], None]) -> None:
        """Exclude the node index if the query is satisfied.

        Args:
            query (Callable[[NodeIndexOperand], None]): The query to apply to exclude
                node indices.
        """
        self._node_index_operand.exclude(
            lambda node_index: query(
                NodeIndexOperand._from_py_node_index_operand(node_index)
            )
        )

    def clone(self) -> NodeIndexOperand:
        """Create a deep clone of the current node index query.

        Returns:
            NodeIndexOperand: A deep clone of the current node index query.
        """
        return NodeIndexOperand._from_py_node_index_operand(
            self._node_index_operand.deep_clone()
        )

    @classmethod
    def _from_py_node_index_operand(
        cls, py_node_index_operand: PyNodeIndexOperand
    ) -> NodeIndexOperand:
        node_index_operand = cls()
        node_index_operand._node_index_operand = py_node_index_operand
        return node_index_operand


class EdgeIndicesOperand:
    """Query API for edge indices in a MedRecord."""

    _edge_indices_operand: PyEdgeIndicesOperand

    def max(self) -> EdgeIndexOperand:
        """Queries and returns the edge index operand with the maximum value.

        Returns:
            EdgeIndexOperand: The edge index operand with the maximum value.
        """
        return EdgeIndexOperand._from_py_edge_index_operand(
            self._edge_indices_operand.max()
        )

    def min(self) -> EdgeIndexOperand:
        """Queries and returns the edge index operand with the minimum value.

        Returns:
            EdgeIndexOperand: The edge index operand with the minimum value.
        """
        return EdgeIndexOperand._from_py_edge_index_operand(
            self._edge_indices_operand.min()
        )

    def count(self) -> EdgeIndexOperand:
        """Queries and returns the number of edge indices.

        Returns:
            EdgeIndexOperand: The number of edge indices.
        """
        return EdgeIndexOperand._from_py_edge_index_operand(
            self._edge_indices_operand.count()
        )

    def sum(self) -> EdgeIndexOperand:
        """Queries and returns the sum of the edge indices.

        Returns:
            EdgeIndexOperand: The sum of the edge indices.
        """
        return EdgeIndexOperand._from_py_edge_index_operand(
            self._edge_indices_operand.sum()
        )

    def random(self) -> EdgeIndexOperand:
        """Queries and returns a random edge index.

        Returns:
            EdgeIndexOperand: A random edge index.
        """
        return EdgeIndexOperand._from_py_edge_index_operand(
            self._edge_indices_operand.random()
        )

    def is_max(self) -> None:
        """Query which edge indices are the maximum value."""
        self._edge_indices_operand.is_max()

    def is_min(self) -> None:
        """Query which edge indices are the minimum value."""
        self._edge_indices_operand.is_min()

    def greater_than(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices are greater than a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.greater_than(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def greater_than_or_equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices are greater than or equal to a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.greater_than_or_equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def less_than(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices are less than a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.less_than(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def less_than_or_equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices are less than or equal to a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.less_than_or_equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices are equal to a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def not_equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices are not equal to a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.not_equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def is_in(self, indices: EdgeIndicesComparisonOperand) -> None:
        """Query which edge indices are in a list of values.

        Args:
            indices (EdgeIndicesComparisonOperand): The values to compare against.
        """
        self._edge_indices_operand.is_in(
            _py_edge_indices_comparison_operand_from_edge_indices_comparison_operand(
                indices
            )
        )

    def is_not_in(self, indices: EdgeIndicesComparisonOperand) -> None:
        """Query which edge indices are not in a list of values.

        Args:
            indices (EdgeIndicesComparisonOperand): The values to compare against.
        """
        self._edge_indices_operand.is_not_in(
            _py_edge_indices_comparison_operand_from_edge_indices_comparison_operand(
                indices
            )
        )

    def starts_with(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices start with a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.starts_with(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def ends_with(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices end with a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.ends_with(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def contains(self, index: EdgeIndexComparisonOperand) -> None:
        """Query which edge indices contain a value.

        Args:
            index (EdgeIndexComparisonOperand): The value to compare against.
        """
        self._edge_indices_operand.contains(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def add(self, index: EdgeIndexArithmeticOperand) -> None:
        """Add a value to the edge indices.

        Args:
            index (EdgeIndexArithmeticOperand): The value to add.
        """
        self._edge_indices_operand.add(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def subtract(self, index: EdgeIndexArithmeticOperand) -> None:
        """Subtract a value from the edge indices.

        Args:
            index (EdgeIndexArithmeticOperand): The value to subtract.
        """
        self._edge_indices_operand.sub(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def multiply(self, index: EdgeIndexArithmeticOperand) -> None:
        """Multiply the edge indices by a value.

        Args:
            index (EdgeIndexArithmeticOperand): The value to multiply by.
        """
        self._edge_indices_operand.mul(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def modulo(self, index: EdgeIndexArithmeticOperand) -> None:
        """Compute the modulo of the edge indices by a value.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            index (EdgeIndexArithmeticOperand): The index to divide by when computing
                the modulo.
        """
        self._edge_indices_operand.mod(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def power(self, index: EdgeIndexArithmeticOperand) -> None:
        """Raise the edge indices to a power.

        Args:
            index (EdgeIndexArithmeticOperand): The power to raise the edge indices to.
        """
        self._edge_indices_operand.pow(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def either_or(
        self,
        either: Callable[[EdgeIndicesOperand], None],
        or_: Callable[[EdgeIndicesOperand], None],
    ) -> None:
        """Apply either-or logic to the edge indices.

        This method evaluates two queries on the edge indices and returns the edge
        indices that satisfy either the first query or the second query.

        Args:
            either (Callable[[EdgeIndexOperand], None]): One of the queries to apply.
            or_ (Callable[[EdgeIndexOperand], None]): The other query to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                edge_indices_operand.either_or(
                    lambda edge_indices: edge_indices.contains(1),
                    lambda edge_indices: edge_indices.less_than(10),
                )

        """
        self._edge_indices_operand.either_or(
            lambda edge_indices: either(
                EdgeIndicesOperand._from_edge_indices_operand(edge_indices)
            ),
            lambda edge_indices: or_(
                EdgeIndicesOperand._from_edge_indices_operand(edge_indices)
            ),
        )

    def exclude(self, query: Callable[[EdgeIndicesOperand], None]) -> None:
        """Exclude the edge indices that satisfy the given query.

        Args:
            query (Callable[[EdgeIndicesOperand], None]): The query to exclude.
        """
        self._edge_indices_operand.exclude(
            lambda edge_indices: query(
                EdgeIndicesOperand._from_edge_indices_operand(edge_indices)
            )
        )

    def clone(self) -> EdgeIndicesOperand:
        """Create a deep clone of the current edge indices operand.

        Returns:
            EdgeIndicesOperand: The cloned edge indices operand.
        """
        return EdgeIndicesOperand._from_edge_indices_operand(
            self._edge_indices_operand.deep_clone()
        )

    @classmethod
    def _from_edge_indices_operand(
        cls, py_edge_indices_operand: PyEdgeIndicesOperand
    ) -> EdgeIndicesOperand:
        edge_indices_operand = cls()
        edge_indices_operand._edge_indices_operand = py_edge_indices_operand
        return edge_indices_operand


class EdgeIndexOperand:
    """A class representing an edge index operand.

    An edge index operand is used to query edge indices in the graph database.
    """

    _edge_index_operand: PyEdgeIndexOperand

    def greater_than(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that are greater than the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.greater_than(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def greater_than_or_equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that are greater than or equal to the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.greater_than_or_equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def less_than(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that are less than the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.less_than(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def less_than_or_equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that are less than or equal to the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.less_than_or_equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that are equal to the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def not_equal_to(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that are not equal to the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.not_equal_to(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def is_in(self, indices: EdgeIndicesComparisonOperand) -> None:
        """Query the edge indices that are in the given indices list.

        Args:
            indices (EdgeIndicesComparisonOperand): The indices to compare with.
        """
        self._edge_index_operand.is_in(
            _py_edge_indices_comparison_operand_from_edge_indices_comparison_operand(
                indices
            )
        )

    def is_not_in(self, indices: EdgeIndicesComparisonOperand) -> None:
        """Query the edge indices that are not in the given indices sequence.

        Args:
            indices (EdgeIndicesComparisonOperand): The indices to compare with.
        """
        self._edge_index_operand.is_not_in(
            _py_edge_indices_comparison_operand_from_edge_indices_comparison_operand(
                indices
            )
        )

    def starts_with(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that start with the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.starts_with(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def ends_with(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that end with the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.ends_with(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def contains(self, index: EdgeIndexComparisonOperand) -> None:
        """Query the edge indices that contain the given index.

        Args:
            index (EdgeIndexComparisonOperand): The index to compare with.
        """
        self._edge_index_operand.contains(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def add(self, index: EdgeIndexArithmeticOperand) -> None:
        """Add the given index to the current edge index.

        Args:
            index (EdgeIndexArithmeticOperand): The index to add.
        """
        self._edge_index_operand.add(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def subtract(self, index: EdgeIndexArithmeticOperand) -> None:
        """Subtract the given index from the current edge index.

        Args:
            index (EdgeIndexArithmeticOperand): The index to subtract.
        """
        self._edge_index_operand.sub(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def multiply(self, index: EdgeIndexArithmeticOperand) -> None:
        """Multiply the current edge index by the given index.

        Args:
            index (EdgeIndexArithmeticOperand): The index to multiply by.
        """
        self._edge_index_operand.mul(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def modulo(self, index: EdgeIndexArithmeticOperand) -> None:
        """Compute the modulo of the current edge index by the given index.

        In mathematics and computer science, the modulo operation finds the remainder
        after division of one number by another.

        Args:
            index (EdgeIndexArithmeticOperand): The index to divide by when computing
                the modulo.
        """
        self._edge_index_operand.mod(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def power(self, index: EdgeIndexArithmeticOperand) -> None:
        """Raise the current edge index to the power of the given index.

        Args:
            index (EdgeIndexArithmeticOperand): The index to raise to the power of.
        """
        self._edge_index_operand.pow(
            _py_edge_index_comparison_operand_from_edge_index_comparison_operand(index)
        )

    def either_or(
        self,
        either: Callable[[EdgeIndexOperand], None],
        or_: Callable[[EdgeIndexOperand], None],
    ) -> None:
        """Apply either-or logic to the current edge index operand.

        This method evaluates two queries on the edge index and returns the edge index
        that satisfies either the first query or the second query.

        Args:
            either (Callable[[EdgeIndexOperand], None]): One of the queries to apply.
            or_ (Callable[[EdgeIndexOperand], None]): The other query to apply.

        Example:
            .. highlight:: python
            .. code-block:: python

                edge_index_operand.either_or(
                    lambda edge_index: edge_index.contains(1),
                    lambda edge_index: edge_index.less_than(10),
                )
        """
        self._edge_index_operand.either_or(
            lambda edge_index: either(
                EdgeIndexOperand._from_py_edge_index_operand(edge_index)
            ),
            lambda edge_index: or_(
                EdgeIndexOperand._from_py_edge_index_operand(edge_index)
            ),
        )

    def exclude(self, query: Callable[[EdgeIndexOperand], None]) -> None:
        """Exclude the edge indices that meet the given query.

        Args:
            query (Callable[[EdgeIndexOperand], None]): The query to exclude.
        """
        self._edge_index_operand.exclude(
            lambda edge_index: query(
                EdgeIndexOperand._from_py_edge_index_operand(edge_index)
            )
        )

    def clone(self) -> EdgeIndexOperand:
        """Clone the current edge index operand so that it can be reused.

        Returns:
            EdgeIndexOperand: The cloned edge index operand.
        """
        return EdgeIndexOperand._from_py_edge_index_operand(
            self._edge_index_operand.deep_clone()
        )

    @classmethod
    def _from_py_edge_index_operand(
        cls, py_edge_index_operand: PyEdgeIndexOperand
    ) -> EdgeIndexOperand:
        edge_index_operand = cls()
        edge_index_operand._edge_index_operand = py_edge_index_operand
        return edge_index_operand
