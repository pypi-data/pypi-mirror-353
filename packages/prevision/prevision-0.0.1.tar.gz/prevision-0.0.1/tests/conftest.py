from sys import path
# path.append("C:\\Users\\David\\nextCloud\\Programmieren\\RWTH Projects\\prevision")
import pytest
from prevision.core.rose_tree import RoseTree
from prevision.core.term import Term, Var, Const, Substitution
from prevision.core.evaluation_strategy import *
# from prevision.Rule import Rule
# from prevision.TRS import TRS
from prevision.core.prule import PRule
from prevision.core.ptrs import Ptrs
from prevision.core.parse.parse_trs import ParseTRS
from prevision.core.parse.parse_ptrs import ParsePTRS
from prevision.core.rose_tree_converter import RTConv
from prevision.core.parse.utility import *

# Terms and Substitutions defined in this file:

# Overview of all terms in simple notation
# Term t1: F(G(0),G(x))
# Term t2: A(M(S(S(0)),S(0)),S(S(0)))
# Term t3: A(M(S(S(0)),S(0)),S(0))
# Term t4: A(M(S(S(0)),S(0)),0)
# Term t5: M(S(S(0)),S(0))
# Term t6: A(0,S(S(0)))
# Term t7: A(0,S(0))
# Term t8: A(0,0)

# Term t9: F(A(x),A(y))
# Term t10: F(c,G(c),G(G(c)))

# Term t11: A(0,S(A(S(C),S(0))))
# Term t12: F(F(0,0), F(0,F(0,0)))


# lhs of rules
# Term l1: F(G(x),y)
# Term l2: A(x,0)
# Term l3: A(x,S(y))
# Term l4: M(x,0)
# Term l5: M(x,S(y))
# Term l6: F(x,x)
# Term l7: F(x,y,G(x))

# Some substitutions 
# Substitution s1: {"x": 0,                 "y": G(x), "z": S(0)}
# Substitution s2: {"x": M(S(S(0)),S(0)),   "y": S(0)           }

@pytest.fixture
def parseTRS() -> ParseTRS:
    return ParseTRS()

@pytest.fixture
def parsePTRS() -> ParsePTRS:
    return ParsePTRS()

@pytest.fixture
def rose_trees() -> dict[str, RoseTree]:
    t1: RoseTree[int] = RoseTree(4, [RoseTree(2, [RoseTree(1, []), RoseTree(3, [])]), RoseTree(6, [RoseTree(5, []), RoseTree(7, [])])])

    return {"t1": t1}

@pytest.fixture
def converter() -> dict[str, RTConv]:
    return {"c1" : RTConv()}

