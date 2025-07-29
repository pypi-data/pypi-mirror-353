from prevision.core.term import Term
from prevision.core.prule import PRule
from prevision.core.ptrs import Ptrs
from .utility import clean, extract_str, parse_fun, parse_term

class ParsePTRS:
    def __init__(self) -> None:
        pass

    def parse_dist(self, raw: str, constants: list[str], functions: dict[str, int]) -> tuple[int, list[tuple[int, Term]]]:
        weightedTerms = []
        i = 1 # raw[i] now beginning of first probabilistic rule
        brackets = 1
        while i < len(raw) and brackets > 0:
            if raw[i] == '(':
                i += 1 # raw[i] now beginning of first term
                brackets += 1
                weight: int # although in the format it is "prob", we are given weights, not probabilities
                t: Term

                end, t = parse_term(raw[i:], constants, functions)
                i += end
                
                start = raw.find(":prob", i) # beginning of ":prob num"
                
                if start == -1:
                    # default case
                    weight = 1
                else:
                    # prob specified, capture number
                    start = end = start + 6 # beginning of num
                    while raw[end] != ' ' and raw[end] != ')':
                        end += 1
                    if not raw[start:end].isnumeric():
                        raise ValueError(f"Not a number: \"{raw[start:end]}\"")
                
                    weight = int(raw[start:end])
                    i = end

                weightedTerms.append((weight, t))
            elif raw[i] == ')':
                i += 1
                brackets -= 1
            else:
                i += 1

        return (i, weightedTerms)


    def parse_prule(self, raw: str, constants: list[str], functions: dict[str, int]) -> PRule:
        lhs: Term
        rhs: list[tuple[int, Term]]
        cost: float
        
        
        i = raw.find("prule")
        if i == -1:
            raise ValueError("Invalid prule!")
        i += 6
        
        # parse lhs
        end, lhs = parse_term(raw[i:], constants, functions)
        # find beginning of distribution
        i += end
        i += raw[i:].find('(')
        
        # parsed lhs, now it should hold that raw[i] = '(', the start of the distribution
        # => parse distribution
        end, rhs = self.parse_dist(raw[i:], constants, functions)
        i += end

        start = raw.find(":cost", i) # beginning of ":cost num"

        if start == -1:
            # default case
            cost = 1
        else:
            # cost specified, capture number
            start = end = start + 6 # beginning of num
            while raw[end] != ' ':
                end += 1

            if not raw[start:end].isnumeric():
                raise ValueError(f"Not a number: \"{raw[start:end]}\"")
        
            cost = int(raw[start:end])
            i = end

        return PRule(lhs, rhs, cost)

    def parse_ptrs(self, inStr) -> tuple[Ptrs, list[tuple[str, int]]]: 
        cStr = clean(inStr)
        i = cStr.find("format PTRS")
        if i == -1:
           raise ValueError("Wrong Format! (\"(format PTRS)\" missing!)")
        
        i = cStr.find('(', i) # skip first bracket'('
        if i == -1:
            return Ptrs([]), [] # TODO: fix this? Value error?
        # ptrs not empty

        functions: list[tuple[str, int]] = [] # store functions
        while i != -1:
            # invariant: string[i] == '('
            #'('   ')'
            if not "fun" in cStr[i:i+5]:
                break
            start, end = extract_str(cStr, i)
            
            functions += [parse_fun(cStr[start:end+1])]
            i = cStr.find('(', end)

        constants = [cons[0] for cons in functions if cons[1] == 0] # get list of constants
        # print(i)
        # print(ptrs_ari[i:])
        # now rules
        prules: list[PRule] = []
        if i == -1:
            return Ptrs([]), []
        while i != -1:
            start, end = extract_str(cStr, i)
            # print(ptrs_ari[start:end+1])
            prules += [self.parse_prule(cStr[start:end+1], constants, dict(functions))]
            i = cStr.find('(', end)
        

        return Ptrs(prules), functions


if __name__ == "__main__":
    pass