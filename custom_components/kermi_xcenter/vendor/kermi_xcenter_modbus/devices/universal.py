"""Heating circuit / universal module — device address 30.

Follows ``Modbusliste - Universalmodul`` in the manufacturer's integration
guide. The heating circuit block is identical to the storage modules', so it
binds the shared :class:`~kermi_xcenter_modbus.devices.heating_circuit.HeatingCircuit`;
only the temperature input terminals and the single run time counter differ.
"""

from __future__ import annotations

from ..data_model import KermiComponent, gauge, temperature
from .heating_circuit import HeatingCircuit

__all__ = ["UNIT_ID", "UniversalHours", "UniversalModule", "UniversalSensors"]

#: Default device address of the heating circuit / universal module.
UNIT_ID = 30


class UniversalSensors(KermiComponent):
    """Module temperature inputs. Manufacturer section "Status".

    The terminal numbering differs from the storage modules': X9-X12 here
    against X13-X10 there.
    """

    register_ranges = ((250, 253),)

    t1 = temperature(
        250,
        maker_key="T1 (X9) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T1 on terminal X9",
    )
    """Temperature input T1 (terminal X9)."""

    t2 = temperature(
        251,
        maker_key="T2 (X10) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T2 on terminal X10",
    )
    """Temperature input T2 (terminal X10)."""

    t3 = temperature(
        252,
        maker_key="T3 (X11) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T3 on terminal X11",
    )
    """Temperature input T3 (terminal X11)."""

    t4 = temperature(
        253,
        maker_key="T4 (X12) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T4 on terminal X12",
    )
    """Temperature input T4 (terminal X12)."""


class UniversalHours(KermiComponent):
    """Run time counter. Manufacturer section "Betriebsstunden"."""

    register_ranges = ((300, 300),)

    circuit_pump = gauge(
        300,
        0.1,
        unit="h",
        signed=False,  # the counters run past 32767
        min_value=0,
        max_value=6553.5,
        range_documented=False,
        maker_key="Heizkreispumpe Laufzeit",
        maker_category="Betriebsstunden",
        description="Heating circuit pump run time",
    )
    """Total heating circuit pump run time."""


class UniversalModule:
    """Every sub-system of the heating circuit / universal module."""

    def __init__(self, unit: object, /) -> None:
        """Bind each sub-system to *unit*."""
        self.heating_circuit = HeatingCircuit(unit)  # type: ignore[arg-type]
        self.sensors = UniversalSensors(unit)  # type: ignore[arg-type]
        self.operating_hours = UniversalHours(unit)  # type: ignore[arg-type]

    #: Sub-systems refreshed on every poll.
    READINGS = ("heating_circuit", "sensors")
    #: Sub-systems that change slowly and can be polled less often.
    SLOW = ("operating_hours",)
