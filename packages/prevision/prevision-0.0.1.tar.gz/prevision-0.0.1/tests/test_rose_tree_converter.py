def test_RTConv(converter, rose_trees):
    c = converter["c1"]
    r = rose_trees["t1"]
    c.rt_to_pd(r).write_png("prevision/tests/test_output/testRTConv1.png")
    # print(f"Repr: {c.rt_to_pd(r).to_string()}")

def test_conv_ptrs(converter, ptrss, terms):
    c = converter["c1"]
    p = ptrss["ptrs1"]
    term = terms["ptrs1_start_s0"]

    rt = p.probabilistic_non_deterministic_tree(term)
    c.rt_to_pd(rt).write_png("prevision/tests/test_output/testRTConv2.png")
