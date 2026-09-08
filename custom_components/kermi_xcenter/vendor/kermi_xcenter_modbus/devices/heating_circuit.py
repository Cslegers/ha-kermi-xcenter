"""The heating circuit block shared by the storage and universal modules.

Registers 150-163 carry an identical layout on the storage system modules
(device addresses 50/51) and on the heating circuit / universal module (device
address 30), so both bind this one component.
"""

from __future__ import annotations

from ..data_model import KermiComponent, boolean, enum, gauge, temperature
from ..enums import (
    EnergyMode,
    HeatingCircuitStatus,
    OperatingMode,
    OperatingType,
    SeasonSelection,
)

__all__ = ["HeatingCircuit"]


class HeatingCircuit(KermiComponent):
    """Heating circuit control. Manufacturer section "Heizkreis"."""

    register_ranges = ((150, 163),)

    status = enum(
        150,
        HeatingCircuitStatus,
        maker_key="Status Heizkreis",
        maker_category="Heizkreis",
        description="Heating circuit state",
    )
    """What the heating circuit is currently doing."""

    temperature_actual = temperature(
        151,
        maker_key="Isttemperatur Heizkreis",
        maker_category="Heizkreis",
        description="Heating circuit actual temperature",
    )
    """Measured heating circuit flow temperature."""

    setpoint = temperature(
        152,
        min_value=0,
        max_value=85,
        maker_key="Solltemperatur Heizkreis",
        maker_category="Heizkreis",
        description="Heating circuit target temperature",
    )
    """Target heating circuit flow temperature."""

    operating_mode = enum(
        153,
        OperatingMode,
        maker_key="Betriebsmodus",
        maker_category="Heizkreis",
        description="Reported heating circuit mode",
    )
    """Reported mode: off, heating or cooling."""

    operating_type = enum(
        154,
        OperatingType,
        writable=True,
        maker_key="Betriebsart",
        maker_category="Heizkreis",
        description="Selected heating circuit operating type",
    )
    """Selected operating type: automatic or forced."""

    energy_mode = enum(
        155,
        EnergyMode,
        writable=True,
        maker_key="Energiemodus",
        maker_category="Heizkreis",
        description="Comfort level of the heating circuit",
    )
    """Comfort level: off, eco, normal, comfort or custom."""

    curve_offset = gauge(
        156,
        0.1,
        unit="K",
        min_value=-5,
        max_value=5,
        writable=True,
        maker_key="Parallelverschiebung Kurve",
        maker_category="Heizkreis",
        description="Parallel shift of the heating curve",
    )
    """Parallel shift applied to the heating curve."""

    season_selection = enum(
        157,
        SeasonSelection,
        writable=True,
        maker_key="Manuelle Saisonauswahl",
        maker_category="Heizkreis",
        description="Manual season override",
    )
    """Manual season override: auto, heating, cooling or off."""

    summer_threshold = temperature(
        158,
        min_value=0,
        max_value=50,
        default=18,
        writable=True,
        maker_key="Sommerbetrieb (Heizen Aus)",
        maker_category="Heizkreis",
        description="Outdoor temperature at which heating switches off",
    )
    """Outdoor temperature above which heating stops."""

    winter_threshold = temperature(
        159,
        min_value=0,
        max_value=50,
        default=16,
        writable=True,
        maker_key="Winterbetrieb (Heizen Ein)",
        maker_category="Heizkreis",
        description="Outdoor temperature at which heating switches on",
    )
    """Outdoor temperature below which heating starts."""

    cooling_on_threshold = temperature(
        160,
        min_value=0,
        max_value=50,
        default=22,
        writable=True,
        maker_key="Kühlbetrieb Ein",
        maker_category="Heizkreis",
        description="Outdoor temperature at which cooling switches on",
    )
    """Outdoor temperature above which cooling starts."""

    cooling_off_threshold = temperature(
        161,
        min_value=0,
        max_value=50,
        default=20,
        writable=True,
        maker_key="Kühlbetrieb Aus",
        maker_category="Heizkreis",
        description="Outdoor temperature at which cooling switches off",
    )
    """Outdoor temperature below which cooling stops."""

    summer_mode = boolean(
        162,
        maker_key="Sommerbetrieb",
        maker_category="Heizkreis",
        description="Whether summer mode is active",
    )
    """True while the circuit is in summer mode."""

    cooling_mode = boolean(
        163,
        maker_key="Kühlbetrieb",
        maker_category="Heizkreis",
        description="Whether cooling mode is active",
    )
    """True while the circuit is in cooling mode."""
