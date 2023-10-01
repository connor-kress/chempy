from .utils import (
    solve,
    tokenize_string,
)
from .compound import Compound
from typing import Self
import numpy as np


class Equation:
    def __init__(
            self,
            reactants: list[Compound],
            products: list[Compound],
            coefficients: list[int] = None,
        ) -> None:
        """Constructs a chemical equation with or without coefficients."""
        self.reactants = reactants
        self.products = products
        self.coefficients = coefficients if coefficients is not None else [
            1 for _ in range(len(self.reactants) + len(self.products))
        ]
    
    def __str__(self) -> str:
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
            self.coefficients.copy(),
        )
    
    def _set_self(self, new_self: Self) -> None:
        """Sets the attributes of `self` to the attributes of `new_self`.
        
        Required to get around Python's mutability syntax/rules."""
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
    
    def extended_all(self, equations: list[Self]) -> Self:
        """Returns an `Equation` representing an extension of `self` by
        applying the reaction described in each `Equation` of `equations`
        in order.
        """
        current = self
        for equation in equations:
            current = current.extended(equation)
        return current
    
    def extend_all(self, equations: list[Self]) -> None:
        """A mutable version of `Equation.extended_all` that extends `self`
        with each `Equation` in `equations`.
        """
        for equation in equations:
            self.extend(equation)

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
        
        coefficients = []

        reactants = []
        for reactant_str in reactants_str.split('+'):
            first_token = tokenize_string(reactant_str)[0]
            if isinstance(first_token, int):
                coefficients.append(first_token)
                reactants.append(Compound.parse_from_string(
                    reactant_str.strip().removeprefix(str(first_token))
                ))
            else:
                coefficients.append(1)
                reactants.append(Compound.parse_from_string(reactant_str))
        
        products = []
        for product_str in products_str.split('+'):
            first_token = tokenize_string(product_str)[0]
            if isinstance(first_token, int):
                coefficients.append(first_token)
                products.append(Compound.parse_from_string(
                    product_str.strip().removeprefix(str(first_token))
                ))
            else:
                coefficients.append(1)
                products.append(Compound.parse_from_string(product_str))

        return cls(reactants, products, coefficients)

    @classmethod
    def parse_from_list(cls, equation_strings: list[str]) -> list[Self]:
        """Parses a list of strings into a list of `Compound`s."""
        return list(map(cls.parse_from_string, equation_strings))
