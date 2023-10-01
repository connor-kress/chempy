from ..element import Element

LEFT_DELS = ['(', '[', '{']
RIGHT_DELS = [')', ']', '}']


def tokenize_string(compound_string: str) -> list[Element | str | int]:
    """Tokenizes a string representing a compound for further parsing."""
    compound_string = compound_string.replace(' ', '')
    tokens = []
    num_str = ''
    lower = ''
    for c in reversed(compound_string):
        if c.isdigit():
            if lower:
                raise ValueError('Invalid compound syntax '
                                    f'"{compound_string}"')
            num_str = c + num_str
            continue
        if num_str:
            tokens.insert(0, int(num_str))
            num_str = ''
        if c in LEFT_DELS + RIGHT_DELS:
            if lower:
                raise ValueError('Invalid compound syntax '
                                    f'"{compound_string}"')
            tokens.insert(0, c)
        elif c.islower():
            lower = c + lower
        elif lower:
            tokens.insert(0, Element(c+lower))
            lower = ''
        else:
            tokens.insert(0, Element(c))
    if lower:
        raise ValueError(f'Invalid compound syntax "{compound_string}"')
    if num_str:
        tokens.insert(0, int(num_str))
    return tokens
