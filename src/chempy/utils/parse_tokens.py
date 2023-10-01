from ..element import Element
from .get_index import get_closing_index
from collections import Counter

LEFT_DELS = ['(', '[', '{']
RIGHT_DELS = [')', ']', '}']


def parse_elements_from_tokens(
    tokens: list[Element | str | int]
) -> Counter[Element]:
    """Parses a list of tokens into a standardized `Counter` of the
    `Element`s represented.
    """
    if not tokens or isinstance(tokens[0], int):
        raise ValueError(f'Invalid compound syntax. {tokens}')
    
    elements = Counter()
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in LEFT_DELS:
            close_idx = get_closing_index(i+1, token, tokens)
            inside = parse_elements_from_tokens(tokens[i+1:close_idx])
            if (close_idx+1 <= len(tokens)-1
                and isinstance(tokens[close_idx+1], int)):
                mul = tokens[close_idx+1]
                elements += Counter({e: n*mul for e, n in inside.items()})
                i = close_idx + 2
            else:
                elements += inside
                i = close_idx + 1
            continue
        if token in RIGHT_DELS:
            raise ValueError('Invalid compound syntax (delimeters).')
        if isinstance(token, Element):
            if i+1 < len(tokens) and isinstance(tokens[i+1], int):
                elements[token] += tokens[i+1]
            else:
                elements[token] += 1
        i += 1
    return elements
