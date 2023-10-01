from .data.elements import ATOMIC_NUMS
from typing import Self
import numpy as np

NUMBER_OF_ELEMENTS = len(ATOMIC_NUMS)


class Element:
    _all_elements: dict[str, Self] = {}

    def __new__(cls, symbol: str) -> Self:
        """"Caches all `Element` instances to avoid redundant memory usage."""
        if symbol in cls._all_elements.keys():
            return cls._all_elements[symbol]

        if symbol not in ATOMIC_NUMS.keys():
            raise ValueError(f'"{symbol}" is not a recognized element.')
        
        element = super().__new__(cls)
        cls._all_elements[symbol] = element
        return element
    
    def __init__(self, symbol: str) -> None:
        """This is ran when a new type of element is passed to `Element`.
        
        Takes the element `symbol` and derives other basic properties.
        """
        self.symbol = symbol
        self.number = ATOMIC_NUMS[symbol]

        temp = np.zeros(NUMBER_OF_ELEMENTS, dtype=int)
        temp[self.number-1] = 1  # np.sqrt(nth_prime(self.neutrons))
        self.vector = temp
    
    def __str__(self) -> str:
        return self.symbol
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.symbol}')"
    
    def __hash__(self):
        """`Element`s can be hashed with their ids as there is only ever one
        instance per unique type of element.
        """
        return id(self)
