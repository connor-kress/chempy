class BalancingError(Exception):
    def __init__(
        self,
        message: str,
        results,
        ratios=None,
        solution=None
    ) -> None:
        """Captures calculation data to provide information on error."""
        super().__init__(message)

        self.results = results
        self.ratios = ratios
        self.solution = solution
