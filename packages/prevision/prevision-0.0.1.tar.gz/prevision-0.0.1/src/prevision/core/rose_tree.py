# typing imports
from __future__ import annotations
from typing import Generator
from typing import Self # Using: PEP 673 – Self Type, a TypeVar bound to the class it is used in.

from copy import deepcopy


class Position:
    def __init__(self, indices: list[int]):
        self.indices = indices

    def __add__(self, other: Position | list[int]) -> Position:
        if isinstance(other, Position):
            return Position(self.indices + other.indices)
        elif isinstance(other, list):
            return Position(self.indices + other)
        else:
            raise TypeError("Can only add Position or list[int] to Position")

    def __radd__(self, other: list[int]) -> 'Position':
        # Allow a list of integers to be added to a Position
        if isinstance(other, list):
            return Position(other + self.indices)
        else:
            raise TypeError("Can only add list[int] to Position")
        
    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, key):
        return self.indices[key]

    def __eq__(self, other) -> bool:
        if isinstance(other, list):
            return self.indices == other
        elif isinstance(other, Position):
            return self.indices == other.indices
        else:
            return False

    def is_true_prefix(self, other: Position) -> bool:
        return len(other) > len(self) and other[:len(self)] == self.indices

    def __str__(self) -> str:
        return str(self.indices)

    def __repr__(self) -> str:
        return f"Position({self.indices})"

