from typing import Optional

from abc import ABC, abstractmethod
from .term import Term, Position, Substitution


class EvaluationStrategy(ABC):
    # Abstract class which define what any EvaluationStrategy does
    @abstractmethod
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        pass

class UniqueElementStrategy(EvaluationStrategy):
    # If there is a matching, select the only one
    def select_redex(self, patternTerm: Term, subjectTerm: Term) -> Optional[tuple[Position, Substitution] | None]:
        res = self.generate_redexes(patternTerm, subjectTerm)
        if res:
            return res[0]
        else:
            return None
class Full(EvaluationStrategy):
    """
    Computes all positions pi and substitutions sig such that patternTerm under the substitution sig matches the subterm at position pi. 
        (All pos. pi and subs. sig with self[sig] = other|pi).
    """
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        matchings: list[tuple[Position, Substitution]] = []
        
        for p, t in subjectTerm.level_order():
            match, substitution = patternTerm.match(t)

            if match:
                matchings += [(p, substitution)]

        return matchings

class Outermost(EvaluationStrategy):
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        # generate all redexes
        allReds = Full().generate_redexes(patternTerm, subjectTerm)

        # start with all redexes and filter
        oReds = allReds.copy()
        for s, _ in allReds:
            # remove any (r, sig) where s is a prefix of r
            oReds = [(r, sig) for r, sig in oReds if not s.is_true_prefix(r)]
        
        return oReds

class Innermost(EvaluationStrategy):
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        allReds = Full().generate_redexes(patternTerm, subjectTerm)
        
        iReds = allReds.copy()
        for p, _ in allReds:
            iReds = [(r, sig) for r, sig in iReds if not r.is_true_prefix(p)]
        
        return iReds


class LeftmostOutermost(UniqueElementStrategy):
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        for p, t in subjectTerm.pre_order():
            match, substitution = patternTerm.match(t)
            if match:
                return [(p, substitution)]
        
        return []

class LeftmostInnermost(UniqueElementStrategy):
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        for p, t in subjectTerm.post_order():
            match, substitution = patternTerm.match(t)
            if match:
                return [(p, substitution)]
            
        return []

class RightmostOutermost(UniqueElementStrategy):
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        for p, t in subjectTerm.reverse_pre_order():
            match, substitution = patternTerm.match(t)
            if match:
                return [(p, substitution)]
        
        return []

class RightmostInnermost(UniqueElementStrategy):
    def generate_redexes(self, patternTerm: Term, subjectTerm: Term) -> list[tuple[Position, Substitution]]:
        for p, t in subjectTerm.reverse_post_order():
            match, substitution = patternTerm.match(t)
            if match:
                return [(p, substitution)]
        
        return []