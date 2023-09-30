from utils import solve
from compound import Compound
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

    def balance(self) -> None:
        """Finds the coefficients corresponding to the balanced `Equation`
        and writes them to `self.coefficients`.
        """
        reactant_vecs = np.array([comp.vector for comp in self.reactants])
        product_vecs = np.array([comp.vector for comp in self.products])
    
        system = np.hstack((reactant_vecs.T, -product_vecs.T))
        self.coefficients = list(solve(system))
    
    def balanced(self) -> Self:
        """Returns a balanced version of `self`."""
        self.balance()
        return self
    
    @staticmethod
    def parse_from_string(equation_string):
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

        return Equation(reactants, products)
