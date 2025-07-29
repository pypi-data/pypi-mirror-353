from typing import Union

from prevision.core.term import Term, Const, Var

from re import sub


def clean(string: str) -> str:
    return sub(' +', ' ', string.replace('\n', ''))

def extract_str(string: str, start: int) -> tuple[int, int]:
    # grabs everything between the first occurrence of the toplevel (...) parenthesis pair in str
    while string[start] != '(':
        start += 1
    
    i = start
    diff = 0
    while i < len(string):
        c: str = string[i]
        if c == '(':
            diff += 1
        elif c == ')':
            diff -= 1
        if diff == 0:
            break
        i += 1
    end = i
    
    if diff != 0 or string[start] != '(' or string[end] != ')':
        raise ValueError(f"Invalid str found: \"{string}\"!")
    
    return start, end

def parse_fun(fun: str) -> tuple[str, int]:
    i = 0
    if fun[i] != '(':
        raise ValueError("Invalid function description.")
    i += 1
    if fun[i] == ' ':
        i += 1
    if fun[i:i+3] != "fun":
        raise ValueError("Invalid function description.")
    # probably valid fun description
    i += 4 # fun[i] now first symbol of {x} in (fun {name} {arity}) / ( fun {name} {arity} )
    
    # grab {name}
    start = i
    while fun[i] != ' ':
        i += 1
    end = i
    name = fun[start:end]
    
    # grab {arity}
    start = i + 1
    while fun[i] != ')':
        i += 1
    end = i
    arity = fun[start:end]

    return (name, int(arity))

def parse_term(raw: str, constants: list[str], functions: dict[str, int]) -> tuple[int, Term]:
    """
    Parses a string assuming the ARI format and yields a term. For this function to behave correctly the *start of the string* **must** be the *start of the term*.
    However, the string can go on after the term is complete.
    
    Parameters
    ----------
    raw: str
        The input string to be parsed.
    constants: list[str]
        A list of all the constants with regard to this PTRS.
    functions: dict[str, int]
        A dictionary of all functions and their corresponding arity values with regard to this PTRS.

    Returns
    -------
    (end, term): tuple[int, Term]
        end: The index **after** the last character of the term.
        term: The corresponding Term object.
    
    Raises
    -------
    ValueError
        If the supplied string does not correspond to a valid term.
    """

    # check if term is empty
    if not raw:
        ValueError("Term must not be empty (\"\")!")

    i = 0 # keep track of current symbol
    working_terms: list[tuple[str, list[Term]]] = [] # stack for (unfinished) terms
    while i < len(raw):
        # found new term
        if raw[i] == '(':

            # capture func symbol
            i = i + 1
            if raw[i] == ' ':
                i += 1
            start = i
            while i < len(raw) and raw[i] != ' ' and raw[i] != '(':
                i += 1
            
            # check if fun symbol is valid
            if raw[start:i] not in functions.keys():
                raise ValueError(f"Invalid function name: {repr(raw[start:i])}")

            # stack the found term, it becomes the new working term
            working_terms += [(raw[start:i], [])] # term[start:i] = f, [] = (...) in f(...)
        # term closed
        elif raw[i] == ')':
            cur = working_terms.pop()
            if len(cur[1]) != functions.get(cur[0], -1):
                raise ValueError(f"Too many/little arguments to function \"{cur[0]}\"")
            if working_terms:
                # cur term is finished, if there is a term of higher level, append it
                working_terms[-1][1].append(Term(cur[0], cur[1]))
            else:
                # stack is empty, closed toplevel term, create and return it
                return (i+1, Term(cur[0], cur[1]))
            i += 1
        elif raw[i] == ' ':
            i += 1 # inbetween terms, continue with next symbol
        else:
            # neither opening '(', nor closing ')' term, nor inbetween
            # -> must be beginning of var or const, skip until next space 
            # ' ' or closing bracket ')'
            
            # grab whole identifier
            start = i
            while i < len(raw) and raw[i] != ' ' and raw[i] != ')' and raw[i] != '(':
                i += 1
            
            # is it a Const or a Var?
            identifier: Union[Const, Var]
            if raw[start:i] in constants:
                identifier = Const(raw[start:i])
            else:
                identifier = Var(raw[start:i])

            # if working terms is empty, no compound term => the whole term is a Var / Const
            if not working_terms:
                return (i, identifier)
            else:
                working_terms[-1][1].append(identifier)

    raise ValueError("The supplied term is invalid.")