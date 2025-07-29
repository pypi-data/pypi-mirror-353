import os

from prevision.cli import parse_args
from prevision.config import Config, create_config
from prevision.core.evaluation_strategy import *
from prevision.core.ptrs_comp_tree_data import TreeData
from prevision.core.rose_tree import RoseTree
from prevision.core.rose_tree_converter import RTConv

def handler(cfg: Config):
    """This method """
    PTRS = cfg.PTRS
    TERM = cfg.TERM
    PROBABILISTIC = cfg.PROBABILISTIC
    DETERMINISTIC = cfg.DETERMINISTIC
    DEPTH = cfg.DEPTH
    STRATEGY = cfg.STRATEGY
    FORMAT = cfg.FORMAT
    OUTPUT_PATH = cfg.OUTPUT_PATH
    
    # Compute the requested tree(s)
    res: list[RoseTree[TreeData]]
    if PROBABILISTIC:
        if not DETERMINISTIC:
            res = [PTRS.probabilistic_non_deterministic_tree(TERM, DEPTH, STRATEGY)]
        else:
            res = PTRS.probabilistic_deterministic_trees(TERM, DEPTH, STRATEGY)
    else:
        if not DETERMINISTIC:
            res = PTRS.non_probabilistic_non_deterministic_trees(TERM, DEPTH, STRATEGY)
        else:
            if isinstance(STRATEGY, UniqueElementStrategy):
                res = [PTRS.non_probabilistic_deterministic_path(TERM, DEPTH, STRATEGY)]
            else:
                raise ValueError(
                    """
                    Non probabilistic deterministic computation tree evaluation\n
                    requires an evaluationstrategy which resolves to a unique\n
                    reducible expression (i.e. 'li', 'lo', 'ri', 'ro').
                    """)
    
    # convert each computation tree (rosetree) to a pydot
    converter = RTConv()
    dots = [converter.rt_to_pd(rt) for rt in res]


    for i, dot in enumerate(dots):
        fileName = f"Tree{i}.{FORMAT}"
        dot.write(os.path.join(OUTPUT_PATH, fileName), format=FORMAT, encoding="utf-8")

def main():
    raw = parse_args()
    cfg = create_config(raw)
    handler(cfg)

    print("End of program.")

if __name__ == "__main__":
    main()