from .data.elements import ATOMIC_NUMS
from .element import Element
from collections import Counter
from typing import Self
import numpy as np

NUMBER_OF_ELEMENTS = len(ATOMIC_NUMS)
LEFT_DELS = ['(', '[', '{']
RIGHT_DELS = [')', ']', '}']


class Compound:
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

    @staticmethod
    def parse_from_string(compound_string: str) -> Self:
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
        
        tokens = Compound._parse_to_tokens(compound_string)
        elements = Compound._parse_from_tokens(tokens)

        return Compound(elements, compound_string)
    
    @staticmethod
    def _parse_to_tokens(compound_string: str) -> list[Element | str | int]:
        """Tokenizes a string representing a compound for further parsing."""
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
        if num_str or lower:
            raise ValueError(f'Invalid compound syntax "{compound_string}"')
        return tokens

    @staticmethod
    def _parse_from_tokens(
        tokens: list[Element | str | int]
    ) -> Counter[Element]:
        """Parses a list of tokens into a standardized `Counter` of the
        `Element`s represented.
        """
        def get_closing_index(start: int, l_del: str) -> int:
            """Returns the closing index of an opened delimeter."""
            r_del = RIGHT_DELS[LEFT_DELS.index(l_del)]
            count = 0
            for i in range(start, len(tokens)):
                frag = tokens[i]
                if frag == l_del:
                    count += 1
                elif frag == r_del:
                    if count == 0:
                        return i
                    count -= 1
            raise ValueError(
                f'"{l_del}" opened at i={start-1} was never closed.'
            )

        if isinstance(tokens[0], int):
            raise ValueError('Invalid compound syntax.')
        
        elements = Counter()
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in LEFT_DELS:
                close_idx = get_closing_index(i+1, token)
                inside = Compound._parse_from_tokens(tokens[i+1:close_idx])
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
