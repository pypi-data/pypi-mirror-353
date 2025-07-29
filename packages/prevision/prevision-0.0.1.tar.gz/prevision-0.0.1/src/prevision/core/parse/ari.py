from typing import Callable

from prevision.core.ptrs import Ptrs
from prevision.core.parse import ParsePTRS, ParseTRS



def check_format_and_choose_parser(input_string: str) -> Callable[[str], tuple[Ptrs, list[tuple[str, int]]]]:
    if "(format PTRS)" in input_string:
        return ParsePTRS().parse_ptrs
    elif "(format TRS)" in input_string:
        return ParseTRS().parse_trs
    else:
        raise ValueError("""Error: Missing the specification (format \\{TRS, PTRS\\}).""")