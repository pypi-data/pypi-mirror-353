"""Define a class to hold optimisation objective with its ideal value."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from lightwin.beam_calculation.simulation_output.simulation_output import (
    SimulationOutput,
)


@dataclass
class Objective(ABC):
    """Hold an objective and methods to evaluate it.

    Parameters
    ----------
    name : str
        A short string to describe the objective and access to it.
    weight : float
        A scaling constant to set the weight of current objective.
    descriptor : str | None, optional
        A longer string to explain the objective. The default is None.
    ideal_value : float | tuple[float], optional
        The ideal value or range of values that we should tend to.

    """

    name: str
    weight: float
    descriptor: str | None = None
    ideal_value: tuple[float, float] | float | None = None

    def __post_init__(self) -> None:
        """Avoid line jumps in the descriptor."""
        if self.descriptor is None:
            self.descriptor = ""
            return
        self.descriptor = " ".join(self.descriptor.split())

    @abstractmethod
    def __str__(self) -> str:
        """Output info on what is this objective about."""

    @abstractmethod
    def base_str(self) -> str:
        """Tell nature and position of objective."""

    @staticmethod
    def str_header() -> str:
        """Give a header to explain what :meth:`__str__` returns."""
        header = f"{'What, where, etc': ^40} | {'wgt.':>5} | "
        header += f"{'ideal value': ^21}"
        return header

    @abstractmethod
    def evaluate(self, simulation_output: SimulationOutput | float) -> float:
        """Compute residue of this objective.

        Parameters
        ----------
        simulation_output : SimulationOutput | float
            Object containing simulation results of the broken linac.

        Returns
        -------
        residue : float
            Difference between current evaluation and ideal_value value for
            ``self.name``, scaled by ``self.weight``.

        """
