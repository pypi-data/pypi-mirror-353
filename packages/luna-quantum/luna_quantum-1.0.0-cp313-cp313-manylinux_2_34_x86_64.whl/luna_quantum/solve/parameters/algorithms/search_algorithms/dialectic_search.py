from __future__ import annotations

from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    Decomposer,
    TabuSearchBaseParams,
)
from luna_quantum.solve.parameters.backends import DWave
from luna_quantum.solve.parameters.constants import DEFAULT_ATOL, DEFAULT_RTOL


class DialecticSearch(LunaAlgorithm[DWave]):
    """
    Parameters for the Dialectic Search optimization algorithm.

    Dialectic Search is an iterative metaheuristic that uses a
    thesis-antithesis-synthesis approach to explore the solution space. It starts with
    a thesis (initial solution) and generates an antithesis (complementary solution).
    Then it performs a path search between them to synthesize improved solutions, using
    tabu search for all three phases.

    Attributes
    ----------
    antithesis_tabu_params: TabuSearchParams
        Parameters for the antithesis phase of the search process. The antithesis
        deliberately explores contrasting regions of the solution space to ensure
        diversity and avoid getting trapped in local optima. This phase often uses
        different tabu parameters to promote exploration over exploitation.
        Default is a TabuSearchParams instance with default settings.
    synthesis_tabu_params: TabuSearchParams
        Parameters for the synthesis phase of the search process. The synthesis combines
        aspects of both thesis and antithesis to generate new candidate solutions,
        exploring the path between these solutions to find potentially better optima.
        This phase is critical for discovering high-quality solutions that neither
        thesis nor antithesis alone would find.
        Default is a TabuSearchParams instance with default settings.
    max_iter: int | None
        Maximum number of iterations for the solver. This limits the total number of
        dialectic cycles (thesis-antithesis-synthesis) that will be performed.
        Higher values allow for more thorough exploration but increase runtime.
        Default is 100.
    max_time: int
        Maximum time in seconds for the solver to run. Provides a hard time limit
        regardless of convergence or iteration status. Useful for time-constrained
        scenarios where some solution is needed within a specific timeframe.
        Default is 5.
    convergence: int
        Number of consecutive iterations without improvement before declaring
        convergence. Higher values ensure more stable solutions but may increase
        computation time unnecessarily if the algorithm has already found the best
        solution. Default is 3.
    target: float | None
        Target objective value that triggers termination if reached. Allows early
        stopping when a sufficiently good solution is found. Default is None, which
        means the algorithm will run until other stopping criteria are met.
    rtol: float
        Relative tolerance for convergence detection. Used when comparing objective
        values between iterations to determine if significant improvement has occurred.
        Default is DEFAULT_RTOL.
    atol: float
        Absolute tolerance for convergence detection. Used alongside rtol when comparing
        objective values to determine if the algorithm has converged. Default is
        DEFAULT_ATOL.
    max_tries: int | None
        Maximum number of synthesis attempts for each input state before moving to a new
        thesis. Controls how persistently the algorithm explores the path between
        thesis and antithesis before generating new starting points. Higher values
        allow for more thorough path exploration but may slow progress if paths are
        unproductive. Default is 100. Must be ≥1.
    decomposer: Decomposer
        Decomposer: Breaks down problems into subproblems of manageable size
        Default is a Decomposer instance with default settings.

    Notes
    -----
    The Dialectic Search algorithm operates through two distinct phases:

    1. Antithesis: Generates a complementary solution designed to explore different
       regions of the solution space
    2. Synthesis: Creates new solutions by exploring paths between thesis and antithesis

    Each phase uses tabu search with potentially different parameter settings to
    guide the exploration process. This approach is particularly effective for
    problems with complex landscapes containing many local optima.

    The algorithm uses D-Wave's backend technology to efficiently solve optimization
    problems. For more details on D-Wave solvers, see:
    https://docs.dwavesys.com/
    """

    antithesis_tabu_params: TabuSearchBaseParams = Field(
        default_factory=TabuSearchBaseParams
    )
    synthesis_tabu_params: TabuSearchBaseParams = Field(
        default_factory=TabuSearchBaseParams
    )

    decomposer: Decomposer = Field(default_factory=Decomposer)
    max_iter: int | None = 100
    max_time: int = 5
    convergence: int = 3
    target: float | None = None
    rtol: float = DEFAULT_RTOL
    atol: float = DEFAULT_ATOL
    max_tries: int | None = Field(default=100, ge=1)

    @property
    def algorithm_name(self) -> str:
        """
        Returns the name of the algorithm.

        This abstract property method is intended to be overridden by subclasses.
        It should provide the name of the algorithm being implemented.

        Returns
        -------
        str
            The name of the algorithm.
        """
        return "DS"

    @classmethod
    def get_default_backend(cls) -> DWave:
        """
        Return the default backend implementation.

        This property must be implemented by subclasses to provide
        the default backend instance to use when no specific backend
        is specified.

        Returns
        -------
            IBackend
                An instance of a class implementing the IBackend interface that serves
                as the default backend.
        """
        return DWave()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[DWave], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (DWave,)
