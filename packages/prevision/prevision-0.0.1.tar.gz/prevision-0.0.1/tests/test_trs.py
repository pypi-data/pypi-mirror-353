from copy import deepcopy

def test_run_trs(ptrss, terms):
    # test trs1 (created manually)
    ptrs3 = ptrss["ptrs3"]
    t2 = terms["t2"]
    # t2_id_before = id(t2) # get id to check for sideeffects
    t2_copy = deepcopy(t2) # create copy to check for sideeffects
    
    # test result of running t2 
    rt = ptrs3.non_probabilistic_deterministic_path(t2, depth=10)
    print(rt)
    _, _, t, _, _ = rt.get_last_layer_nodes().pop().get_value().data
    assert t == terms["ctr8"]
    # if side effect => t2 != t2_copy, no side effect => t2 == t2_copy
    assert t2 == t2_copy

    trs11 = ptrss["pTRS11"]
    startterm = terms["compound42"]
    endterm = terms["42"]

    # print(trs11)
    rt = trs11.non_probabilistic_deterministic_path(startterm, depth=40)
    _, _, t, _, _ = rt.get_last_layer_nodes().pop().get_value().data
    assert t == endterm
    