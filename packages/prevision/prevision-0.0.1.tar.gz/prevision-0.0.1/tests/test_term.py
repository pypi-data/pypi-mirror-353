# Need to make package prevision available as package so that it can be used
from sys import path
# path.append("C:\\Users\\David\\nextCloud\\Programmieren\\RWTH Projects\\prevision")
from prevision.core.term import Term, Var, Const, Position
from copy import deepcopy


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


def test_v(terms):

    assert terms["t1"].v() == [([1,0], Var("x"))]
    assert terms["t2"].v() == terms["t3"].v() == terms["t4"].v() == terms["t5"].v() == terms["t6"].v() == terms["t7"].v() == terms["t8"].v() == []

    assert terms["t9"].v() == [([0,0], Var("x")), ([1,0], Var("y"))]
    assert terms["t10"].v() == terms["t11"].v() == []

    assert terms["l1"].v() == [([1], Var("y")), ([0,0], Var("x"))]
    assert terms["l2"].v() == [([0], Var("x"))]
    assert terms["l6"].v() == [([0], Var("x")), ([1], Var("x"))]
    assert terms["l7"].v() == [([0], Var("x")), ([1], Var("y")), ([2,0], Var("x"))]


def test_match(terms):
    # test first example
    assert terms["l1"].match(terms["t1"]) == (True, {"x": Const("0"), "y": Term("G", [Var("x")])})
    # test second more complex example
    assert terms["l3"].match(terms["t2"]) == (True, {"x": Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])]), "y": Term("S", [Const("0")])})
    assert terms["l3"].match(terms["t3"]) == (True, {"x": Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])]), "y": Const("0")})
    assert terms["l2"].match(terms["t4"]) == (True, {"x": Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])])})
    assert terms["l5"].match(terms["t5"]) == (True, {"x": Term("S", [Term("S", [Const("0")])]), "y": Const("0")})
    assert terms["l3"].match(terms["t6"]) == (True, {"x": Const("0"), "y": Term("S", [Const("0")])})
    assert terms["l3"].match(terms["t7"]) == (True, {"x": Const("0"), "y": Const("0")})
    assert terms["l2"].match(terms["t8"]) == (True, {"x": Const("0")})
    # test not matching terms
    assert terms["l6"].match(terms["t9"]) == (False, {})
    assert terms["l7"].match(terms["t10"]) == (False, {})

# def test_match_all(terms):

#     assert terms["l3"].match_all(terms["t11"]) == [([], {"y": Term("A", [Term("S", [Const("C")]), Term("S", [Const("0")])]), "x": Const("0")}),
#                                  ([1,0], {"x": Term("S", [Const("C")]), "y": Const("0")})]

#     assert terms["l6"].match_all(terms["t12"]) == [([], {"x": Term("F", [Const("0"), Term("F", [Const("0"), Const("0")])])}),
#                                  ([0,1], {"x": Const("0")}),
#                                  ([1,1], {"x": Const("0")})]

def test_apply_substitution(terms, substitutions):
    l1_copy = deepcopy(terms["l1"])
    l3_copy = deepcopy(terms["l3"])
    l7_copy = deepcopy(terms["l7"])
    id_l1, id_l3, id_l7 = id(terms["l1"]), id(terms["l3"]), id(terms["l7"])
    id_l1_copy, id_l3_copy, id_l7_copy = id(l1_copy), id(l3_copy), id(l7_copy)


    # safe=False, check right result
    assert l1_copy.apply_substitution(substitutions["s1"]) == terms["t1"]
    assert l3_copy.apply_substitution(substitutions["s2"]) == terms["t2"]
    assert l7_copy.apply_substitution(substitutions["s2"]) == Term("F", [Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])]),
                                                              Term("S", [Const("0")]),
                                                              Term("G", [Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])])])])

    # safe=False modifies the calling object
    assert id_l1_copy == id(l1_copy)
    assert id_l3_copy == id(l3_copy)
    assert id_l7_copy == id(l7_copy)

    # Substitution objects are not put into calling term when applying substitution
    assert substitutions["s2"].get("x").get_subtree(Position([1,0])) == l7_copy.get_subtree(Position([0,1,0]))
    assert substitutions["s2"].get("x").get_subtree(Position([1,0])) is not l7_copy.get_subtree(Position([0,1,0]))



    # **basically legacy code from a previous version**
    # # safe=True
    # new_l1 = terms["l1"].apply_substitution(substitutions["s1"], safe=True)
    # new_l3 = terms["l3"].apply_substitution(substitutions["s2"], safe=True)
    # new_l7 = terms["l7"].apply_substitution(substitutions["s2"], safe=True)

    # # check right result
    # assert new_l1 == terms["t1"]
    # assert new_l3 == terms["t2"]
    # assert new_l7 == Term("F", [Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])]),
    #                                                           Term("S", [Const("0")]),
    #                                                           Term("G", [Term("M", [Term("S", [Term("S", [Const("0")])]), Term("S", [Const("0")])])])])

    # # safe=True does not modify calling object
    # assert new_l1 is not terms["l1"] and id(terms["l1"]) == id_l1
    # assert new_l3 is not terms["l3"] and id(terms["l3"]) == id_l3
    # assert new_l7 is not terms["l7"] and id(terms["l7"]) == id_l7

    # # Substitution objects are not put into calling term when applying substitution
    # assert substitutions["s2"].get("x").get_subtree([1,0]) == new_l7.get_subtree(Position([0,1,0]))
    # assert substitutions["s2"].get("x").get_subtree([1,0]) is not new_l7.get_subtree(Position([0,1,0]))


if __name__ == "__main__":
    # for i in range(1,12):
    #     print("Term " + f"l{i}: " + str(locals()[f"l{i}"]))
    # for j in range(1,8):
    #     print("Term " + f"t{j}: " + str(locals()[f"t{j}"]))
    pass