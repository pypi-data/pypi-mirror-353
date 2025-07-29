def test_full(evaluationStratgies, terms):
    subjectTerm = terms["eTSubjectTerm"]
    patternTerm = terms["eTPatternTerm"]

    reds = [x for x, y in evaluationStratgies["F"].generate_redexes(patternTerm, subjectTerm)]
    assert reds == [[0], [1], [0, 1], [1, 1]]

def test_outermost(evaluationStratgies, terms):
    subjectTerm = terms["eTSubjectTerm"]
    patternTerm = terms["eTPatternTerm"]

    reds = [x for x, y in evaluationStratgies["O"].generate_redexes(patternTerm, subjectTerm)]
    assert reds == [[0], [1]]

def test_innermost(evaluationStratgies, terms):
    subjectTerm = terms["eTSubjectTerm"]
    patternTerm = terms["eTPatternTerm"]

    reds = [x for x, y in evaluationStratgies["I"].generate_redexes(patternTerm, subjectTerm)]
    assert reds == [[0, 1], [1, 1]]

def test_leftmost_outermost(evaluationStratgies, terms):
    subjectTerm = terms["eTSubjectTerm"]
    patternTerm = terms["eTPatternTerm"]

    reds = [x for x, y in evaluationStratgies["LO"].generate_redexes(patternTerm, subjectTerm)]
    assert reds == [[0]]

def test_leftmost_innermost(evaluationStratgies, terms):
    subjectTerm = terms["eTSubjectTerm"]
    patternTerm = terms["eTPatternTerm"]

    reds = [x for x, y in evaluationStratgies["LI"].generate_redexes(patternTerm, subjectTerm)]
    assert reds == [[0, 1]]

def test_rightmost_outermost(evaluationStratgies, terms):
    subjectTerm = terms["eTSubjectTerm"]
    patternTerm = terms["eTPatternTerm"]

    reds = [x for x, y in evaluationStratgies["RO"].generate_redexes(patternTerm, subjectTerm)]
    assert reds == [[1]]

def test_rightmost_innermost(evaluationStratgies, terms):
    subjectTerm = terms["eTSubjectTerm"]
    patternTerm = terms["eTPatternTerm"]

    reds = [x for x, y in evaluationStratgies["RI"].generate_redexes(patternTerm, subjectTerm)]
    assert reds == [[1, 1]]