@pytest.fixture
def terms(parsePTRS) -> dict[str, Term]:
    # the following examples have a matching
    # first a simple example from Terese (p. 35, Def. reduction rule)
    # l1: F(G(x),y), left hand side of a rule
    # t1: F(G(0),G(x))

    l1: Term = Term("F", 
                        [
                            Term("G",[Var("x")]),
                            Var("y")
                        ]
                    )
    r1: Term = Term("F", [Var("x"), Var("x")])
    t1: Term = Term("F",
                        [
                            Term("G", [Const("0")]),
                            Term("G", [Var("x")])
                        ]
                    )
    ctr1: Term = Term("F", [Const("0"), Const("0")]) # ctr for contractum
    # more complex example from Terese (p. 38f), the rules l2-5 define a computation 
    # procedure to determine the result of terms build with natural numbers, addition and multiplication
    # rules:

    # l2: A(x,0)
    l2: Term = Term("A", 
                        [
                            Var("x"),
                            Const("0")
                        ]
                    )
    # l3: A(x,S(y))
    l3: Term = Term("A",
                        [
                            Var("x"),
                            Term("S", [Var("y")])
                        ]
                    )
    # l4: M(x,0)
    l4: Term = Term("M", 
                        [
                            Var("x"),
                            Const("0")
                        ]
                    )
    # l5: M(x, S(y))
    l5: Term = Term("M", 
                        [
                            Var("x"), 
                            Term("S", [Var("y")])
                        ]
                    )
    # r2: x
    r2: Term = Var("x")
    # r3: S(A(x,y))
    r3: Term = Term("S", [Term("A", [Var("x"), Var("y")])])
    # r4: 0
    r4: Term = Const("0")
    # r5: A(M(x,y), x)
    r5: Term = Term("A", [Term("M", [Var("x"), Var("y")]), Var("x")])
    # the starting term is t2: A(M(S(S(0)),S(0)),S(S(0))); t3-8 are NOT the result of the computation,
    # but rather the next chosen redex:

    # t2: A(M(S(S(0)),S(0)),S(S(0)))
    t2: Term = Term("A",
                        [
                            Term("M",
                                    [
                                        Term("S", [Term("S", [Const("0")])]),
                                        Term("S", [Const("0")])
                                    ]
                                ),
                            
                            Term("S", [Term("S", [Const("0")])])
                        ]
                    )
    # t3: A(M(S(S(0)),S(0)),S(0))
    t3: Term = Term("A",
                        [
                            Term("M",
                                    [
                                        Term("S", [Term("S", [Const("0")])]),
                                        Term("S", [Const("0")])
                                    ]
                                ),
                            
                            Term("S", [Const("0")])
                        ]
                    )
    # t4: A(M(S(S(0)),S(0)),0)
    t4: Term = Term("A",
                        [
                            Term("M",
                                    [
                                        Term("S", [Term("S", [Const("0")])]),
                                        Term("S", [Const("0")])
                                    ]
                                ),
                            
                            Const("0")
                        ]
                    )
    # t5: M(S(S(0)),S(0))
    t5: Term = Term("M", 
                        [
                            Term("S", [Term("S", [Const("0")])]), 
                            Term("S", [Const("0")])
                        ]
                    )
    # t6: A(0,S(S(0)))
    t6: Term = Term("A", 
                        [
                            Const("0"),
                            Term("S", [Term("S", [Const("0")])])
                        ]
                    )
    # t7: A(0,S(0))
    t7: Term = Term("A", 
                        [
                            Const("0"),
                            Term("S", [Const("0")])
                        ]
                    )
    # t8: A(0,0)
    t8: Term = Term("A", 
                        [
                            Const("0"),
                            Const("0")
                        ]
                    )

    # for contractums use t2 as initial term as mentioned, but new terms for the following computations, starting with ctr2:
    # ctr2: S(A(M(S(S(0)),S(0)),S(0)))
    ctr2: Term = Term("S", [Term("A",[Term("M",[Term("S", [Term("S", [Const("0")])]),Term("S", [Const("0")])]),Term("S", [Const("0")])])])
    # ctr3: S(S(A(M(S(S(0)),S(0)),0)))
    ctr3: Term = Term("S", [Term("S", [Term("A",[Term("M",[Term("S", [Term("S", [Const("0")])]),Term("S", [Const("0")])]),Const("0")])])])
    
    # these can be found below (used parser to create these, its faster)
    # ------------------------------------
    # ctr4: S(S(M(S(S(0)),S(0))))
    # ctr5: S(S(A(M(S(S(0)),0), S(S(0)))))
    # ctr6: S(S(S(A(0,S(0)))))
    # ctr7: S(S(S(S(A(0,0)))))
    # ctr8: S(S(S(S(0))))
    # ------------------------------------

    ctr8: Term = Term("S", [Term("S", [Term("S", [Term("S", [Const("0")])])])])
    # examples where there should be no matching, not taken from a book
    # l6: F(x,x)
    l6: Term = Term("F", [Var("x"), Var("x")])
    # t9: F(A(x),A(y))
    t9: Term = Term("F", [Term("A", [Var("x")]), Term("A", [Var("y")])])

    # l7: F(x,y,G(x))
    l7: Term = Term("F", [Var("x"), Var("y"), Term("G", [Var("x")])])
    # t10: Z(c,G(c),G(G(c)))
    t10: Term = Term("Z", [Const("c"), Term("G", [Const("c")]), Term("G", [Term("G", [Const("c")])])])

    # this term should have two matchings with term l3
    # t11: A(0,S(A(S(C),S(0))))
    t11: Term = Term("A", 
                        [
                            Const("0"), 
                            Term("S", [Term("A", 
                                                [
                                                    Term("S", [Const("C")]), 
                                                    Term("S", [Const("0")])
                                                ]
                                            )])
                        ]
                    )
    # t12: F(F(0,F(0,0)), F(0,F(0,0)))
    t12: Term = Term("F", 
                        [
                            Term("F", 
                                    [
                                        Const("0"), 
                                        Term("F", [Const("0"), Const("0")])
                                    ]
                                ), 
                            Term("F", 
                                    [
                                        Const("0"), 
                                        Term("F", [Const("0"), Const("0")])
                                    ]
                                )
                        ]
                    )


    # create terms with parser
    # ctr4 in parse format: (S (S (M (S (S 0)) (S 0))))
    _, ctr4 = parse_term("(S (S (M (S (S 0)) (S 0))))", ['0'], {'M': 2, 'A': 2, 'S': 1, '0': 0})
    # ctr5: S(S(A(M(S(S(0)),0), S(S(0)))))
    _, ctr5 = parse_term("(S (S (A (M (S (S 0)) 0) (S (S 0)))))", ['0'], {'M': 2, 'A': 2, 'S': 1, '0': 0})
    # ctr6: S(S(S(A(0,S(0)))))
    _, ctr6 = parse_term("(S (S (S (A 0 (S 0))))))", ['0'], {'M': 2, 'A': 2, 'S': 1, '0': 0})
    # ctr7: S(S(S(S(A(0,0)))))
    _, ctr7 = parse_term("(S (S (S (S (A 0 0)))))", ['0'], {'M': 2, 'A': 2, 'S': 1, '0': 0})

    # create term for ARI11
    # compute 1+2+3+5+7+11+13 (forty two, ft / term_ft)
    ft = ("(+ (s 0) (+ (s (s 0)) (+ (s (s (s 0))) " + 
                "(+ (s (s (s (s (s 0))))) (+ (s (s (s (s (s (s (s 0))))))) (+ (s (s (s (s (s (s (s (s (s (s (s 0))))))))))) " +
                "(s (s (s (s (s (s (s (s (s (s (s (s (s 0)))))))))))))))))))")
    
    ftc = ("(s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s " +
                           "(s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s (s " +
                           "(s (s (s (s 0))))))))))))))))))))))))))))))))))))))))))")
    
    _, t_ft = parse_term(ft, ['0'], {'+': 2, 's': 1, '0': 0})
    _, t_ftc = parse_term(ftc, ['0'], {'+': 2, 's': 1, '0': 0})

    # The terms belonging to PTRS 1
    # (S x) 
    prule1_lhs_sx = Term('S', [Var('x')])
    # x
    prule1_rhs1_x = Var('x')
    # (S (S x))
    prule1_rhs2_ssx = Term('S', [Term('S', [Var('x')])])
    
    # Starting term for PTRS 1
    # (S 0)
    ptrs1_start_s0 = Term('S', [Const('0')])

    # The terms belonging to the PTRS 2
    # g
    prule2_lhs = Const('g')
    # b
    prule2_rhs = Const('b')
    # g
    prule3_lhs = Const('g')
    # (f g), stop
    prule3_rhs1, prule3_rhs2 = Term('f', [Const('g')]), Const('stop')
    # (f b)
    prule4_lhs = Term('f', [Const('b')])
    # g
    prule4_rhs = Const('g')

    #Starting term for PTRS 2
    # (f g)
    ptrs2_start_fg = Term('f', [Const('g')])



    # Term as result of ptrs1
    normalform = Const('0')


    # term to test evaluationstrategy
    _, eTSubjectTerm = parse_term("(A (A 0 (A 0 (S 0))) (A 0 (A 0 (S 0))))", ['0'], {'A': 2, 'S': 1, '0': 0})
    _, eTPatternTerm = parse_term("(A 0 X)", ['0'], {'A': 2, 'S': 1, '0': 0})

    # term to test probabilistic_deterministic_trees function
    _, startTermPDTs1 = parse_term("(len (cons (len nil) nil))", ['0'], {'cons': 2, 'len': 1})

    _, startTermPDTs2 = parse_term("a", ['a'], {'a': 0})

    return {'t1':t1,'t2':t2,'t3':t3,'t4':t4,'t5':t5,'t6':t6,'t7':t7,'t8':t8,
            't9':t9,'t10':t10,'t11':t11,'t12':t12,'l1':l1,'l2':l2,'l3':l3,'l4':l4,
            'l5':l5,'l6':l6,'l7':l7, "r1": r1, "r2": r2, "r3": r3, "r4": r4, "r5": r5, 
            "ctr1": ctr1, "ctr2": ctr2, "ctr3": ctr3, "ctr4": ctr4, "ctr5": ctr5, 
            "ctr6": ctr6, "ctr7": ctr7, "ctr8": ctr8, "compound42": t_ft, "42": t_ftc, 
            "prule1_lhs_sx": prule1_lhs_sx, "prule1_rhs1_x": prule1_rhs1_x, 
            "prule1_rhs2_ssx": prule1_rhs2_ssx, "ptrs1_start_s0": ptrs1_start_s0,
            "prule2_lhs": prule2_lhs, "prule2_rhs": prule2_rhs, "prule3_lhs": prule3_lhs,
            "prule3_rhs1": prule3_rhs1, "prule3_rhs2": prule3_rhs2, "prule4_lhs": prule4_lhs,
            "prule4_rhs": prule4_rhs, "nf": normalform, "ptrs2_start_fg": ptrs2_start_fg,
            "eTSubjectTerm": eTSubjectTerm, "eTPatternTerm": eTPatternTerm, "startTermPDTs": startTermPDTs1,
            "startTermPDTs2": startTermPDTs2}

