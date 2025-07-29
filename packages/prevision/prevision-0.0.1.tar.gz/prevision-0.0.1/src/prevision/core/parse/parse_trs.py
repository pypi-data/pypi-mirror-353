from prevision.core.prule import PRule
from prevision.core.ptrs import Ptrs
from prevision.core.parse.utility import clean, extract_str, parse_fun, parse_term
# from os import getcwd

COST: int = 0 # TODO: find out what cost should be in TRS

class ParseTRS:
    def __init__(self) -> None:
        pass

    def parse_trs(self, inStr) -> tuple[Ptrs, list[tuple[str, int]]]:
        # remove newlines and multiple spaces        
        f_str = clean(inStr)
        
        i = f_str.find("format TRS")
        if i == -1:
            raise ValueError("Wrong Format! (\"(format TRS)\" missing!)")
        # "format TRS" has been found, probably (somewhat) correct format
        trs_str = f_str[i:]
        
        i = trs_str.find('(')
        if i == -1:
            return Ptrs([]), [] # TODO: Value error? Also fix this spaghetti code?
        # trs not empty
        # search for fun(cs)
        functions: list[tuple[str, int]] = [] # store functions
        while i != -1:
            # invariant: trs_str[i] == '('
            #'('   ')'
            if not "fun" in trs_str[i:i+5]:
                break
            start, end = extract_str(trs_str, i)
            functions += [parse_fun(trs_str[start:end+1])]
            i = trs_str.find('(', end)

        # filter constants out of funcs
        constants = [cons[0] for cons in filter(lambda x: x[1] == 0, functions)] # get list of constants
        
        # search for rules
        rules: list[PRule] = []
        while i != -1:
            start, end = extract_str(trs_str, i)
            rules += [self.parse_rule(trs_str[start:end+1], constants, dict(functions))]
            i = trs_str.find('(', end)

        return Ptrs(rules), functions

    def parse_rule(self, rule: str, constants: list[str], functions: dict[str, int]) -> PRule:
        # need to find rule in "(rule {x} {y})" or e.g. "( rule {x} {y})"
        i = rule.find("rule")
        if i == -1:
            raise ValueError("Invalid rule.")

        i += 5
        if rule[i] == '(':
            # first term compound, grab it
            start, end = extract_str(rule, i)
            _, lhs = parse_term(rule[start:end+1], constants, functions)
            
            # start of second term
            start = i = end + 2
            if rule[i] == '(':
                # compound
                start, end = extract_str(rule, i)
                _, rhs = parse_term(rule[start:end+1], constants, functions)
            else:
                # not compound
                while rule[i] != ')' and rule[i] != ' ':
                    i += 1
                end = i
                _, rhs = parse_term(rule[start:end], constants, functions)
            return PRule(lhs, [(1, rhs)], COST)
        else:
            # first term not compound
            start = i
            while rule[i] != ' ':
                i += 1
            end = i
            _, lhs = parse_term(rule[start:end], constants, functions)
            
            # start of second term
            start = i = end+1
            if rule[i] == '(':
                # compound
                start, end = extract_str(rule, i)
                _, rhs = parse_term(rule[start:end+1], constants, functions)
            else:
                # not compound
                while rule[i] != ')' and rule[i] != ' ':
                    i += 1
                end = i
                _, rhs = parse_term(rule[start:end], constants, functions)
            return PRule(lhs, [(1, rhs)], COST)


if __name__ == "__main__":
    pass