def test_parse_distribution(parsePTRS, terms):
    # ((x :prob 1) ((S (S x)) :prob 1))
    dist1 = [(1, terms["prule1_rhs1_x"]), (1, terms["prule1_rhs2_ssx"])]
    dist2 = [(5, terms["prule3_rhs1"]), (3, terms["prule3_rhs2"])]

    assert parsePTRS.parse_dist("((x :prob 1) ((S (S x)) :prob 1))", ['0'], {'S': 1, '0': 0})[1] == dist1
    assert parsePTRS.parse_dist("(((f g) :prob 5 ) (stop :prob 3 ))", ['g', 'b', 'stop'], {'g': 0, 'b': 0, 'f': 1, 'stop': 0})[1] == dist2


def test_parse_prule(parsePTRS, prules):
    assert parsePTRS.parse_prule("(prule (S x) ((x :prob 1) ((S (S x)) :prob 1)))", ['0'], {'S': 1, '0': 0}) == prules["prule1"]
    assert parsePTRS.parse_prule("(prule g ((b :prob 1 )))", ['g', 'b', 'stop'], {'g': 0, 'b': 0, 'f': 1, 'stop': 0}) == prules["prule2"]
    assert parsePTRS.parse_prule("(prule g (((f g) :prob 5 ) (stop :prob 3 )))", ['g', 'b', 'stop'], {'g': 0, 'b': 0, 'f': 1, 'stop': 0}) == prules["prule3"]
    assert parsePTRS.parse_prule("(prule (f b) ((g :prob 1 )))", ['g', 'b', 'stop'], {'g': 0, 'b': 0, 'f': 1, 'stop': 0}) == prules["prule4"]
    

def test_parse_ptrs(parsePTRS, ptrss):
    
    with open("prevision/tests/test_input_ari/test_input5.txt") as file:
        ptrs_in_str_1 = "".join(file.readlines())
        ptrs, _ = parsePTRS.parse_ptrs(ptrs_in_str_1)
        assert ptrs == ptrss["ptrs1"] 

    with open("prevision/tests/test_input_ari/test_input3.txt") as file:
        ptrs_in_str_2 = "".join(file.readlines())
        ptrs, _ = parsePTRS.parse_ptrs(ptrs_in_str_2)
        assert ptrs == ptrss["ptrs2"]