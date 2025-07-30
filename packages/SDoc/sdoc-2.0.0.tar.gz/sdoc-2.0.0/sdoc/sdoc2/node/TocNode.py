from typing import Dict

from sdoc import sdoc2
from sdoc.io.SDocIO import SDocIO
from sdoc.sdoc2.node.HeadingNode import HeadingNode
from sdoc.sdoc2.node.Node import Node
from sdoc.sdoc2.node.ParagraphNode import ParagraphNode
from sdoc.sdoc2.NodeStore import NodeStore


class TocNode(Node):
    """
    SDoc2 node for table of contents.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, *, io: SDocIO, options: Dict[str, str], argument: str):
        """
        Object constructor.

        :param io: The IO object.
        :param options: The options of this table of contents.
        :param argument: The argument of this TOC.
        """
        Node.__init__(self, io=io, name='toc', options=options, argument=argument)

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
    def generate_toc(self) -> None:
        """
        Generates the table of contents.
        """
        self._options['ids'] = []

        for node in sdoc2.node_store.nodes.values():
            if not isinstance(node, ParagraphNode) and isinstance(node, HeadingNode):
                node.set_toc_id()

                data = {'id':        node.get_option_value('id'),
                        'arg':       node.argument,
                        'level':     node.get_hierarchy_level(),
                        'number':    node.get_option_value('number'),
                        'numbering': node.numbering}

                self._options['ids'].append(data)


# ----------------------------------------------------------------------------------------------------------------------
NodeStore.register_inline_command('toc', TocNode)