class RoseTree[V]:
    """A Tree with arbitrary depth, and arbitrary degree for storing a type T."""
    def __init__(self, value: V, subtrees: list[Self]) -> None:
        """Initializes the tree with a value of type T and a list of subtrees of type Tree."""
        self.value = value
        self.subtrees = subtrees

    def __len__(self) -> int:
        """Returns the number of subtrees."""
        return len(self.subtrees)
    
    def __str__(self) -> str:
        res = ""
        # child stack
        cs = [[self]]
        while cs:
            # take last list in stack (ccs, "current child stack")
            ccs = cs[-1]

            # if it is empty all children of current level have been consumed
            if not ccs:
                cs.pop()
            
            else:
                # take first of the ccs (ct, "current tree")
                ct = ccs.pop(0)
                # create indent of length cs-1
                indent = "  " * (len(cs)-1)
                res += f"{indent}+- {ct.get_value()}\n"
                # if ct has children, add new childstack
                if len(ct) > 0:
                    cs += [ct.get_subtrees().copy()]
            

        return res
    
    def __repr__(self) -> str:
        """Returns the string representation of a RoseTree."""
        res = "RoseTree(" + repr(self.get_value()) + ", " + "[" + ", ".join([repr(rt) for rt in self.get_subtrees()]) + "])"
        return res

    def __eq__(self, other: object) -> bool:
        """True if RoseTree objects are equal, false otherwise."""
        if isinstance(other, RoseTree):
            if self.get_value() == other.get_value():
                if len(self) == len(other):
                    return all([x == y for (x,y) in zip(self.get_subtrees(), other.get_subtrees())])
        return False
    
    def pre_order(self, pos: Position = Position([])) -> Generator[tuple[Position, Self], None, None]:
        """
        Generate a pre-order traversal of the tree.

        Parameters
        ----------
        pos : Position, optional
            Parameter which helps to compute the correct positions of the yielded trees.
            pos is the Position which self is assumed to have.

        Yields
        ------
        tuple[Position, Self]
            A tuple containing the current position and the current tree (self) at that position.
        """
        yield (pos, self)
        for nP, tree in enumerate(self.get_subtrees()):
            yield from tree.pre_order(pos + [nP])

    def reverse_pre_order(self, pos: Position = Position([])) -> Generator[tuple[Position, Self], None, None]:
        """
        Generate a reverse pre-order traversal of the tree.

        Parameters
        ----------
        pos : Position, optional
            Parameter which helps to compute the correct positions of the yielded trees.
            pos is the Position which self is assumed to have.

        Yields
        ------
        tuple[Position, Self]
            A tuple containing the current position and the current tree (self) at that position.
        """
        yield (pos, self)
        for nP, tree in list(enumerate(self.get_subtrees()))[::-1]:
            yield from tree.reverse_pre_order(pos + [nP])

    def post_order(self, pos: Position = Position([])) -> Generator[tuple[Position, Self], None, None]:
        """
        Generate a post-order traversal of the tree.

        Parameters
        ----------
        pos : Position, optional
            Parameter which helps to compute the correct positions of the yielded trees.
            pos is the Position which self is assumed to have.

        Yields
        ------
        tuple[Position, Self]
            A tuple containing the current position and the current tree (self) at that position.
        """
        for nP, tree in enumerate(self.get_subtrees()):
            yield from tree.post_order(pos + [nP])
        yield (pos, self)

    def reverse_post_order(self, pos: Position = Position([])) -> Generator[tuple[Position, Self], None, None]:
        """
        Generate a reverse pre-order traversal of the tree.

        Parameters
        ----------
        pos : Position, optional
            Parameter which helps to compute the correct positions of the yielded trees.
            pos is the Position which self is assumed to have.

        Yields
        ------
        tuple[Position, Self]
            A tuple containing the current position and the current tree (self) at that position.
        """
        for nP, tree in list(enumerate(self.get_subtrees()))[::-1]:
            yield from tree.reverse_post_order(pos + [nP])
        yield (pos, self)

    def level_order(self, pos: Position = Position([])) -> Generator[tuple[Position, Self], None, None]:
        """
        Generate a level-order traversal of the tree (Breadth-first search).

        Parameters
        ----------
        pos : Position, optional
            Parameter which helps to compute the correct positions of the yielded trees.
            pos is the Position which self is assumed to have.

        Yields
        ------
        tuple[Position, Self]
            A tuple containing the position pos and the current tree (self).
        """
        queue = [(pos, self)]
        while queue:
            curPos, curTree = queue.pop(0)
            queue += list(zip([curPos + [nP] for nP in range(len(curTree))], curTree.get_subtrees()))
            yield (curPos, curTree)

    def get_last_layer_nodes(self) -> list[Self]:
        """
        Returns the all those leafs of the tree which are at maximum depth.

        Returns
        -------
        list[RoseTree[V]]
        """
        curLayer:   list[Self] = []
        nextLayer:  list[Self] = [self]

        while nextLayer:
            
            curLayer = nextLayer
            nextLayer = []
            
            for subTree in curLayer:
                nextLayer += subTree.get_subtrees()
            
        return curLayer


    def get_value(self) -> V:
        """Returns the value."""
        return self.value

    def get_subtrees(self) -> list[Self]:
        """Returns the list of subtrees of this RoseTree."""
        return self.subtrees
    
    def get_subtree(self, position: Position) -> Self:
        """Returns a specific subtree at any depth/location."""
        if not position:
            return self
        
        cur = self
        for idx in position.indices:
            cur = cur.get_subtrees()[idx]

        return cur
    
    def set_value(self, value: V) -> None:
        """Sets this trees root value."""
        self.value = value

    def set_subtrees(self, subtrees: list[Self]) -> None:
        """Sets this trees list of subtrees."""
        self.subtrees = subtrees
            
    def set_subtree(self, position: Position, replacement: Self) -> Self:
        """
        This method **replaces** a (sub)tree of self by modifying self. A copy of replacement is inserted.
        
        Parameters
        ----------
        position: Position
            The position at which the replacement tree is to be inserted. .
        replacement: Tree
            The replacement tree.
        
        Returns
        ----------
        Tree, where a copy of replacement is inserted at position, or, if position == [] (specifies root), 
        returns self but with the attributes of a copy of replacement.
        """
        newSub = deepcopy(replacement)
        
        if not position:
            self.__class__ = newSub.__class__ # question: Is this ok to solve being able to replace self?
            self.set_value(newSub.get_value())
            self.set_subtrees(newSub.get_subtrees())
        else:
            sub = self.get_subtree(Position(position[:-1]))
            sub.get_subtrees()[position[-1]] = newSub
        
        return self