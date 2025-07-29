# Command Parser
# Use pythons argparse library to parse the CLI arguments
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from prevision.config import STRATEGY_MAPPING, AVAILABLE_FORMATS

def parse_args() -> dict:
    """
    This function uses the argparse library to define an ArgumentParser which parses the passed arguments.
    It adds minimal functionality to ensure correct default values are set.

    Returns
    -------
    A dict satisfying the requirements of Config.
    """
    parser = ArgumentParser(
        prog='prevision',
        description="PReVision: A Probabilistic Term Rewrite System Visualization tool.",
        epilog="""\
the following options are mutually exclusive:
  * '--deterministic' (-d) and '--non-deterministic' (-b)
  * '--probabilistic' (-p) and '--non-probabilistic' (-q)

the default options are:
  * prevision -pb --depth 3 --strategy full --format png --output './'

available evaluation strategies:
  * 'full'    computes the entire computation tree
  * 'o'       evaluates all outermost reducible expressions at each step
  * 'i'       evaluates all innermost reducible expressions at each step
  * 'lo'      evaluates only the leftmost outermost reducible expression
  * 'ro'      evaluates only the rightmost outermost reducible expression
  * 'li'      evaluates only the leftmost innermost reducible expression
  * 'ri'      evaluates only the rightmost innermost reducible expression

available output formats:
  * ['canon', 'cmap', 'cmapx', 'cmapx_np', 'dia', 'dot', 'fig', 'gd',
     'gd2', 'gif', 'hpgl', 'imap', 'imap_np', 'ismap', 'jpe', 'jpeg',
     'jpg', 'mif', 'mp', 'pcl', 'pdf', 'pic', 'plain', 'plain-ext',
     'png', 'ps', 'ps2', 'svg', 'svgz', 'vml', 'vmlz', 'vrml', 'vtx',
     'wbmp', 'xdot', 'xlib']

example invocation of prevision:
  > prevision -pd -t 3 -o './results' -s 'lo' './input_file.ari' '(s (s x))'
  * description:
      The file input_file.ari in the current directory is parsed and the
      corresponding PTRS is built. Computes tree(s) with root (s (s x)),
      non-determinism resolved and probabilistic choices shown. Only
      evaluates the leftmost outermost redex. The generated trees have a
      maximum depth of 3. Results will be saved in the './results'
      directory as PNG images.
    """,
        formatter_class=lambda prog: RawTextHelpFormatter(prog, max_help_position=34),
    )

    parser.add_argument(
        'input_file', 
        type=str,
        help="path to the input file with extension\n.ari or .txt\n\n", 
    )

    parser.add_argument(
        'term',
        type=str,
        help="term in ari format, root of the\ncomputation tree; " \
             "variables and\nfunctionsymbols are inferred\nfrom the given PTRS",
    )

    # Mutually exclusive group for probabilistic / non-probabilistic option
    group_probabilistic = parser.add_mutually_exclusive_group()
    group_probabilistic.add_argument(
        '-p',
        '--probabilistic',
        action='store_true',
        help="show probabilistic paths",
    )
    group_probabilistic.add_argument(
        '-q',
        '--non-probabilistic',
        action='store_true',
        help="resolve probabilistic paths",
    )

    # Mutually exclusive group for deterministic / non-deterministic option
    group_deterministic = parser.add_mutually_exclusive_group()
    group_deterministic.add_argument(
        '-d', 
        '--deterministic', 
        action='store_true', 
        help="resolve non-deterministic paths"
    )
    group_deterministic.add_argument(
        '-b',
        '--non-deterministic',
        action='store_true',
        help="show non-deterministic paths",
    )

    # DEPTH
    parser.add_argument(
        '-t',
        '--depth',
        type=int,
        default=3,
        metavar='<int>',
        help="maximum depth of the computation tree",
    )

    # STRATEGY
    parser.add_argument(
        '-s',
        '--strategy',
        type=str,
        choices=STRATEGY_MAPPING.keys(),
        default='full',
        metavar='<str>',
        help="evaluation strategy for filtering redexes",
    )

    # OUTPUT
    parser.add_argument(
        '-f',
        '--format',
        type=str,
        choices = AVAILABLE_FORMATS,
        default='png',
        metavar='<str>',
        help="the output format",
    )

    # OUTPUT
    parser.add_argument(
        '-o',
        '--output-dir',
        type=str,
        default=Path.cwd(),
        metavar='<dir>',
        help="output directory",
    )

    # parse arguments
    parsed_args = parser.parse_args()

    # set non_deterministic and probabilistic as default values.
    # if the other option has not been explicitly chosen
    # the default one must be true.
    if not parsed_args.deterministic:
        parsed_args.non_deterministic = True
    if not parsed_args.non_probabilistic:
        parsed_args.probabilistic = True

    return vars(parsed_args)