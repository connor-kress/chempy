"""
TODO: Make `extended` try the abstracted extension and then `.balance`
before using the current method for better answers.
"""

from .printable import Printable
from .errors import BalancingError
from .utils import (
    solve,
    tokenize_string,
    CompoundCounter,
)
from .compound import Compound
from typing import Self
from itertools import chain
import numpy as np


class Equation(Printable):
    def __init__(
            self,
            reactants: CompoundCounter[Compound],
            products: CompoundCounter[Compound],
        ) -> None:
        """Constructs a chemical equation from `reactants` and `products`."""
        if not isinstance(reactants, CompoundCounter):
            raise TypeError('Parameters `reactants` and `products` to '
                            '`Equation.__init__` must be `CompoundCounter`s, '
                            f'not `{reactants.__class__.__name__}`s.')
        elif not isinstance(products, CompoundCounter):
            raise TypeError('Parameters `reactants` and `products` to '
                            '`Equation.__init__` must be `CompoundCounter`s, '
                            f'not `{products.__class__.__name__}`s.')
        self.reactants = reactants
        self.products = products
    
    def __str__(self) -> str:
        reactants_string = ' + '.join([
            f'{coef}({comp})' if coef != 1 else str(comp)
            for comp, coef in self.reactants.items()
        ])
        products_string = ' + '.join([
            f'{coef}({comp})' if coef != 1 else str(comp)
            for comp, coef in self.products.items()
        ])
        return reactants_string + ' -> ' + products_string

    def __repr__(self) -> str:
        return f"""
            {self.__class__.__name__}(
                {self.reactants},
                {self.products},
            )
        """
    
    def latex(self) -> str:
        """Returns a LaTeX string representation of the equation."""
        reactant_strs = [
            fr'{coef}\,{comp.latex()}' if coef != 1 else comp.latex()
            for comp, coef in self.reactants.items()
        ]
        product_strs = [
            fr'{coef}\,{comp.latex()}' if coef != 1 else comp.latex()
            for comp, coef in self.products.items()
        ]
        return '+'.join(reactant_strs)\
            + r'\rightarrow'\
            + '+'.join(product_strs)
    
    def copy(self) -> Self:
        return self.__class__(
            self.reactants.copy(),
            self.products.copy(),
        )
    
    def _set_self(self, new_self: Self) -> None:
        """Sets the attributes of `self` to the attributes of `new_self`.
        
        Required to get around Python's mutability syntax/rules."""
        self.reactants = new_self.reactants
        self.products = new_self.products
        self.coefficients = new_self.coefficients
    
    def __mul__(self, other: int) -> Self:
        """Returns an `Equation` with the coefficients of `self`
        multiplied by an integer.
        """
        if not isinstance(other, int):
            raise TypeError('`Equation`s can only be multiplied by '
                            f'integers, not `{other.__class__.__name__}`s.')
        reactants = self.reactants * other
        products = self.products * other
        return self.__class__(reactants, products)
    
    def __rmul__(self, other: int) -> Self:
        return self * other

    def __add__(self, other: Self) -> Self:
        """Returns an addition of two `Equation`s in parallel."""
        if not isinstance(other, Equation):
            raise TypeError('`Equation`s can only be added to other '
                            f'`Equation`s, not `{other.__class__.__name__}`s.')
        reactants = self.reactants + other.reactants
        products = self.products + other.products
        return self.__class__(reactants, products)
    
    def __sub__(self, other: Self) -> Self:
        return self + -1*other
    
    def __truediv__(self, other: int) -> Self:
        """Returns an `Equation` with the coefficients of `self`
        divided by an integer.
        """
        if not isinstance(other, int):
            raise TypeError('`Equation`s can only be multiplied by '
                            f'integers, not `{other.__class__.__name__}`s.')
        reactants = self.reactants / other
        products = self.products / other
        return self.__class__(reactants, products)
    
    def _get_max_coefficient(self) -> int:
        """Returns the maximum integer that can be reduced out of
        the coefficients of `self`.
        """
        return int(np.gcd.reduce([coef for coef in
                                  chain(self.reactants.values(),
                                        self.products.values())]))
    
    def reduced(self) -> Self:
        """Returns a reduced coefficient version of `self`.
        
        Examples
        --------
        from chempy import Equation
        >>> equation = Equation.parse_from_string('2H2O -> 2H2 + 2O')
        >>> equation
        2(H2O) -> 2(H2) + 2(O)
        >>> equation.reduced()
        H2O -> H2 + O
        """
        return self / self._get_max_coefficient()
    
    def reduce(self) -> None:
        """A mutable version of `Equation.reduced` that updates `self` to
        the reduced version of `self`.
        """
        self._set_self(self.reduced())
    
    def is_reduced(self) -> bool:
        """"Returns `True` if the `Equation` is reduced else `False`."""
        return self._get_max_coefficient() == 1
    
    def assert_reduced(self) -> Self:
        """Asserts that `self` is reduced and returns `self`."""
        if not self.is_reduced():
            raise AssertionError(f'The equation {self} was not '
                                    'reduced as asserted.')
        return self
    
    def _max_mul_in_reactants(self, compounds: CompoundCounter) -> int:
        """Returns the maximum multiple of `compounds` contained
        within `self.reactants`.
        """
        return int(min([
            self.reactants[comp] / coef
            for comp, coef in compounds.items()
        ]))

    def _max_mul_in_products(self, compounds: CompoundCounter) -> int:
        """Returns the maximum multiple of `compounds` contained
        within `self.products`.
        """
        return int(min([
            self.products[comp] / coef
            for comp, coef in compounds.items()
        ]))

    def extended(self, other: Self | list[Self]) -> Self:
        """Returns an `Equation` representing an extension of `self` by
        applying the reaction described in `other` to the products of `self`.

        If a list of `Equation`s is passed, they will each be applied in the
        order given.

        Examples
        --------
        >>> from chempy import Equation
        >>> equation1 = Equation.parse_from_string('H2O2 -> H2 + O2')
        >>> equation2 = Equation.parse_from_string('O2 -> 2(O)')
        >>> equation1.extended(equation2)
        H2O2 -> H2 + 2(O)
        """
        if not isinstance(other, (Equation, list)):
            raise TypeError('`Equation.extended` can only be passed other '
                            '`Equation` or `list[Equation] instances.')
        
        if isinstance(other, list):
            current = self.copy()
            for equation in other:
                current = current.extended(equation)
            return current
        
        reactants_set = set(self.reactants)
        products_set = set(other.products)
        intermediates = set(self.products).intersection(other.reactants)
        reactants_set.update(set(other.reactants).difference(intermediates))
        products_set.update(set(self.products).difference(intermediates))
        reactants = CompoundCounter({comp: 1 for comp in reactants_set})
        products = CompoundCounter({comp: 1 for comp in products_set})

        equation = self.__class__(reactants, products)
        try:
            equation.balance()
        except BalancingError:
            pass
        else:
            return equation
        
        mul = self._max_mul_in_products(other.reactants)
        intermediates = other.reactants * mul
        missing_reactants = (other.reactants - intermediates).max(0)
        reactants = self.reactants + missing_reactants
        if intermediates:
            products = self.products + other.products*mul - intermediates
        else:
            products = self.products + other.products*(1+mul)
        # print(f'mul = {mul}')
        # print(f'intermediates = {intermediates}')
        # print(f'missing_reactants = {missing_reactants}')
        # print(f'reactants = {reactants}')
        # print(f'products = {products}')
        
        equation = self.__class__(reactants, products)
        if self.is_balanced() and other.is_balanced():
            assert equation.is_balanced()
        return equation.reduced()

    def extend(self, other: Self) -> None:
        """A mutable version of `Equation.extended` that updates `self` to
        the extension of `self` and `other`.
        """
        if not isinstance(other, (Equation, list)):
            raise TypeError('`Equation.extend` can only be passed other '
                            '`Equation` or `list[Equation] instances.')
        self._set_self(self.extended(other))

    def is_balanced(self) -> bool:
        """"Returns `True` if the `Equation` is balanced else `False`."""
        reactants_vec = np.sum(np.array([
            comp.vector * coef
            for comp, coef in self.reactants.items()
        ]), axis=0)
        products_vec = np.sum(np.array([
            comp.vector * coef
            for comp, coef in self.products.items()
        ]), axis=0)

        return np.allclose(reactants_vec, products_vec)
    
    def assert_balanced(self) -> Self:
        """Asserts that `self` is balanced and returns `self`."""
        if not self.is_balanced():
            raise AssertionError(f'The equation {self} was not '
                                    'balanced as asserted.')
        return self

    def balance(self) -> None:
        """Finds the coefficients corresponding to the balanced `Equation`
        and writes them to `self.coefficients`.
        """
        reactants = list(self.reactants.keys())
        products = list(self.products.keys())
        reactant_vecs = np.array([comp.vector for comp in reactants])
        product_vecs = np.array([comp.vector for comp in products])
    
        system = np.hstack((reactant_vecs.T, -product_vecs.T))
        coefficients = solve(system)

        reactant_coefs = coefficients[:len(reactants)]
        product_coefs = coefficients[len(reactants):]
        for reactant, coef in zip(reactants, reactant_coefs):
            self.reactants[reactant] = coef
        for product, coef in zip(products, product_coefs):
            self.products[product] = coef
        
        if not self.is_balanced():
            raise Exception(f'An equation was incorrectly balanced to {self}')
    
    def balanced(self) -> Self:
        """Returns a balanced version of `self`."""
        equation = self.copy()
        equation.balance()
        return equation
    
    @classmethod
    def parse_from_string(cls, equation_string):
        """Parses a given string into an `Equation` instance."""
        if '->' in equation_string:
            reactants_str, products_str = equation_string.split('->')
        elif '→' in equation_string:
            reactants_str, products_str = equation_string.split('→')
        else:
            raise ValueError('Invalid equation syntax. Seperate '
                             'reactants and products with "->".')
        
        reactants = CompoundCounter()
        for reactant_str in reactants_str.split('+'):
            first_token = tokenize_string(reactant_str)[0]
            if isinstance(first_token, int):
                reactant = Compound.parse_from_string(
                    reactant_str.strip().removeprefix(str(first_token))
                )
                reactants[reactant] += first_token
            else:
                reactant = Compound.parse_from_string(reactant_str)
                reactants[reactant] += 1
        
        products = CompoundCounter()
        for product_str in products_str.split('+'):
            first_token = tokenize_string(product_str)[0]
            if isinstance(first_token, int):
                product = Compound.parse_from_string(
                    product_str.strip().removeprefix(str(first_token))
                )
                products[product] += first_token
            else:
                product = Compound.parse_from_string(product_str)
                products[product] += 1

        return cls(reactants, products)

    @classmethod
    def parse_from_list(cls, equation_strings: list[str]) -> list[Self]:
        """Parses a list of strings into a list of `Compound`s."""
        return list(map(cls.parse_from_string, equation_strings))
