from pathlib import Path

from prevision.config import Config, STRATEGY_MAPPING, AVAILABLE_FORMATS
from prevision.core.evaluation_strategy import *
from prevision.core.parse.ari import check_format_and_choose_parser
from prevision.core.parse.utility import parse_term


def create_config(raw_data: dict):
    """
    Checks whether or not the passed dict specifies valid arguments for prevision.
    If so, creates a config, else throws an exception.

    Parameters
    ----------
    raw_data: dict
    - Expected keys in the raw data dictionary (before validation):
        - input_file: str
            - must be a valid .txt file containing the ptrs in ari format
        - term: str
            - must be a valid term
        - probabilistic: str
            - {'true', '1', 'yes', 'y'} or {'false', '0', 'no', 'n'} (insensitive to capitalization)
        - deterministic: str
            - like probabilistic
        - depth: str
            - a string convertible to an int (e.g. "1")
        - strategy: EvaluationStrategy
            - one of ['full', 'o', 'i', 'lo', 'ro', 'li', 'ri']
        - format: str
            - a valid format (see config)
        - output_path: str
            - must be a directory.

    Returns
    -------
    Config

    Raises
    ------
    KeyError, ValueError
    """

    # try to get all required raw data
    try:
        input_file_raw      :str = str(raw_data['input_file'])          # (1/8)
        term_raw            :str = str(raw_data['term'])                # (2/8)
        probabilistic_raw   :str = str(raw_data['probabilistic'])       # (3/8)
        deterministic_raw   :str = str(raw_data['deterministic'])       # (4/8)
        depth_raw           :str = str(raw_data['depth'])               # (5/8)
        strategy_raw        :str = str(raw_data['strategy'])            # (6/8)
        frmt_raw            :str = str(raw_data['format'])              # (7/8)
        output_path_raw     :str = str(raw_data['output_dir'])          # (8/8)
    except KeyError as e:
        raise KeyError(f"Could not find a value for the required field {e}.")
    
    # validate inputfile and parse ptrs (1/8)
    input_file = Path(input_file_raw).absolute()
    if not input_file.is_file():
        raise ValueError("Path to input file invalid. Must specify a file.")
    if not (input_file.suffix == '.ari' or input_file.suffix == '.txt'):
        raise ValueError(f"Wrong format of input file: {input_file.suffix}. Needs to be .txt")

    with open(input_file, "rb") as f:
        in_str = f.read().decode("UTF-8")
        parser = check_format_and_choose_parser(in_str)
        ptrs, funcs = parser(in_str)

    # parse term (2/8)
    _, term = parse_term(term_raw, constants=[symbol for symbol, arity in funcs if arity == 0], functions=dict(funcs))
    
    # handle probabilistic (3/8)
    match probabilistic_raw.lower():
        case 'true' | '1' | 'yes' | 'y':
            probabilistic = True
        case 'false' | '0' | 'no' | 'n':
            probabilistic = False
        case _:
            raise ValueError(f"Invalid input for probabilistic: {probabilistic_raw}")
    # deterministic (4/8)
    match deterministic_raw.lower():
        case 'true' | '1' | 'yes' | 'y':
            deterministic = True
        case 'false' | '0' | 'no' | 'n':
            deterministic = False
        case _:
            raise ValueError(f"Invalid input for deterministic: {deterministic_raw}")
    # depth (5/8)
    try:
        depth = int(depth_raw)
    except ValueError:
        raise ValueError(f"Invalid input for depth: {depth_raw}.")
    # strategy (6/8)
    try:
        strategy = STRATEGY_MAPPING[strategy_raw]
    except KeyError:
        raise ValueError(f"Invalid evaluation strategy: {strategy_raw}.")
    # format (7/8)
    if not frmt_raw in AVAILABLE_FORMATS:
        raise ValueError(f"Invalid format: {frmt_raw}")
    else:
        frmt = frmt_raw
    # output_path (8/8)
    output_path = Path(output_path_raw).absolute()
    if not output_path.is_dir():
        raise ValueError(f"Path to output invalid: {output_path_raw}. Must specify a folder.")
    
    # success
    return Config(
        INPUT_FILE = input_file,
        PTRS = ptrs,
        TERM = term,
        PROBABILISTIC = probabilistic,
        DETERMINISTIC = deterministic,
        DEPTH = depth,
        STRATEGY = strategy,
        FORMAT = frmt,
        OUTPUT_PATH = output_path
    )