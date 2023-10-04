from ..compound import Compound
from typing import Self
import numpy as np


class CompoundCounter(dict):
    def __str__(self) -> str:
        return f'{{{", ".join([f"{comp.string}: {n}" for comp, n in self.items()])}}}'
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'
    
    def __getitem__(self, compound: Compound) -> int:
        if not isinstance(compound, Compound):
            raise TypeError('`CompoundCounter`s keys are `Compound`s, '
                            f'not `{compound.__class__.__name__}`s.')
        if compound not in self.keys():
            return 0
        return super().__getitem__(compound)
    
    def __setitem__(self, compound: Compound, count: int) -> None:
        if isinstance(count, np.int_):
            count = int(count)
        if not isinstance(compound, Compound):
            raise TypeError('`CompoundCounter` only accepts `Compound`s as '
                            f'keys, not `{compound.__class__.__name__}`s.')
        if not isinstance(count, int):
            raise TypeError('`CompoundCounter` only accepts integers as '
                            f'values, not `{count.__class__.__name__}`s.')
        if count != 0:
            super().__setitem__(compound, count)
        elif compound in self.keys():
            del self[compound]

    def __add__(self, other: Self) -> Self:
        if not isinstance(other, CompoundCounter):
            raise TypeError('Cannot add `CompoundCounter` to '
                            f'`{other.__class__.__name__}`.')
        result = self.__class__()
        for key in set(self.keys()).union(other.keys()):
            result[key] = self[key] + other[key]
        return result
    
    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, CompoundCounter):
            raise TypeError(f'Cannot subtract `{other.__class__.__name__}` '
                            'from `CompoundCounter`.')
        return self + -1*other

    def __mul__(self, other: int | float) -> Self:
        if not isinstance(other, (int, float)):
            raise TypeError('Cannot multiply `CompoundCounter` with '
                            f'`{other.__class__.__name__}`.')
        if other == 0:
            return self.__class__()
        data = {comp: count*other for comp, count in self.items()}
        if not np.all([np.isclose(n, np.round(n)) for n in data.values()]):
            raise TypeError('Cannot multiply `CompoundCounter` with a '
                            "float that isn't near an integer.")
        return self.__class__({comp: int(np.round(count)) for comp, count in
                               data.items() if int(np.round(count)) != 0})
    
    def __rmul__(self, other: int) -> Self:
        return self * other
    
    def __truediv__(self, other: int) -> Self:
        if not isinstance(other, int):
            raise TypeError('Cannot divide `CompoundCounter` by '
                            f'`{other.__class__.__name__}`.')
        return self * (1/other)
    
    def __abs__(self) -> Self:
        return self.__class__({comp: abs(count) for comp, count
                               in self.items()})

    def max(self, n: int) -> Self:
        if not isinstance(n, int):
            raise TypeError('`CompoundCounter.max` only accepts integers.')
        return self.__class__({comp: max(count, n) for comp, count
                               in self.items()})
    
    def copy(self) -> Self:
        return self.__class__(super().copy())