@pytest.fixture
def substitutions() -> dict[str, Substitution]:
    # Some substitutions 
    # Substitution s1: {"x": 0,                 "y": G(x), "z": S(0)}
    s1: Substitution = Substitution({"x": Const("0"), "y": Term("G", [Var("x")]), "z": Term("S", [Const("0")])})
    # Substitution s2: {"x": M(S(S(0)),S(0)),   "y": S(0)           }
    s2: Substitution = Substitution({"x": Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])]), 
                                     "y": Term("S", [Const("0")])})

    return {"s1": s1, "s2": s2}

@pytest.fixture
def prules(terms):
    # prules for ptrs1
    lhs1 = terms["prule1_lhs_sx"]
    dist1 = [(1, terms["prule1_rhs1_x"]), (1, terms["prule1_rhs2_ssx"])]

    # prules for ptrs2
    lhs2, dist2 = terms["prule2_lhs"], [(1, terms["prule2_rhs"])]
    lhs3, dist3 = terms["prule3_lhs"], [(5, terms["prule3_rhs1"]), (3, terms["prule3_rhs2"])]
    lhs4, dist4 = terms["prule4_lhs"], [(1, terms["prule4_rhs"])]


    # prules for parse_trs
    # simple example of p. 35 again
    lhs5, dist5 = terms["l1"], [(1, terms["l6"])]
    
    # more complex example of p. 38f again
    lhs6, dist6 = terms["l2"], [(1, terms["r2"])]
    lhs7, dist7 = terms["l3"], [(1, terms["r3"])]
    lhs8, dist8 = terms["l4"], [(1, terms["r4"])]
    lhs9, dist9 = terms["l5"], [(1, terms["r5"])]
    
    return {"prule1": PRule(lhs1, dist1, 0), "prule2": PRule(lhs2, dist2, 0),
            "prule3": PRule(lhs3, dist3, 0), "prule4": PRule(lhs4, dist4, 0),
            "prule5": PRule(lhs5, dist5, 0), "prule6": PRule(lhs6, dist6, 0),
            "prule7": PRule(lhs7, dist7, 0), "prule8": PRule(lhs8, dist8, 0),
            "prule9": PRule(lhs9, dist9, 0), "prule10": PRule(Const("a"), [(1, Term("h", [Const("a")]))], 0)}

