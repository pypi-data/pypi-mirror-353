def test_run_ptrs1(ptrss, terms):
    # test ptrs1 (created manually)
    ptrs1 = ptrss["ptrs1"]
    rt = ptrs1.non_probabilistic_deterministic_path(terms["ptrs1_start_s0"], depth=10000)
    _, _, t, _, _ = rt.get_last_layer_nodes().pop().get_value().data
    
    
    assert t == terms["nf"]


# def test_eval_dist_ptrs1(ptrss, terms):
#     print("Test PTRS1:")
#     ptrs1 = ptrss["ptrs1"]
#     print("_________________________________________________________")
#     print("Evaluation of distribution of ptrs1:\n")
#     print(ptrs1.eval_distribution(terms["ptrs1_start_s0"]))

# def test_eval_dist_ptrs2(ptrss, terms):
#     print("Test PTRS2:")
#     ptrs2 = ptrss["ptrs2"]
#     print("_________________________________________________________")
#     print("Evaluation of distribution of ptrs2:\n")
#     print(ptrs2.eval_distribution(terms["ptrs2_start_fg"]))

# def test_defeat_nonterminism(ptrss, terms):
#     print("Testing defeat_nonterminism method:")
#     print("_________________________________________________________")
#     print(f"Building whole Tree of PTRS2 with {terms["ptrs2_start_fg"]} as start term:")
#     ptrs2 = ptrss["ptrs2"]
#     print(ptrs2.defeat_nondeterminism(terms["ptrs2_start_fg"], 3))

# def test_probabilistic_non_deterministic_tree(converter, ptrss, terms):
#     print("Testing probabilistic_non_deterministic_tree method:")
#     print("_________________________________________________________")
#     print(f"Building whole Tree of PTRS1 with {terms["ptrs1_start_s0"]} as start term:")
#     conv = converter["c1"]
#     ptrs1 = ptrss["ptrs1"]
#     computation_tree = ptrs1.probabilistic_non_deterministic_tree(terms["ptrs1_start_s0"])
#     conv.rt_to_pd(computation_tree)

def test_probabilistic_deterministic_trees(converter, ptrss, terms):
    c0 = converter["c1"]
    p0 = ptrss["ptrs1"]
    t0 = terms["ptrs1_start_s0"]

    rts0 = p0.probabilistic_deterministic_trees(t0)
    for i, rt in enumerate(rts0):
        c0.rt_to_pd(rt).write_png(f"prevision/tests/test_output/succs{i}.png")
    
    
    c1 = converter["c1"]
    p1 = ptrss["lists0"]
    t1 = terms["startTermPDTs"]
    
    rts1 = p1.probabilistic_deterministic_trees(t1)
    for i, rt in enumerate(rts1):
        c1.rt_to_pd(rt).write_png(f"prevision/tests/test_output/lists{i}.png")

    c2 = converter["c1"]
    p2 = ptrss["testPD"]
    t2 = terms["startTermPDTs2"]
    
    rts2 = p2.probabilistic_deterministic_trees(t2)
    for i, rt in enumerate(rts2):
        c2.rt_to_pd(rt).write_png(f"prevision/tests/test_output/testPD{i}.png")

def test_non_probabilistic_non_deterministic_trees(converter, ptrss, terms):
    c0 = converter["c1"]
    p0 = ptrss["testPD"]
    t0 = terms["startTermPDTs2"]
    
    rts0 = p0.non_probabilistic_non_deterministic_trees(t0)
    for i, rt in enumerate(rts0):
        c0.rt_to_pd(rt).write_png(f"prevision/tests/test_output/NPND_testPD{i}.png")