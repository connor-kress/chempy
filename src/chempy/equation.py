from .utils import solve
from .compound import Compound
from typing import Self
import numpy as np


class Equation:
    def __init__(
            self,
            reactants: list[Compound],
            products: list[Compound],
            coefficients: list[int] = None
        ) -> None:
        """Constructs a chemical equation with or without coefficients."""
        self.reactants = reactants
        self.products = products
        self.coefficients = coefficients
    
    def __str__(self) -> str:
        if self.coefficients is not None:
            return (
                ' + '.join([
                    f'{coef}({comp})' if coef!=1 else str(comp)
                    for comp, coef in zip(
                        self.reactants, self.coefficients[:len(self.reactants)]
                    )
                ])
                + ' -> '
                + ' + '.join([
                    f'{coef}({comp})' if coef!=1 else str(comp)
                    for comp, coef in zip(
                        self.products, self.coefficients[len(self.reactants):]
                    )
                ])
            )
        else:
            return (
                ' + '.join(map(str, self.reactants))
                + ' -> '
                + ' + '.join(map(str, self.products))
            )

    def __repr__(self) -> str:
        return f"""
            {self.__class__.__name__}(
                {self.reactants},
                {self.products},
                {self.coefficients},
            )
        """
    
    def copy(self) -> Self:
        return self.__class__(
            [comp.copy() for comp in self.reactants],
            [comp.copy() for comp in self.products],
            self.coefficients.copy()\
                if self.coefficients is not None else None,
        )
    
    def _set_self(self, new_self: Self) -> None:
        self.reactants = new_self.reactants
        self.products = new_self.products
        self.coefficients = new_self.coefficients

    def extended(self, other: Self) -> Self:
        """Returns an `Equation` representing an extension of `self` by
        applying the reaction described in `other` to the products of `self`.

        Examples
        --------
        >>> from chempy import Equation
        >>> equation1 = Equation.parse_from_string('H2O2 -> H2 + O2')
        >>> equation2 = Equation.parse_from_string('O2 -> O')
        >>> equation1.extended(equation2).balanced()
        H2O2 -> H2 + 2(O)
        """
        if not isinstance(other, Equation):
            raise TypeError('`Equation.extended` can only be passed '
                            'other `Equation` instances.')
        
        total_reactants = set(self.reactants)
        total_products = set(other.products)
        intermediates = set(self.products).intersection(other.reactants)
        total_reactants.update(set(other.reactants).difference(intermediates))
        total_products.update(set(self.products).difference(intermediates))
        
        return self.__class__(list(total_reactants), list(total_products))

    def extend(self, other: Self) -> None:
        """A mutable version of `Equation.extended` that updates `self` to
        the extension of `self` and `other`.
        """
        self._set_self(self.extended(other))
    
    def extended_all(self, others: list[Self]) -> Self:
        current = self
        for other in others:
            current = current.extended(other)
        return current
    
    def extend_all(self, others: list[Self]) -> None:
        for other in others:
            self.extend(other)

    def is_balanced(self) -> bool:
        """"Returns `True` if the `Equation` is balanced else `False`."""
        if self.coefficients is None:
            return False
        
        reactants_vec = np.sum(np.array([
            comp.vector * coef
            for comp, coef in zip(
                self.reactants, self.coefficients[:len(self.reactants)]
            )
        ]), axis=0)
        products_vec = np.sum(np.array([
            comp.vector * coef
            for comp, coef in zip(
                self.products, self.coefficients[len(self.reactants):]
            )
        ]), axis=0)

        return np.all(reactants_vec == products_vec)
    
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
        reactant_vecs = np.array([comp.vector for comp in self.reactants])
        product_vecs = np.array([comp.vector for comp in self.products])
    
        system = np.hstack((reactant_vecs.T, -product_vecs.T))
        self.coefficients = list(solve(system))
        if not self.is_balanced():
            raise Exception(f'An equation was incorrectly balanced to {self}')
    
    def balanced(self) -> Self:
        """Returns a balanced version of `self`."""
        self.balance()
        return self
    
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

        reactants = list(map(Compound.parse_from_string, reactants_str.split('+')))
        products = list(map(Compound.parse_from_string, products_str.split('+')))

        return cls(reactants, products)
