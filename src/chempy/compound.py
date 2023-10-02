"""
TODO: Add parsing for state (s, l, g, aq). (Enum? What else does this affect?)
TODO: Move `LEFT\RIGHT_DELS` into a file in `data` directory.
TODO: Add more data for elements for atomic mass etc. (Isotope mass data?)
"""

from .data.elements import ATOMIC_NUMS
from .element import Element
from .printable import Printable
from .utils import (
    get_closing_index,
    tokenize_string,
    parse_elements_from_tokens
)
from collections import Counter
from typing import Self
import numpy as np

NUMBER_OF_ELEMENTS = len(ATOMIC_NUMS)
LEFT_DELS = ['(', '[', '{']
RIGHT_DELS = [')', ']', '}']


class Compound(Printable):
    def __init__(self, elements: Counter[Element], string: str = None):
        """Constructs a compound from a number of `Element`s and an optional
        `string` to refer to the `Compound` by.
        """
        self.elements = elements
        self.string = string

        vector = np.zeros(NUMBER_OF_ELEMENTS, dtype=int)
        for element, freq in self.elements.items():
            vector += element.vector * freq
        self.vector = vector

    def __str__(self) -> str:
        if self.string is not None:
            return self.string
        
        cmp_str = ''
        for element, freq in self.elements.items():
            if freq != 1:
                cmp_str += f'{element}{freq}'
            else:
                cmp_str += f'{element}'
        return cmp_str
    
    def __repr__(self) -> str:
        return f"""
            {self.__class__.__name__}(
                {self.elements},
                {'None' if self.string is None else f"'{self.string}'"},
            )
        """
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Compound):
            raise ValueError('Connot compare the types `Compound` '
                             f'and `{type(other).__name__}`')
        return self.elements == other.elements
    
    def __hash__(self) -> int:
        element_data = list(self.elements.items())
        element_data.sort(key=lambda tup: ATOMIC_NUMS[tup[0].symbol])
        return hash(tuple(element_data))
    
    def latex(self) -> str:
        """Returns a LaTeX string representation of the compound."""
        tokens = tokenize_string(self.string)
        previous_token = None
        string_frags = []
        while tokens:
            token = tokens.pop()
            if isinstance(token, Element):
                string_frags.append(token.latex())
            elif token in LEFT_DELS:
                del_str = fr'\{token}' if token == '{' else token
                front_space = '' if tokens and tokens[-1]\
                                    in LEFT_DELS else r'\!'
                string_frags.append(fr'{front_space}\left{del_str}')
            elif token in RIGHT_DELS:
                del_str = fr'\{token}' if token == '}' else token
                back_space = r'\!' if isinstance(previous_token,
                                                 Element) else ''
                string_frags.append(fr'\right{del_str}{back_space}')
            elif isinstance(token, int):
                if tokens[-1] in RIGHT_DELS:
                    back_space = '' if previous_token in LEFT_DELS\
                                    or previous_token in RIGHT_DELS else r'\!'
                    string_frags.append(f'_{{{token}}}{back_space}')
                elif isinstance(tokens[-1], Element):
                    count, token = token, tokens.pop()
                    string_frags.append(token.latex(count))
                else:
                    raise Exception('Unknown error.')
            else:
                raise Exception('Unknown error.')
            previous_token = token
        return ''.join(reversed(string_frags))

    def copy(self) -> Self:
        return self.__class__(self.elements.copy(), self.string)

    @classmethod
    def parse_from_string(cls, compound_string: str) -> Self:
        """Parses a given string into a `Compound` instance."""
        compound_string = compound_string.replace(' ', '')
        if not all(
            c.isalnum()
                or c in LEFT_DELS
                or c in RIGHT_DELS
            for c in compound_string
        ):
            raise ValueError('Invalid character found while '
                             f'parsing "{compound_string}".')
        if (sum(c in LEFT_DELS for c in compound_string)
            != sum(c in RIGHT_DELS for c in compound_string)):
            raise ValueError('Unequal left and right delimiters '
                             f'in "{compound_string}".')
        
        tokens = tokenize_string(compound_string)
        elements = parse_elements_from_tokens(tokens)

        while tokens[0] in LEFT_DELS\
            and get_closing_index(1, tokens[0], tokens) == len(tokens)-1:
            tokens.pop(0); tokens.pop()
            compound_string = compound_string[1:-1]
        
        return cls(elements, compound_string)

    @classmethod
    def parse_from_list(cls, compound_strings: list[str]) -> list[Self]:
        """Parses a list of strings into a list of `Compound`s."""
        return list(map(cls.parse_from_string, compound_strings))
