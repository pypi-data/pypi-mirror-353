# imports for typechecking
from __future__ import annotations
from typing import cast, Self, NewType

# imports the Term class depends on
from .rose_tree import RoseTree, Position

class Term(RoseTree[str]):
    """A Term is a variable (x,y,z,x_1,...) or a constant (c,0,1,...), or a f(t1,...,tn) where t1,...,tn are terms."""
    # if python was a typed language i would obviously like to enforce that a term can 
    # only have objects of type term as subTERMS, so that is_var and is_cons are defined.
    def __init__(self, varSymbol: str, subterms: list[Self]) -> None:
        """"Initializes the Term with a function symbol as its root and a NON EMPTY list of subterms."""
        if type(self) is Term and subterms == []:
            raise ValueError("Subterms must not be empty!")
        
        super().__init__(varSymbol, subterms)

    def __repr__(self) -> str:
        """Returns the string representation of a Term."""
        res =  "Term(" + repr(self.get_value()) + ", " + "[" + ", ".join([repr(rt) for rt in self.get_subtrees()]) + "])"
        return res

    def __str__(self) -> str:
        """Returns the Term in Ari-like format"""
        res = "(" + str(self.get_value()) + " " + " ".join([str(rt) for rt in self.get_subtrees()]) + ")"
        return res

    def get_subtrees(self) -> list[Self]:
        return super().get_subtrees()

    def get_subtree(self, position: Position) -> Term:
        return super().get_subtree(position)

    def set_subtree(self, position: Position, replacement: Self) -> Self:
        return super().set_subtree(position, replacement)

    def is_var(self) -> bool:
        return False
    
    def is_const(self) -> bool:
        return False

    def v(self) -> list[tuple[Position, Self]]:
        """Returns a list of all variables contained in self."""
        
        terms: list[tuple[Position, Self]] = [(Position([]), self)]
        variables: list[tuple[Position, Var]] = []

        while terms:
            pi, t = terms.pop(0)
            if isinstance(t, Var):
                variables += [(pi, t)]
            elif not isinstance(t, Const):
                terms += list(zip([pi + [i] for i in range(len(t))], t.get_subtrees()))

        return cast(list[tuple[Position, Self]], variables)

    def match(self, subjectTerm: Term) -> tuple[bool, Substitution]:
        """
        Computes if self matches subjectTerm in root position, and if so, the substitution.
        
        Parameters
        ----------
        subjectTerm: Term
            The term which it is attempted to find a substitution for the calling object for, 
            such that under the substituion the calling object matches subjectTerm.
        
        Returns
        ----------
        (match, substitution): term[bool, Substitution]
            match: True if terms match, False if terms do not match.
            substitution: The *matching substitution*. Empty if terms do not match.
        """
        if not isinstance(subjectTerm, Term):
            return (False, {})
        
        # a variable can be substituted to match anything
        if self.is_var():
            return (True, Substitution({self.get_value(): subjectTerm}))
        
        # a const only matches itself
        if self.is_const():
            return (self == subjectTerm, Substitution({}))
        

        # not a simple case, need to check rootsymbol, arity and then each subterm (and their subterms, and ...)
        if self.get_value() != subjectTerm.get_value() or len(self) != len(subjectTerm):
            return (False, Substitution({}))
        
        terms = list(zip(self.get_subtrees(), subjectTerm.get_subtrees())) # does not modify initial lists, zip to compare
        substitution = Substitution({}) # need to keep track of variable substitutions

        while terms:
            s, o = terms.pop(0)
            if s.is_var(): # a var has to be the same everywhere
                sVal = s.get_value()
                
                if sVal not in substitution: # add substitution
                    substitution.update({sVal: o})
                else: # sVal in substitution, need to check if o matches saved key
                    if o != substitution[sVal]:
                        return (False, Substitution({}))
                    else:
                        continue
            elif s.is_const(): # a const still only matches itself
                if s != o:
                    return (False, Substitution({}))
                else:
                    continue
            else: # s is a term, s needs to match o (under the current substitution)
                if s.get_value() == o.get_value() and len(s) == len(o):
                    terms += list(zip(s.get_subtrees(), o.get_subtrees()))
                else:
                    return (False, Substitution({}))
                
        # return substitution
        return (True, substitution)
    
    def apply_substitution(self, sigma: dict[str, Self]) -> Self:
        """
        Applies a substitution to a term by replacing the variables in Term by copies of the Terms specified in substituion.
        
        Parameters
        ----------
        sigma: Substitution
            list of (str, t), where str stands for a variable.
        
        Returns
        -------
            The calling term substituted by sigma.
        """
        vs = self.v()
        for pos, v in vs:
            self.set_subtree(pos, sigma.get(v.get_value(), v))

        return self



class Var(Term):
    """A Term is a variable (x,y,z,x_1,...) or a constant (c,0,1,...), or a f(t1,...,tn) where t1,...,tn are terms."""
    def __init__(self, const_symbol: str) -> None:
        """Initializes a variable with symbol varSymbol."""
        super().__init__(const_symbol, [])

    def __repr__(self) -> str:
        return "Var(" + repr(self.get_value()) + ")"
    
    def __str__(self) -> str:
        return self.value

    def is_var(self) -> bool:
        return True
    
    def is_const(self) -> bool:
        return False


class Const(Term):
    """A Term is a variable (x,y,z,x_1,...) or a constant (c,0,1,...), or a f(t1,...,tn) where t1,...,tn are terms."""
    def __init__(self, const_symbol: str) -> None:
        """Initializes a constant with symbol constSymbol."""
        super().__init__(const_symbol, [])
    
    def __repr__(self) -> str:
        return "Const(" + repr(self.get_value()) + ")"
    
    def __str__(self) -> str:
        return self.value

    def is_var(self) -> bool:
        return False
    
    def is_const(self) -> bool:
        return True
    

Substitution = NewType("Substitution", dict[str, Term])