@pytest.fixture
def evaluationStratgies() -> dict[str, EvaluationStrategy]:
    return {"F": Full(), "LO": LeftmostOutermost(), "LI": LeftmostInnermost(),
            "RO": RightmostOutermost(), "RI": RightmostInnermost(),
            "I": Innermost(), "O": Outermost()}

@pytest.fixture
def ptrss(prules):
    ptrs1 = Ptrs([prules["prule1"]])

    ptrs2 = Ptrs([prules["prule2"], prules["prule3"], prules["prule4"]])

    add_mult_trs = Ptrs(list(prules.values())[5:10])
    
    with open("prevision/tests/test_input_ari/test_inputARI11.txt") as file:
        in_str = "".join(file.readlines())
        ptrs11, _ = ParseTRS().parse_trs(in_str)

    with open("prevision/tests/test_input_ari/lists0.ari") as file:
        in_str = "".join(file.readlines())
        lists0, _ = ParsePTRS().parse_ptrs(in_str)
    
    with open("prevision/tests/test_input_ari/testPD.txt") as file:
        in_str = "".join(file.readlines())
        testPD, _ = ParsePTRS().parse_ptrs(in_str)
        
    
    return {"ptrs1": ptrs1, "ptrs2": ptrs2, "ptrs3": add_mult_trs, "pTRS11": ptrs11,
            "lists0": lists0, "testPD": testPD}