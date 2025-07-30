from typing import Dict

from sdoc import sdoc2
from sdoc.io.SDocIO import SDocIO
from sdoc.sdoc2.node.DateNode import DateNode
from sdoc.sdoc2.node.Node import Node
from sdoc.sdoc2.node.TitleNode import TitleNode
from sdoc.sdoc2.node.VersionNode import VersionNode
from sdoc.sdoc2.NodeStore import NodeStore


class DocumentNode(Node):
    """
    SDoc2 node for documents.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, *, io: SDocIO, options: Dict[str, str]):
        """
        Object constructor.

        :param io: The IO object.
        :param options: The options of this document.
        """
        Node.__init__(self, io=io, name='document', options=options)

        self.title_node_id: int | None = None
        """
        The ID of the node the title of the sdoc document.
        """

        self.date_node_id: int | None = None
        """
        The ID of the node the date of the sdoc document.
        """

        self.version_node_id: int | None = None
        """
        The ID of the node with the version of the sdoc document.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def get_hierarchy_level(self, parent_hierarchy_level: int = -1) -> int:
        """
        Returns 0.
        """
        return 0

    # ------------------------------------------------------------------------------------------------------------------
    def get_hierarchy_name(self) -> str:
        """
        Returns 'sectioning'.
        """
        return 'sectioning'

    # ------------------------------------------------------------------------------------------------------------------
    def is_block_command(self) -> bool:
        """
        Returns True.
        """
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def is_document_root(self) -> bool:
        """
        Returns True.
        """
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def is_inline_command(self) -> bool:
        """
        Returns False.
        """
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def is_phrasing(self) -> bool:
        """
        Returns False.
        """
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def prepare_content_tree(self) -> None:
        """
        Prepares this node for further processing.
        """
        for node_id in self.child_nodes:
            node = sdoc2.in_scope(node_id)

            node.prepare_content_tree()
            self.__set_document_info(node)

            sdoc2.out_scope(node)

        self.__remove_document_info_nodes()

    # ------------------------------------------------------------------------------------------------------------------
    def __set_document_info(self, node: Node) -> None:
        """
        Sets the info of a document (i.e., date, version or title) to DocumentNode attributes.

        :param node: The current node.
        """
        if isinstance(node, DateNode):
            self.__check_document_info(self.date_node_id, node)
            self.date_node_id = node.id

        elif isinstance(node, TitleNode):
            self.__check_document_info(self.title_node_id, node)
            self.title_node_id = node.id

        elif isinstance(node, VersionNode):
            self.__check_document_info(self.version_node_id, node)
            self.version_node_id = node.id

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __check_document_info(info_node_current: int | None, info_node_new: Node) -> None:
        """
        Checks if a document info node has been set already. If so, an error will be logged.

        :param int|None info_node_current: The current document info node (i.e., a property of the document).
        :param info_node_new: The (new) document info node.
        """
        if info_node_current:
            node = sdoc2.in_scope(info_node_current)
            position = node.position
            sdoc2.out_scope(node)

            NodeStore.error(f'Document info {info_node_new.name} can be specified only once. '
                            f'Previous definition at {position!s}.',
                            info_node_new)

    # ------------------------------------------------------------------------------------------------------------------
    def __remove_document_info_nodes(self):
        """
        Removes the nodes with document info from the list of child nodes.
        """
        obsolete_node_ids = [self.date_node_id, self.title_node_id, self.version_node_id]
        obsolete_node_ids = [node_id for node_id in obsolete_node_ids if node_id is not None]
        self._remove_child_nodes(obsolete_node_ids)


# ----------------------------------------------------------------------------------------------------------------------
NodeStore.register_block_command('document', DocumentNode)
