from data.elements import ATOMIC_NUMS
from collections import Counter
from element import Element
import numpy as np

NUMBER_OF_ELEMENTS = len(ATOMIC_NUMS)


class Compound:
    def __init__(self, elements: Counter[Element], string: str=None):
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
                {'None' if self.string is None else f"'{self.string}'"}
            )
        """
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Compound):
            raise ValueError(
                f'Connot compare the types `Compound` and `{type(other).__name__}`'
            )
        return self.elements == other.elements
