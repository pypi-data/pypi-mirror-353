from .rose_tree import RoseTree, Position
from .term import Term
from .ptrs_comp_tree_data import TreeData, NonDeterminismData, ResultTreeData
from .prule import PRule
from .evaluation_strategy import EvaluationStrategy, UniqueElementStrategy, LeftmostOutermost, Full

from itertools import product
from copy import deepcopy

class Ptrs:
    def __init__(self, prules: list[PRule]) -> None:
        # TODO need to handle empty ptrs?
        self.prules = {f"R{i}": prule for i, prule in enumerate(prules)}

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Ptrs):
            return all([pRule in other.get_prules() for pRule in self.get_prules()])
        return False

    def __str__(self) -> str:
        res = "PTRS contains the following rules:\n"
        res += "\n".join([f"R{i}: " + str(rule) for i, rule in enumerate(self.get_prules())])
        return res

    def __repr__(self) -> str:
        res = f"PTRS({repr(self.get_prules())})"
        return res

    def get_prules(self) -> list[PRule]:
        return list(self.prules.values())
    
    def non_probabilistic_deterministic_path(self, t: Term, depth: float = 3, strategy: UniqueElementStrategy = LeftmostOutermost()) -> RoseTree[TreeData]:
        """
        Calculates a reduction sequence with regard to the PTRS.
        The result is then a nonprobabilistic deterministic path where every term has at most one reduction.

        Parameters
        ----------
        t: Term
            The term which is the beginning of the reduction sequence.
        depth: float, optional
            The maximum number of reductions that are allowed. If depth equals inf, then the function will run until a normal form is found (potentially forever).
        strategy: UniqueElementStrategy
            The evaluationstrategy which choses which redex is contracted.

        Returns
        -------
        RoseTree[TreeData]
        """
        # no side effects on t
        t_0 = deepcopy(t)

        treeData = ResultTreeData(None, 1, t_0, None, "")
        root: RoseTree[TreeData] = RoseTree(treeData, [])

        # store last node in path, the next derived term becomes the child node
        curNode = root
        
        modified = True
        layerIdx = 0
        while modified and layerIdx < depth:
            layerIdx += 1
            modified = False
            
            # get term from last node
            _, curProb, curTerm, _, _ = curNode.get_value().data
            
            # try to apply any rule
            for prule in self.get_prules(): # TODO: Document: non determinisms in this method are chosen deterministically
                
                res = strategy.select_redex(prule.get_lhs(), curTerm)
                
                if res is not None:
                    modified = True
                    
                    pos, sub = res
                    prob, resultingTerm = prule.apply(deepcopy(curTerm), pos, sub)
                    nxtNode: RoseTree[TreeData] = RoseTree(ResultTreeData(prule, curProb * prob, resultingTerm, pos, ""), [])
                    
                    curNode.set_subtrees([nxtNode])
                    curNode = nxtNode
                    break
    
        # normal_form = not modified
        
        return root
    
    def non_probabilistic_non_deterministic_trees(self, t: Term, depth: int = 3, strategy: EvaluationStrategy = Full()) -> list[RoseTree]:
        t_0 = deepcopy(t)

        # create the first root node
        treeData = ResultTreeData(None, 1, t_0, None, "")
        root: RoseTree[TreeData] = RoseTree(treeData, [])     
        

        # two lists, one for storing the curLayer (work until empty and put new trees in nxtLayer)
        curLayer: list[tuple[RoseTree[TreeData], list[RoseTree[TreeData]]]]
        nxtLayer: list[tuple[RoseTree[TreeData], list[RoseTree[TreeData]]]]
        curLayer = []                       # currently not working on anything
        nxtLayer = [(root, [root])]        # will be working on the root next (layer 1)

        # expand tree until reaching depth
        layerIdx = 0
        while layerIdx < depth:
            layerIdx += 1
            
            curLayer = nxtLayer    # start work on the curLayer, previously nxtLayer
            nxtLayer = []          # nxtLayer empty at this point
            
            # work through all trees of the curLayer, each possibly sprouting its own trees of the nxtLayer
            while curLayer:
                curRoot, curLeafs = curLayer.pop(0) # get the next tree and its leafs
                
                distributionList: list[list[tuple[RoseTree[TreeData], RoseTree[TreeData]]]] = []
                for leaf in curLeafs:
                    # we are working on the data stored inside the nodes of the derivation tree
                    # i.e., the terms, with their prior calculated probability
                    _, curProb, cTerm, _, _ = leaf.get_value().data
                    
                    children: list[RoseTree] = []
                    for name, prule in list(self.prules.items()):
                        filteredRedexes = strategy.generate_redexes(prule.get_lhs(), cTerm)

                        for pos, sub in filteredRedexes:
                            # create this node to visualize the unresolved nondeterminism
                            nonDeterminismNode: RoseTree[TreeData] = RoseTree(NonDeterminismData(name, pos), [])
                            # add it to the list of children for this leaf
                            children += [nonDeterminismNode]
                            
                            # create the distribution for this nonDeterminism
                            resultingTerms: list[tuple[float, Term]] = prule.apply_distribution_at(cTerm, pos, sub)
                            distribution: list[RoseTree[TreeData]] = [RoseTree(ResultTreeData(prule, curProb * prob, t, pos, ""), []) for prob, t in resultingTerms]
                            distributionList += [[(nonDeterminismNode, event) for event in distribution]]
                            
                    # need to add children to leaf
                    leaf.set_subtrees(children)
                    
                # build cartesian product of distributionList
                cartesianProduct = list(product(*distributionList))

                for combination in cartesianProduct:
                    
                    for node, child in combination:
                        node.set_subtrees([child])
                
                    # the curRoot sprouts a new tree
                    newTree = deepcopy(curRoot)
                    newLeafs = newTree.get_last_layer_nodes()
                    # add the new tree and its leafs to the next layer
                    nxtLayer += [(newTree, newLeafs)]
                            


        return [tree for tree, _ in nxtLayer]


    def probabilistic_deterministic_trees(self, t: Term, depth: int = 3, strategy: EvaluationStrategy = Full()) -> list[RoseTree]:
        t_0 = deepcopy(t)

        # create the first root node
        treeData = ResultTreeData(None, 1, t_0, None, "")
        root: RoseTree[TreeData] = RoseTree(treeData, [])     
        

        # two lists, one for storing the curLayer (work until empty and put new trees in nxtLayer)
        curLayer: list[tuple[RoseTree[TreeData], list[RoseTree[TreeData]]]]
        nxtLayer: list[tuple[RoseTree[TreeData], list[RoseTree[TreeData]]]]
        curLayer = []                       # currently not working on anything
        nxtLayer = [(root, [root])]        # will be working on the root next (layer 1)

        # expand tree until reaching depth
        layerIdx = 0
        while layerIdx < depth:
            layerIdx += 1
            
            curLayer = nxtLayer    # start work on the curLayer, previously nxtLayer
            nxtLayer = []          # nxtLayer empty at this point
            
            # work through all trees of the curLayer, each possibly sprouting its own trees of the nxtLayer
            while curLayer:
                curRoot, curLeafs = curLayer.pop(0) # get the next tree and its leafs

                """ 
                    Store a list xss of lists xs_i, where each entry x_ij of xs_i is a tuple (leaf_i, dist_j), with dist_j applicable at the i-th leaf, e.g.:
                    xs_1 = [(leaf_1, dist_1), (leaf_1, dist_2), (leaf_1, dist_3), ...]
                    xs_2 = [(leaf_2, dist_1), (leaf_2, dist_2), ...]
                    xss = [xs_1, xs_2, ...]
                    We will build the cartesian product of this list to get the different trees 
                    corresponding to the different options of combining the nondeterminisms.
                    Basically, the tuples are (parent, possibleChildren) = one nonDeterminism.
                    nonDeterminismsList is a list of nonDeterminisms: [nonDeterminisms] or [[nonDeterminism]]
                    So nonDeterminisms is a list of nonDeterminism [nonDeterminism].
                """
                nonDeterminismsList: list[list[tuple[RoseTree[TreeData], list[RoseTree[TreeData]]]]] = []
                for leaf in curLeafs:
                    # we are working on the data stored inside the nodes of the derivation tree
                    # i.e., the terms, with their prior calculated probability
                    _, curProb, cTerm, _, _ = leaf.get_value().data

                    # store all distributions applicable at leaf, e.g. a list of nonDeterminism
                    nonDeterminisms: list[tuple[RoseTree[TreeData], list[RoseTree[TreeData]]]] = []
                    
                    for _, prule in list(self.prules.items()):
                        filteredRedexes = strategy.generate_redexes(prule.get_lhs(), cTerm)

                        for pos, sub in filteredRedexes:
                            # apply a distribution at each nonDeterminism
                            distribution = prule.apply_distribution_at(cTerm, pos, sub)
                            # convert the distribution into compatible subtrees that can be children of leaf
                            nonDeterminism: list[RoseTree[TreeData]] = [RoseTree(ResultTreeData(prule, curProb * prob, t, pos, ""), []) for prob, t in distribution]
                            nonDeterminisms += [(leaf, nonDeterminism)]

                    """
                        Now nonDeterminisms contains all nonDeterminisms applicable at leaf.
                        If there is not a single nonDeterminism (i.e. nonDeterminisms empty),
                        we must not put it into the list to prevent the cartesian from being empty.
                    """
                    if nonDeterminisms:
                        nonDeterminismsList += [nonDeterminisms]

                """
                    Build the cartesian product of the nonDeterminisms:
                    With the notation from above cartesianProduct = [((leaf_1, dist_11), (leaf_2, dist_21), ...), ...]
                """
                cartesianProduct = list(product(*nonDeterminismsList))

                # now we apply each combination for the current computation tree (curRoot)
                for combination in cartesianProduct:
                    
                    for node, children in combination:
                        node.set_subtrees(children)
                    
                    # the curRoot sprouts a new tree
                    newTree = deepcopy(curRoot) 
                    newLeafs = newTree.get_last_layer_nodes()
                    # add the new tree and its leafs to the next layer
                    nxtLayer += [(newTree, newLeafs)]
                    

        return [tree for tree, _ in nxtLayer]

    def probabilistic_non_deterministic_tree(self, t: Term, layerCount: int = 3, strategy: EvaluationStrategy = Full()) -> RoseTree:
        
        # starting term, root, do not modify t
        t_0 = deepcopy(t)

        # create first tree which saves trees (visualization etc.)
        treeData = ResultTreeData(None, 1, t_0, None, "")
        root: RoseTree = RoseTree(treeData, [])
        
        # add root to trees list
        curLayer = [root]
        # keep going until trees is empty -> we have finished one layer
        while layerCount > 0:
            # we will finish one layer of terms in this loop
            layerCount -= 1
            # save the trees, containing terms, which need to be processed in the next loop
            nxtLayer = []
            
            # process all trees in current layer
            while curLayer:
                # process one tree at a time
                cTree = curLayer.pop(0)
                # get the important information, cp (probability), ct (term)
                _, cp, cTerm, _, _ = cTree.get_value().data
                # list to store all the children of the current tree
                children: list[RoseTree] = []
                
                # apply all possible rules and positions filtered by the strategy
                for name, prule in list(self.prules.items()):
                    
                    # computing redexes where distribution can be applied given a strategy
                    filteredRedexes = strategy.generate_redexes(prule.get_lhs(), cTerm)

                    for pos, sub in filteredRedexes:
                        # one (prule, pos) per loop, makes one layer of resolving nondeterminism
                        nonDeterminismNode: RoseTree = RoseTree(NonDeterminismData(name, pos), [])
                        children += [nonDeterminismNode]
                        
                        # apply distribution at nonDeterminismNode (so in the tree, the next term layer)
                        resultingTerms: list[tuple[float, Term]] = prule.apply_distribution_at(cTerm, pos, sub)
                        
                        # store children of nonDeterminismNode
                        grandChildren: list[RoseTree] = []
                        
                        for prob, t in resultingTerms:
                            grandChildren += [RoseTree(ResultTreeData(prule, cp * prob, t, pos, ""), [])]
                        nonDeterminismNode.set_subtrees(grandChildren)
                        nxtLayer += grandChildren
                
                # add the children to current Tree
                cTree.set_subtrees(children)
                
            
            curLayer = nxtLayer
        
        
        return root