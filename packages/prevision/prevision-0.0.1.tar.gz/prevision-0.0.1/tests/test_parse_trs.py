from pytest import raises

def test_parse_rule(parseTRS, prules):
    
    assert parseTRS.parse_rule("(rule (F (G x) y) (F x x))", [], {'F': 2, 'G': 1}) == prules["prule5"]
    assert parseTRS.parse_rule("(rule (A x 0) x)", ['0'], {'A': 2, 'M': 2, 'S': 1, '0': 0}) == prules["prule6"]
    assert parseTRS.parse_rule("(rule (A x (S y)) (S (A x y)))", ['0'], {'A': 2, 'M': 2, 'S': 1, '0': 0}) == prules["prule7"]
    assert parseTRS.parse_rule("(rule (M x 0) 0)", ['0'], {'A': 2, 'M': 2, 'S': 1, '0': 0}) == prules["prule8"]
    assert parseTRS.parse_rule("(rule (M x (S y)) (A (M x y) x))", ['0'], {'A': 2, 'M': 2, 'S': 1, '0': 0}) == prules["prule9"]
    assert parseTRS.parse_rule("(rule a (h a))", ['a'], {'a': 0, 'h': 1}) == prules["prule10"]

    with raises(Exception) as e_info:
        parseTRS.parse_rule("(rule (M x (S y) 0)", ['0'])
    with raises(Exception) as e_info:
        parseTRS.parse_rule("(rule x (F x x))", ['0'])
    # print(e_info.value)
    with raises(Exception) as e_info:
        parseTRS.parse_rule("(rule (F (G x) y) (F z x))", ['0'])
    # print(e_info.value)


def test_parse_trs(parseTRS, ptrss):
    
    with open("prevision/tests/test_input_ari/test_input1.txt") as file:
        in_str = "".join(file.readlines())
        ptrs, _ = parseTRS.parse_trs(in_str)
        assert ptrs == ptrss["ptrs3"]