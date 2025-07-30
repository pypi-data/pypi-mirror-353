"""Define an objective that is a quantity must be within some bounds.

.. todo::
    Implement loss functions.

"""

import logging

from lightwin.beam_calculation.simulation_output.simulation_output import (
    SimulationOutput,
)
from lightwin.core.elements.element import Element
from lightwin.optimisation.objective.objective import Objective


class QuantityIsBetween(Objective):
    """Quantity must be within some bounds."""

    def __init__(
        self,
        name: str,
        weight: float,
        get_key: str,
        get_kwargs: dict[str, Element | str | bool],
        limits: tuple[float, float],
        descriptor: str | None = None,
        loss_function: str | None = None,
    ) -> None:
        """
        Set complementary :meth:`.SimulationOutput.get` flags, reference value.

        Parameters
        ----------
        get_key : str
            Name of the quantity to get, which must be an attribute of
            :class:`.SimulationOutput`.
        get_kwargs : dict[str, Element | str | bool]
            Keyword arguments for the :meth:`.SimulationOutput.get` method. We
            do not check its validity, but in general you will want to define
            the keys ``elt`` and ``pos``. If objective concerns a phase, you
            may want to precise the ``to_deg`` key. You also should explicit
            the ``to_numpy`` key.
        limits : tuple[float, float]
            Lower and upper bound for the value.
        loss_function : str | None, optional
            Indicates how the residues are handled whe the quantity is outside
            the limits. The default is None.

        """
        self.get_key = get_key
        self.get_kwargs = get_kwargs
        super().__init__(
            name, weight, descriptor=descriptor, ideal_value=limits
        )
        if loss_function is not None:
            logging.warning("Loss functions not implemented.")

    def base_str(self) -> str:
        """Tell nature and position of objective."""
        message = f"{self.get_key:>23}"

        elt = str(self.get_kwargs.get("elt", "NA"))
        message += f" @elt {elt:>5}"

        pos = str(self.get_kwargs.get("pos", "NA"))
        message += f" ({pos:>3}) | {self.weight:>5} | "
        return message

    def __str__(self) -> str:
        """Give objective information value."""
        message = self.base_str()
        message += f"{self.ideal_value[0]:+.2e} ~ {self.ideal_value[1]:+.2e}"  # type: ignore
        return message

    def _value_getter(self, simulation_output: SimulationOutput) -> float:
        """Get desired value using :meth:`.SimulationOutput.get` method."""
        return simulation_output.get(self.get_key, **self.get_kwargs)

    def evaluate(self, simulation_output: SimulationOutput) -> float:
        value = self._value_getter(simulation_output)
        return self._compute_residues(value)

    def _compute_residues(self, value: float) -> float:
        """Compute the residues."""
        if value < self.ideal_value[0]:
            return self.weight * (value - self.ideal_value[0]) ** 2
        if value > self.ideal_value[1]:
            return self.weight * (value - self.ideal_value[1]) ** 2
        return 0.0
