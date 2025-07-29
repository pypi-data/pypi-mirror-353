from dataclasses import dataclass
from pathlib import Path

from prevision.core.evaluation_strategy import *
from prevision.core.ptrs import Ptrs
from prevision.core.term import Term


AVAILABLE_FORMATS: tuple[str, ...] = (
    'canon', 'cmap', 'cmapx', 'cmapx_np', 'dia', 'dot', 
    'fig', 'gd', 'gd2', 'gif', 'hpgl', 'imap', 
    'imap_np', 'ismap', 'jpe', 'jpeg', 'jpg', 
    'mif', 'mp', 'pcl', 'pdf', 'pic', 'plain', 
    'plain-ext', 'png', 'ps', 'ps2', 'svg', 'svgz', 
    'vml', 'vmlz', 'vrml', 'vtx', 'wbmp', 'xdot', 'xlib'
)

STRATEGY_MAPPING: dict[str, EvaluationStrategy] = {
    'full': Full(), 
    'o':    Outermost(), 
    'i':    Innermost(), 
    'lo':   LeftmostOutermost(), 
    'ro':   RightmostOutermost(), 
    'li':   LeftmostInnermost(), 
    'ri':   RightmostInnermost()
}

@dataclass
class Config:
    """
    Config for prevision.
    """
    INPUT_FILE: Path
    PTRS: Ptrs
    TERM: Term
    PROBABILISTIC: bool
    DETERMINISTIC: bool
    DEPTH: int
    STRATEGY: EvaluationStrategy
    FORMAT: str
    OUTPUT_PATH: Path

