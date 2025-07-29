from .rose_tree import Position
from .term import Term, Substitution
from copy import deepcopy
from random import choices


# Distribution = NewType("Distribution", list[tuple[float, Term]])
class Distribution:
    def __init__(self, weightedTerms: list[tuple[int, Term]]):
        # normalize
        weights, terms = zip(*weightedTerms)
        self.norm = sum(weights)
        if self.norm == 0:
            raise ValueError("The sum over all probabilities in a distribution must be equal to one.")
        probabilities = [x / self.norm for x in weights]
        
        # store
        self.values: tuple[tuple[int, Term]] = tuple(zip(probabilities, terms)) # type: ignore

    def get_values(self):
        return self.values
    
    def __str__(self):
        res = "{\n"
        for prob, term in self.get_values():
            res += f"   {prob}: {term}\n"
        return res + "}"
    
    def __eq__(self, other):
        if isinstance(other, Distribution):
            return self.get_values() == other.get_values() and self.norm == other.norm
        return False


# need to store q, r in N, probability = q/r,


class PRule:
    def __init__(self, lhs: Term, weightedTerms: list[tuple[int, Term]], cost: float) -> None:
        # PRule valid if: V(r_i) \subseteq V(l) and l not in V for each r_i in distribution [0.5, r_1, 0.2, r_2, ...]
        for _, rhs in weightedTerms:
            if (not (set(y.get_value() for (_,y) in rhs.v()) <= set(y.get_value() for (_,y) in lhs.v()))) or lhs.is_var():
                raise ValueError("This is not a valid PRule, a violation of V(r) subseteq V(l) and l not in Vars has been found!")

        self.lhs = lhs
        self.distribution = Distribution(weightedTerms)
        self.cost = cost

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PRule):
            return self.lhs == other.lhs and self.distribution == other.distribution
        return False
    
    def __str__(self) -> str:
        res = f"{self.lhs} -> {self.distribution}"
        return res
    
    def __repr__(self) -> str:
        res = f"PRule({repr(self.lhs)}, {repr(self.distribution)})"
        return res

    def get_lhs(self):
        return self.lhs

    def get_distribution(self):
        return self.distribution

    def choose(self) -> tuple[float, Term]:
        """
        Chooses a term by a given weight.
        :return: 
            A Term
        """
        weights, terms = zip(*self.distribution.get_values())
        return choices(self.distribution.get_values(), weights, k=1)[-1]
        
    def apply(self, subjectTerm: Term, pos: Position, sub: Substitution) -> tuple[float, Term]:
        """
        Applys the rule probabilistically. Evaluates the distribution and choses a term rhs.\\
        **Modifies subjectTerm by inserting rhs under the substitution sub at pos. (Sideeffect!)**\\
        **Does not check if this application is valid, i.e. if lhs matches subjectTerm at pos**.
        
        
        Parameters
        ----------
        subjectTerm: Term
            The term which the rule is applied to probabilistically.
        pos: Position
            The position at which the rule is applied.
        sub: Substitution
            A substitution which is applied to the chosen term.

        Returns
        -------
        Term
            The result of inserting the [rhs]sub at subjectTerm|pos
        """
        
        # choose a replacement term (r) from the distribution and deepcopy term to prevent modifying the rule
        prob, r = self.choose()
        # do not modify it
        r = deepcopy(r)

        # apply substitution to copied term
        r = r.apply_substitution(sub)

        # set subtree at position (modifies candidate)
        subjectTerm.set_subtree(pos, r)

        return (prob, subjectTerm)
    

    # def apply_distribution(self, candidate: Term, strategy: EvaluationStrategy) -> list[Term]:
    #     # TODO: Document (no?) SIDE EFFECT on candidate!!

    #     lhs = self.get_lhs()

    #     # compute where lhs can be applied
    #     redexes = lhs.match_all(candidate) # possibly multiple (pi, sig) with lhs[sig] = candidate|pi
        
    #     # select one of the redexes to contract
    #     redex = strategy.select_redex(strategy.pre_order_sort(redexes))
        
    #     # Check for no matchings found (res == None)
    #     if redex is None:
    #         return []
        
    #     # redex has been found
    #     pos, sub = redex # position of where lhs can be applied and the substitution under which it can be applied
    #     res: list[Term] = [] # list which stores all possible modifications of candidate under the distribution
        
    #     weights, terms = zip(*self.get_distribution().get_values())
    #     # evaluate candidate under the distribution
    #     for term in terms:
    #         # do not modify terms in distribution or candidate
    #         r, c = deepcopy(term), deepcopy(candidate)
    #         # apply substitution to r (copy of term)
    #         r = r.apply_substitution(sub)
    #         # set subtree at position (modifies c)
    #         c.set_subtree(pos, r)
    #         # add to res
    #         res.append(c)

    #     return res
    
    def apply_distribution_at(self, subjectTerm: Term, pos: Position, sub: Substitution) -> list[tuple[float, Term]]:
        """
        Applys the whole distribution with their probabilities.\\
        Does not modify subjectTerm.\\
        **Does not check if this application is valid, i.e. if lhs matches subjectTerm at pos**.
        
        
        Parameters
        ----------
        subjectTerm: Term
            The term which the distribution is applied to.
        pos: Position
            The position at which the distribution is applied.
        sub: Substitution
            A substitution which is applied to each term in the distribution.

        Returns
        -------
        list[tuple[float, Term]]
            The distribution of applying the rule in pairs of probability and resulting term.
        """
        
        # redex has been found
        res: list[tuple[float, Term]] = [] # list which stores all possible modifications of candidate under the distribution
        
        # evaluate candidate under the distribution
        for prob, term in self.get_distribution().get_values():
            # do not modify terms in distribution or candidate
            r, c = deepcopy(term), deepcopy(subjectTerm)
            # apply substitution to r (copy of term)
            r = r.apply_substitution(sub)
            # set subtree at position (modifies c)
            c.set_subtree(pos, r)
            # add to res
            res.append((prob, c))

        return res