from typing import Optional

from .term import Term, Position
from .prule import PRule
    
class TreeData:
    def __init__(self, data):
        self.data = data
    
class ResultTreeData(TreeData):
    def __init__(self, rule: Optional[PRule], probability: float, t: Term, pos: Optional[Position], edgeLabel: str):
        self.data = (rule, probability, t, pos, edgeLabel)

    def __str__(self) -> str:
        return f"{self.data[1]} :\\text{{{self.data[2]}}}"
    
class NonDeterminismData(TreeData):
    def __init__(self, ruleName: str, position: Position):
        super().__init__((ruleName, position))

    def __str__(self) -> str:
        pos = self.data[1].indices
        if not pos:
            pos_str = "\\\\varepsilon"
        else:
            pos_str = ".".join([str(x) for x in pos])
            
        return f"\\text{{{self.data[0]}, }}{pos_str}"