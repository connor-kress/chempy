import numpy as np
import numpy.typing as npt


class BalancingError(Exception):
    def __init__(
        self,
        message: str,
        results: npt.NDArray[np.float_],
        ratios: npt.NDArray[np.float_] = None,
        solution: npt.NDArray[np.float_] = None,
    ) -> None:
        """Captures calculation data to provide information on error."""
        super().__init__(message)

        self.results = results
        self.ratios = ratios
        self.solution = solution
