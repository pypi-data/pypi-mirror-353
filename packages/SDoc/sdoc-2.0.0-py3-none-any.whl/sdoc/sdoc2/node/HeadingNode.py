from abc import ABC
from typing import Any, Dict

import sdoc
from sdoc import sdoc2
from sdoc.io.SDocIO import SDocIO
from sdoc.sdoc2.helper.Enumerable import Enumerable
from sdoc.sdoc2.node.EndParagraphNode import EndParagraphNode
from sdoc.sdoc2.node.Node import Node
from sdoc.sdoc2.node.TextNode import TextNode
from sdoc.sdoc2.NodeStore import NodeStore


class HeadingNode(Node, ABC):
    """
    Abstract class for heading nodes.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, *, io: SDocIO, name: str, options: Dict[str, str], argument: str):
        """
        Object constructor.

        :param io: The IO object.
        :param name: The (command) name of this heading.
        :param options: The options of this heading.
        :param argument: The title of this heading.
        """
        Node.__init__(self, io=io, name=name, options=options, argument=argument)

        self.numbering: bool = True
        """
        The True the node must be numbered.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def get_hierarchy_name(self) -> str:
        """
        Returns 'sectioning'.
        """
        return 'sectioning'

    # ------------------------------------------------------------------------------------------------------------------
    def is_block_command(self) -> bool:
        """
        Returns False.
        """
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def is_inline_command(self) -> bool:
        """
        Returns True.
        """
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def number(self, enumerable_numbers: Dict[str, Any]):
        """
        Sets number of heading nodes.

        :param enumerable_numbers:
        """
        if 'heading' not in enumerable_numbers:
            enumerable_numbers['heading'] = Enumerable()

        enumerable_numbers['heading'].generate_numeration(self.get_hierarchy_level())
        enumerable_numbers['heading'].increment_last_level()
        enumerable_numbers['heading'].remove_starting_zeros()

        if 'part' in enumerable_numbers:
            self._options['part_number'] = enumerable_numbers['part'].get_string()

        self._options['number'] = enumerable_numbers['heading'].get_string()

        Node.number(self, enumerable_numbers)

    # ------------------------------------------------------------------------------------------------------------------
    def set_toc_id(self) -> None:
        """
        Set ID for table of contents.
        """
        if 'id' not in self._options:
            if 'part_number' in self._options:
                self._options['id'] = f'{self.name}:{self._options["part_number"]}:{self._options["number"]}'
            else:
                self._options['id'] = f'{self.name}:{self._options["number"]}'

    # ------------------------------------------------------------------------------------------------------------------
    def prepare_content_tree(self) -> None:
        """
        Prepares the content tree. Create paragraph nodes.
        """
        Node.prepare_content_tree(self)

        self.set_numbering()

        # Adding the id's of split text in 'new_child_nodes1' list.
        self.split_text_nodes()

        # Creating paragraphs and add all id's in 'new_child_nodes2' list.
        self.create_paragraphs()

    # ------------------------------------------------------------------------------------------------------------------
    def set_numbering(self) -> None:
        """
        Sets the numbering status to the heading node.
        """
        if 'numbering' in self._options:
            if self._options['numbering'] == 'off':
                self.numbering = False
            elif self._options['numbering'] == 'on':
                self.numbering = True
            else:
                NodeStore.error("Invalid value '{}' for attribute 'numbering'. Allowed values are 'on' and 'off'.".
                                format(self._options['numbering']), self)

    # ------------------------------------------------------------------------------------------------------------------
    def split_text_nodes(self) -> None:
        """
        Replaces single text nodes that contains a paragraph separator (i.e., a double new line) with multiple text
        nodes without a paragraph separator.
        """
        new_child_nodes = []

        for node_id in self.child_nodes:
            node = sdoc2.in_scope(node_id)

            if isinstance(node, TextNode):
                list_ids = node.split_by_paragraph()
                for ids in list_ids:
                    new_child_nodes.append(ids)
            else:
                new_child_nodes.append(node.id)

            sdoc2.out_scope(node)

        self.child_nodes = new_child_nodes

    # ------------------------------------------------------------------------------------------------------------------
    def create_paragraphs(self) -> None:
        """
        Create paragraph nodes.

        A paragraph consists of phrasing nodes only. Each continuous slice of phrasing child nodes is moved to a
        paragraph node.
        """
        new_child_nodes = []
        paragraph_node = None

        for node_id in self.child_nodes:
            node = sdoc2.in_scope(node_id)

            if node.is_phrasing():
                if not paragraph_node:
                    paragraph_node = sdoc.sdoc2.node_store.create_inline_node('paragraph')
                    new_child_nodes.append(paragraph_node.id)

                paragraph_node.append_child_node(node)
            else:
                if paragraph_node:
                    paragraph_node.prune_whitespace()
                    sdoc.sdoc2.node_store.store_node(paragraph_node)
                    paragraph_node = None

                # End paragraph nodes are created temporary to separate paragraphs in a flat list of (text) node. There
                # role is replaced by the content hierarchy now. So, we must not store end paragraph nodes.
                if not isinstance(node, EndParagraphNode):
                    new_child_nodes.append(node.id)

            sdoc2.out_scope(node)

        if paragraph_node:
            paragraph_node.prune_whitespace()
            sdoc.sdoc2.node_store.store_node(paragraph_node)
            # paragraph_node = None

        # Setting child nodes.
        self.child_nodes = new_child_nodes

    # ------------------------------------------------------------------------------------------------------------------
    def print_info(self, level: int) -> None:
        """
        Temp function for development.

        :param level: The level of block commands.
        """
        self._io.write_line(f"{' ' * 4 * level}{self.id} {self.name} {self.argument.replace("\n", '\\n')}")

        for node_id in self.child_nodes:
            node = sdoc2.in_scope(node_id)

            node.print_info(level + 1)

            sdoc2.out_scope(node)

# ----------------------------------------------------------------------------------------------------------------------
