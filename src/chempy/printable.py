from abc import ABC, abstractmethod


class Printable(ABC):
    def _repr_latex_(self) -> str:
        """IPython/Jupyter LaTeX printing."""
        return fr'$\displaystyle {self.latex()}$'

    @abstractmethod
    def latex(self) -> str:
        """Returns a LaTeX string representation of the expression."""
