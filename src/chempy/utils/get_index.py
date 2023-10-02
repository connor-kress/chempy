from ..data import  LEFT_DELS, RIGHT_DELS
from ..element import Element


def get_closing_index(start: int, l_del: str,
                      tokens: list[Element | str | int]) -> int:
    """Returns the closing index of an opened delimeter."""
    r_del = RIGHT_DELS[LEFT_DELS.index(l_del)]
    count = 0
    for i in range(start, len(tokens)):
        token = tokens[i]
        if token == l_del:
            count += 1
        elif token == r_del:
            if count == 0:
                return i
            count -= 1
    raise ValueError(f'"{l_del}" opened at i={start-1} was never closed.')
