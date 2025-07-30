from typing import Any, Dict, List, Tuple

from sdoc.io.SDocIO import SDocIO
from sdoc.sdoc2.helper.Enumerable import Enumerable
from sdoc.sdoc2.Position import Position

inline_creators = {}
"""
Map from inline commands to node creators.

:type: dict[str,callable]
"""

block_creators = {}
"""
Map from block commands to object creators.

:type: dict[str,callable]
"""

formatters = {}
"""
Map from format name to map from inline and block commands to format creators.

:type: dict[str,dict[str,callable]]
"""


class NodeStore:
    """
    Class for creating, storing, and retrieving nodes.

    @todo Make abstract and implement other document store classes.
    """

    _errors: int = 0
    """
    The error count.
    """

    _io: SDocIO | None = None
    """
    Styled output formatter.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, io: SDocIO):
        """
        Object constructor.
        """
        NodeStore._io = io

        self.format: str = 'html'
        """
        The output format.
        """

        self.nested_nodes: List[Any] = []
        """
        The stack of nested nodes (only filled when creating all nodes).

        :type: list[sdoc.sdoc2.node.Node.Node]
        """

        self.nodes: Dict[Any] = {}
        """
        The actual node store. Map from node ID to node.

        :type: dict[int,sdoc.sdoc2.node.Node.Node]
        """

        self._enumerable_numbers: Dict[Enumerable] = {}
        """
        The current numbers of enumerable nodes (e.g. headings, figures).
        """

        self.labels: Dict[str, str | Dict[str, str]] = {}
        """
        The identifiers of labels which refers on each heading node.
        """

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def error(message: str, node=None) -> None:
        """
        Logs an error.

        :param message: The error message will be appended with ' at filename:line.column.' ot the token.
        :param sdoc.sdoc2.node.Node.Node|None node: The node where the error occurred.
        """
        NodeStore._errors += 1

        messages = [message]
        if node:
            filename = node.position.file_name
            line_number = node.position.start_line
            column_number = node.position.start_column + 1
            messages.append(f' at position: {filename}:{line_number}.{column_number}')
        NodeStore._io.write_error(messages)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_formatter(output_type: str, name_formatter: str):
        """
        Returns the formatter for special type.

        :param output_type: The type of output formatter (e.g. 'html')
        :param name_formatter: The name of formatter (e.g. 'smile')
        """
        return formatters[output_type][name_formatter]

    # ------------------------------------------------------------------------------------------------------------------
    def end_block_node(self, command: str) -> None:
        """
        Signals the end of a block command.

        :param command: The name of the inline command.
        """
        # Pop none block command nodes from the stack.
        while self.nested_nodes and not self.nested_nodes[-1].is_block_command():
            self.nested_nodes.pop()

        if not self.nested_nodes:
            # @todo position
            raise RuntimeError(f"Unexpected \\end{{{command}}}.")

        # Get the last node on the block stack.
        node = self.nested_nodes[-1]

        if node.name != command:
            # @todo position \end
            # @todo position \begin
            raise RuntimeError(f"\\begin{{{node.name}}} and \\end{{{command}}} do not match.")

        # Pop the last node of the block stack.
        self.nested_nodes.pop()

    # ------------------------------------------------------------------------------------------------------------------
    def in_scope(self, node_id: int):
        """
        Retrieves a node based on its ID.

        :param int node_id: The node ID.
        """
        return self.nodes[node_id]

    # ------------------------------------------------------------------------------------------------------------------
    def out_scope(self, node):
        """
        Marks a node as no longer in scope.

        :param node: The node.
        """
        pass

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def register_inline_command(command: str, constructor) -> None:
        """
        Registers a node constructor for an inline command.

        :param command: The name of the inline command.
        :param callable constructor: The node constructor.
        """
        inline_creators[command] = constructor

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def register_formatter(command: str, output_format: str, formatter) -> None:
        """
        Registers an output formatter constructor for a command.

        :param command: The name of the command.
        :param output_format: The output format the formatter generates.
        :param callable formatter: The formatter for generating the content of the node in the output format.
        """
        if output_format not in formatters:
            formatters[output_format] = {}

        formatters[output_format][command] = formatter

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def register_block_command(command: str, constructor) -> None:
        """
        Registers a node constructor for a block command.

        :param command: The name of the inline command.
        :param callable constructor: The node constructor.
        """
        block_creators[command] = constructor

    # ------------------------------------------------------------------------------------------------------------------
    def create_inline_node(self,
                           command: str,
                           options: Dict[str, str] | None = None,
                           argument: str = '',
                           position: Position = None):
        """
        Creates a node based an inline command.

        Note: The node is not stored nor appended to the content tree.

        :param command: The inline command.
        :param options: The options.
        :param argument: The argument of the inline command.
        :param Position|None position: The position of the node definition.
        """
        if command not in inline_creators:
            # @todo set error status
            constructor = inline_creators['unknown']
            node = constructor(io=self._io, command=command)

        else:
            # Create the new node.
            constructor = inline_creators[command]
            node = constructor(io=self._io, options=options, argument=argument)

        node.position = position

        # Store the node and assign ID.
        self.store_node(node)

        return node

    # ------------------------------------------------------------------------------------------------------------------
    def create_block_node(self, command: str, options: Dict[str, str], position: Position):
        """
        Creates a node based on a block command.

        Note: The node is not appended to the content tree.

        :param command: The inline command.
        :param options: The options.
        :param Position position: The position of the node definition.
        """
        if command not in block_creators:
            constructor = block_creators['unknown']
            # @todo set error status

        else:
            # Create the new node.
            constructor = block_creators[command]

        node = constructor(io=self._io, options=options)
        node.position = position

        # Store the node and assign ID.
        self.store_node(node)

        return node

    # ------------------------------------------------------------------------------------------------------------------
    def append_inline_node(self, command: str, options: Dict[str, str], argument: str, position: Position):
        """
        Creates a node based an inline command and appends it to the end of the content tree.

        :param command: The inline command.
        :param options: The options.
        :param argument: The argument of the inline command.
        :param Position position: The position of the node definition.
        """
        # Create the inline node.
        node = self.create_inline_node(command, options, argument, position)

        # Add the node to the node store.
        self._append_to_content_tree(node)

        return node

    # ------------------------------------------------------------------------------------------------------------------
    def append_block_node(self, command: str, options: Dict[str, str], position: Position):
        """
        Creates a node based on a block command and appends it to the end of the content tree.

        :param command: The inline command.
        :param options: The options.
        :param Position position: The position of the node definition.
        """
        # Create the block node.
        node = self.create_block_node(command, options, position)

        # Add the node to the node store.
        self._append_to_content_tree(node)

        return node

    # ------------------------------------------------------------------------------------------------------------------
    def create_formatter(self, io: SDocIO, node, parent=None):
        """
        Creates a formatter for generating the output of nodes in the requested output format.

        :param io: The IO object.
        :param node: The SDoc2 node.
        :param parent: The parent formatter.
        """
        if self.format not in formatters:
            raise RuntimeError(f"Unknown output format '{self.format}'.")

        if node.name in formatters[self.format]:
            constructor = formatters[self.format][node.name]
        else:
            self.error(f"No formatter available for SDoc2 command \\{node.name}q", node)
            constructor = formatters[self.format]['none']

        formatter = constructor(io, parent)

        return formatter

    # ------------------------------------------------------------------------------------------------------------------
    def _adjust_hierarchy(self, node) -> None:
        """
        Adjust the hierarchy based on the hierarchy of a new node.

        :param node: The new node.
        """
        node_hierarchy_name = node.get_hierarchy_name()
        parent_found = False
        while self.nested_nodes and not parent_found:
            parent_node = self.nested_nodes[-1]
            parent_hierarchy_name = parent_node.get_hierarchy_name()
            if parent_hierarchy_name != node_hierarchy_name:
                if node.is_hierarchy_root():
                    parent_found = True
                else:
                    self.error(f"Improper nesting of node '{parent_node.name}' at {parent_node.position!s} and node '{node.name}' at {node.position!s}.")

            if not parent_found:
                parent_hierarchy_level = parent_node.get_hierarchy_level()
                node_hierarchy_level = node.get_hierarchy_level(parent_hierarchy_level)
                if parent_hierarchy_level >= node_hierarchy_level and len(self.nested_nodes) > 1:
                    self.nested_nodes.pop()
                else:
                    parent_found = True

        parent_node = self.nested_nodes[-1]
        parent_hierarchy_level = parent_node.get_hierarchy_level()
        node_hierarchy_level = node.get_hierarchy_level(parent_hierarchy_level)

        if node_hierarchy_level - parent_hierarchy_level > 1:
            self.error(
                f"Improper nesting of levels:{parent_hierarchy_level} at {parent_node.position!s} and {node_hierarchy_level} at {node.position!s}.",
                node)

    # ------------------------------------------------------------------------------------------------------------------
    def store_node(self, node) -> int:
        """
        Stores a node. If the node was not stored before assigns an ID to this node, otherwise the node replaces the
        node stored under the same ID. Returns the ID if the node.

        :param sdoc.sdoc2.node.Node.Node node: The node.
        """
        if not node.id:
            # Add the node to the node store.
            node_id = len(self.nodes) + 1
            node.id = node_id

        self.nodes[node.id] = node

        return node.id

    # ------------------------------------------------------------------------------------------------------------------
    def _append_to_content_tree(self, node) -> None:
        """
        Appends the node at the proper nesting level at the end of the content tree.

        :param sdoc.sdoc2.node.Node.Node node: The node.
        """
        if node.id == 1:
            # The first node must be a document root.
            if not node.is_document_root():
                # @todo position of block node.
                raise RuntimeError(f"Node {node.name} is not a document root.")

            self.nested_nodes.append(node)

        else:
            # All other nodes must not be a document root.
            if node.is_document_root():
                # @todo position of block node.
                raise RuntimeError(f"Unexpected {node.name}. Node is document root.")

            # If the node is a part of a hierarchy, adjust the nested nodes stack.
            if node.get_hierarchy_name():
                self._adjust_hierarchy(node)

            # Add the node to the list of child nodes of its parent node.
            if self.nested_nodes:
                parent_node = self.nested_nodes[-1]

                # Pop from stack if we have two list element nodes (e.g., item nodes) in a row.
                if node.is_list_element() and type(parent_node) == type(node):
                    self.nested_nodes.pop()
                    parent_node = self.nested_nodes[-1]

                parent_node.child_nodes.append(node.id)

            # Block commands and hierarchical nodes must be appended to the nested nodes.
            if node.is_block_command() or node.get_hierarchy_name():
                self.nested_nodes.append(node)

    # ------------------------------------------------------------------------------------------------------------------
    def prepare_content_tree(self) -> None:
        """
        Prepares after parsing at SDoc2 level the content tree for further processing.
        """
        # Currently, node with ID 1 is the document node. @todo Improve getting the document node.
        self.nodes[1].prepare_content_tree()

    # ------------------------------------------------------------------------------------------------------------------
    def number_numerable(self) -> None:
        """
        Numbers all numerable nodes such as chapters, sections, figures, and, items.
        """
        self.nodes[1].number(self._enumerable_numbers)

    # ------------------------------------------------------------------------------------------------------------------
    def generate_toc(self) -> None:
        """
        Checks if we have a table of contents in the document. If yes, we generate the table of contents.
        """
        for node in self.nodes.values():
            if node.name == 'toc':
                node.generate_toc()

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def generate(target_format) -> int:
        """
        Generates the document.

        :param sdoc.format.Format.Format target_format: The format which will generate file.
        """
        # Start generating file using specific formatter and check the errors.
        format_errors = target_format.generate()

        NodeStore._errors += format_errors

        return NodeStore._errors

    # ------------------------------------------------------------------------------------------------------------------
    def get_enumerated_items(self) -> List[Tuple[str, str]]:
        """
        Returns a list with tuples with command and number of enumerated nodes.

        This method is intended for unit test only.
        """
        return self.nodes[1].get_enumerated_items()

    # ------------------------------------------------------------------------------------------------------------------
    def parse_labels(self) -> None:
        """
        Method for parsing labels, setting additional arguments to nodes, and removing label nodes from tree.
        """
        self.nodes[1].parse_labels()
        self.nodes[1].change_ref_argument()

# ----------------------------------------------------------------------------------------------------------------------
