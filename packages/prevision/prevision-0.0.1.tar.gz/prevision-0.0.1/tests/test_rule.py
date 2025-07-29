# def test_apply(terms, rules, strategies):
#     # modifies other
#     rules["rule1"].apply(terms["t1"], strategies["lmom"])
#     assert terms["t1"] == terms["ctr1"]
    
#     # expected values
#     assert rules["rule3"].apply(terms["t2"], strategies["lmom"]) == (True, terms["ctr2"])
#     assert rules["rule3"].apply(terms["ctr2"], strategies["lmom"]) == (True, terms["ctr3"])