from pytest import raises
from prevision.core.parse.utility import *

def test_extract_str_ptrs():
    str1 = "(((((((())))))))"
    start, end = extract_str(str1, 0)
    assert str1[start:end+1] == str1
    
    str2 = "(a(f((c((D(\"\"())))))))"
    start, end = extract_str(str2, 0)
    assert str2[start:end+1] == str2
    
    str3 = "(1(( ((23((:(((())) ue) )\n))df  ))))"
    start, end = extract_str(str3, 0)
    assert str3[start:end+1] == str3
    
    str4 = "893483984289LKS:DAF§(((32478907)))203984724"
    start, end = extract_str(str4, 0)
    assert str4[start:end+1] == "(((32478907)))"
    
    with raises(Exception) as e_info:
        str5 = "((())"
        extract_str(str5, 0)
    # print(e_info)

    with raises(Exception) as e_info:
        str6 = ")))((())"
        extract_str(str6, 0)
    # print(e_info)


def test_parse_term_ptrs(terms):
    # 0 and c have been consistently chosen as constants for the terms in terms
    constants = ["0", "c"]
    functions = {'0': 0, 'F': 2, 'G': 1, 'A': 2, 'M': 2, 'S': 1, 'c': 0, 'Z': 3}
    
    # terms to test ptrs
    _, prule1_lhs_sx = parse_term("(S x)", ['0'], {'S': 1, '0': 0})
    _, prule1_rhs1_x = parse_term("x", ['0'], {'S': 1, '0': 0})
    _, prule1_rhs2_ssx = parse_term("(S (S x))", ['0'], {'S': 1, '0': 0})
    _, ptrs1_start_s0 = parse_term("(S 0)", ['0'], {'S': 1, '0': 0})

    assert prule1_lhs_sx == terms["prule1_lhs_sx"]
    assert id(prule1_lhs_sx) != id(terms["prule1_lhs_sx"])
    assert prule1_rhs1_x == terms["prule1_rhs1_x"]
    assert prule1_rhs2_ssx == terms["prule1_rhs2_ssx"]
    assert ptrs1_start_s0 == terms["ptrs1_start_s0"]

    # l1: F(G(x),y)
    l1_str = "(F (G x) y)"
    assert parse_term(l1_str, constants, functions) == (len(l1_str), terms["l1"])

    # t1: F(G(0),G(x))
    t1_str = "(F (G 0) (G x))"
    assert parse_term(t1_str, constants, functions) == (len(t1_str), terms["t1"])

    # r4: 0
    r4_str = "0"
    assert parse_term(r4_str, constants, functions) == (len(r4_str), terms["r4"])

    # t2: A(M(S(S(0)),S(0)),S(S(0)))
    t2_str = "(A (M (S (S 0)) (S 0)) (S (S 0)))"
    assert parse_term(t2_str, constants, functions) == (len(t2_str), terms["t2"])

    # t10: Z(c,G(c),G(G(c)))
    t10_str = "(Z c (G c) (G (G c)))"
    assert parse_term(t10_str, constants, functions) == (len(t10_str), terms["t10"])

    # t12: F(F(0,F(0,0)), F(0,F(0,0)))
    t12_str = "(F (F 0 (F 0 0)) (F 0 (F 0 0)))"
    assert parse_term(t12_str, constants, functions) == (len(t12_str), terms["t12"])

    # test some terms that are a bit deformed
    # t12: F(F(0,F(0,0)), F(0,F(0,0)))
    # (no space between F and sub1: (F(sub1) (sub2))
    deformed1 = "(F(F 0 (F 0 0)) (F 0 (F 0 0)))     "
    assert parse_term(deformed1, constants, functions) == (len(deformed1) - 5, terms["t12"])

    deformed2 = "(F(F 0 (F 0 0)) (F 0(F 0 0 )) )  "
    assert parse_term(deformed2, constants, functions) == (len(deformed2) - 2, terms["t12"])

    # test some not working terms
    nw1 = "(asdf)"
    with raises(Exception) as e_info:
        parse_term(nw1, constants, functions)

    nw2 = "((((())"
    with raises(Exception) as e_info:
        parse_term(nw2, constants, functions)

    nw3 = "(F (G 0 (G 0)) (G x))"
    with raises(Exception) as e_info:
        parse_term(nw3, constants, functions)
    
    nw4 = "(A (M (S (S 0)) (S 0) (A 0 0)) (S (S 0)))"
    with raises(Exception) as e_info:
        parse_term(nw4, constants, functions)