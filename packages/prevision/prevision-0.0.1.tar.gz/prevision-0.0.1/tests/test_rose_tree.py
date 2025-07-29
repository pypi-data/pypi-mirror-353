def test_pre_order(rose_trees):
    t1 = rose_trees["t1"]
    res = [(p, x.get_value()) for p, x in list(t1.pre_order())]
    expected = [([], 4), ([0], 2), ([0, 0], 1), ([0, 1], 3), ([1], 6), ([1, 0], 5), ([1, 1], 7)]
    assert res == expected

def test_reverse_pre_order(rose_trees):
    t1 = rose_trees["t1"]
    res = [(p, x.get_value()) for p, x in list(t1.reverse_pre_order())]
    expected = [([], 4), ([1], 6), ([1, 1], 7), ([1, 0], 5), ([0], 2), ([0, 1], 3), ([0, 0], 1)]
    assert res == expected

def test_post_order(rose_trees):
    t1 = rose_trees["t1"]
    res = [(p, x.get_value()) for p, x in list(t1.post_order())]
    expected = [([0, 0], 1), ([0, 1], 3), ([0], 2), ([1, 0], 5), ([1, 1], 7), ([1], 6), ([], 4)]
    assert res == expected

def test_reverse_post_order(rose_trees):
    t1 = rose_trees["t1"]
    res = [(p, x.get_value()) for p, x in list(t1.reverse_post_order())]
    expected = [([1, 1], 7), ([1, 0], 5), ([1], 6), ([0, 1], 3), ([0, 0], 1), ([0], 2), ([], 4)]
    assert res == expected

def test_level_order(rose_trees):
    t1 = rose_trees["t1"]
    res = [(p, x.get_value()) for p, x in list(t1.level_order())]
    expected = [([], 4), ([0], 2), ([1], 6), ([0, 0], 1), ([0, 1], 3), ([1, 0], 5), ([1, 1], 7)]
    assert res == expected

def test_get_last_layer_nodes(rose_trees):
    t1 = rose_trees["t1"]
    res = [x.get_value() for x in list(t1.get_last_layer_nodes())]
    expected = [1, 3, 5, 7]
    assert res == expected