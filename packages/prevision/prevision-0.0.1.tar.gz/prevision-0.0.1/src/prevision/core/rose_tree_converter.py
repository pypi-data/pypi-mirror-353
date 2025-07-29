from pydot import Dot, Edge, Node # type: ignore
from .rose_tree import RoseTree
from .ptrs_comp_tree_data import TreeData, ResultTreeData, NonDeterminismData

class RTConv:
    def __init__(self):
        pass

    def rt_to_pd(self, tree: RoseTree[TreeData]) -> Dot:
        """
        Converts a RoseTree to a clean pydot graph.
        """
        graph = Dot(
            graph_type="digraph",
            overlap="false",       # prevent node overlaps
            rankdir="LR",
            ranksep="0.3",
            nodesep="0.2"
        )
        
        # add nodes 
        for p1, rt in tree.level_order():
            nodeID = str(p1)
            data = rt.get_value()
            if isinstance(data, NonDeterminismData):
                node = Node(
                    nodeID,
                    label=str(data),
                    shape="box",
                    fontname="Courier",
                    style="filled,solid",
                    color="#fdd58f"
                )
            else:
                node = Node(
                    nodeID,
                    label=str(data),
                    shape="box",
                    fontname="Courier",
                )

            graph.add_node(node)
        
        for p1, rt in tree.level_order():
            for i, c in enumerate(rt.get_subtrees()):
                p2 = p1 + [i]
                edge = Edge(
                    str(p1),
                    str(p2),
                    color="black",    # black edges
                    penwidth="0.8"    # thinner for elegance
                )
                graph.add_edge(edge)
        
        return graph