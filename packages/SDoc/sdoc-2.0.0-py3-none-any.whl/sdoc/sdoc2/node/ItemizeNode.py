import re
from typing import Dict

from sdoc import sdoc2
from sdoc.io.SDocIO import SDocIO
from sdoc.sdoc2.node.ItemNode import ItemNode
from sdoc.sdoc2.node.Node import Node
from sdoc.sdoc2.node.TextNode import TextNode
from sdoc.sdoc2.NodeStore import NodeStore


class ItemizeNode(Node):
    """
    SDoc2 node for itemize.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, *, io: SDocIO, options: Dict[str, str]):
        """
        Object constructor.

        :param io: The IO object.
        :param options: The options of this itemize.
        """
        Node.__init__(self, io=io, name='itemize', options=options)

        self._hierarchy_level: int = 0
        """
        The hierarchy level of the itemize.
        """

        sdoc2.node_store.first = True

    # ------------------------------------------------------------------------------------------------------------------
    def get_hierarchy_level(self, parent_hierarchy_level: int = -1) -> int:
        """
        Returns parent_hierarchy_level + 1.

        :param parent_hierarchy_level: The level of the parent in the hierarchy.
        """
        self._hierarchy_level = parent_hierarchy_level + 1

        return self._hierarchy_level

    # ------------------------------------------------------------------------------------------------------------------
    def get_hierarchy_name(self) -> str:
        """
        Returns 'item'
        """
        return 'item'

    # ------------------------------------------------------------------------------------------------------------------
    def is_block_command(self) -> bool:
        """
        Returns True.
        """
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def is_hierarchy_root(self):
        """
        Returns True.
        """
        return self._hierarchy_level == 0

    # ------------------------------------------------------------------------------------------------------------------
    def is_inline_command(self) -> bool:
        """
        Returns False.
        """
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def is_phrasing(self) -> bool:
        """
        Returns True.
        """
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def prepare_content_tree(self) -> None:
        """
        Method which checks if all child nodes are instances of sdoc.sdoc2.node.ItemNode.ItemNode.
        """
        obsolete_node_ids = []

        for node_id in self.child_nodes:
            child_node = sdoc2.in_scope(node_id)

            if isinstance(child_node, TextNode):
                # Ignore text nodes with only whitespace silently.
                if re.sub(r'\s+', '', child_node.argument) != '':
                    # This text node contains more than only whitespace.
                    sdoc2.node_store.error(f"Unexpected text '{child_node.argument}'.", child_node)
                obsolete_node_ids.append(node_id)

            elif not isinstance(child_node, ItemNode):
                # An itemize node can have only item nodes as direct child nodes.
                sdoc2.node_store.error(f"Node: id:{child_node.id}, {child_node.name} is not instance of 'ItemNode'.",
                                       child_node)
                obsolete_node_ids.append(node_id)

            else:
                child_node.prepare_content_tree()

            sdoc2.out_scope(child_node)

        self._remove_child_nodes(obsolete_node_ids)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def level_down(number: str) -> str:
        """
        Decrements the level of hierarchy.

        :param number: The number of the last node.
        """
        number_list = number.split('.')
        number = '.'.join(number_list[:-1])

        return number

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def level_up(numbers: Dict[str, str]) -> None:
        """
        Increments the level of hierarchy.

        :param numbers: The number of the last node.
        """
        if 'item' in numbers:
            numbers['item'] += '.0'
        else:
            numbers['item'] = '0'

    # ------------------------------------------------------------------------------------------------------------------
    def number(self, numbers: Dict[str, str]) -> None:
        """
        Passing over all child nodes, for numeration.

        :param numbers: The number of the last node.
        """
        self.level_up(numbers)

        Node.number(self, numbers)

        numbers['item'] = self.level_down(numbers['item'])


# ----------------------------------------------------------------------------------------------------------------------
NodeStore.register_block_command('itemize', ItemizeNode)
