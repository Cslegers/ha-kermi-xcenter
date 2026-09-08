"""Storage system modules — device addresses 50 (heating) and 51 (hot water).

Both addresses serve the same layout (``Modbusliste - Speichersystemmodule`` in
the manufacturer's integration guide); which half carries meaningful values
depends on what the module is fitted for. On real hardware the heating module
populates the heating store and heating circuit blocks while leaving hot water
at zero, and the hot water module does the reverse.
"""

from __future__ import annotations

from ..data_model import KermiComponent, boolean, enum, gauge, temperature
from ..enums import ExternalHeatGeneratorMode, ExternalHeatGeneratorStatus
from .heating_circuit import HeatingCircuit

__all__ = [
    "ExternalHeatGenerator",
    "HeatingCircuit",
    "HotWater",
    "Sensors",
    "StorageHours",
    "StorageModule",
    "StorageTemperatures",
    "UNIT_ID_HEATING",
    "UNIT_ID_HOT_WATER",
]

#: Default device address of the heating storage module.
UNIT_ID_HEATING = 50
#: Default device address of the hot water storage module.
UNIT_ID_HOT_WATER = 51


class StorageTemperatures(KermiComponent):
    """Heating and cooling store temperatures.

    Manufacturer sections "Heizen" and "Kühlen".
    """

    register_ranges = ((1, 2), (50, 51))

    heating_temperature = temperature(
        1,
        maker_key="Isttemperatur Heizspeicher",
        maker_category="Heizen",
        description="Heating store actual temperature",
    )
    """Measured temperature of the heating store."""

    heating_setpoint = temperature(
        2,
        maker_key="Solltemperatur Heizspeicher",
        maker_category="Heizen",
        description="Heating store target temperature",
    )
    """Target temperature of the heating store."""

    cooling_temperature = temperature(
        50,
        maker_key="Isttemperatur Kühlspeicher",
        maker_category="Kühlen",
        description="Cooling store actual temperature",
    )
    """Measured temperature of the cooling store."""

    cooling_setpoint = temperature(
        51,
        maker_key="Solltemperatur Kühlspeicher",
        maker_category="Kühlen",
        description="Cooling store target temperature",
    )
    """Target temperature of the cooling store."""


class HotWater(KermiComponent):
    """Domestic hot water. Manufacturer section "Trinkwassererwärmung"."""

    register_ranges = ((100, 104),)

    temperature_actual = temperature(
        100,
        maker_key="Isttemperatur TWE",
        maker_category="Trinkwassererwärmung",
        description="Hot water actual temperature",
    )
    """Measured hot water temperature."""

    setpoint = temperature(
        101,
        maker_key="Solltemperatur TWE",
        maker_category="Trinkwassererwärmung",
        description="Hot water target temperature",
    )
    """Currently effective hot water target temperature."""

    constant_setpoint = temperature(
        102,
        min_value=0,
        max_value=85,
        default=48,
        writable=True,
        maker_key="Konstanter Sollwert TWE",
        maker_category="Trinkwassererwärmung",
        description="Constant hot water setpoint",
    )
    """Constant hot water setpoint."""

    boost_active = boolean(
        103,
        writable=True,
        false_key="off",
        true_key="on",
        maker_key="Einmalladung TWE",
        maker_category="Trinkwassererwärmung",
        description="One-shot hot water charge",
    )
    """One-shot ("boost") hot water charge."""

    boost_setpoint = temperature(
        104,
        min_value=30,
        max_value=60,
        default=50,
        writable=True,
        maker_key="Sollwert Einmalladung TWE",
        maker_category="Trinkwassererwärmung",
        description="Target temperature for a one-shot hot water charge",
    )
    """Target temperature used for a one-shot charge."""


class ExternalHeatGenerator(KermiComponent):
    """Auxiliary heat source. Manufacturer section "Externer Wärmeerzeuger"."""

    register_ranges = ((200, 203),)

    heating_status = enum(
        200,
        ExternalHeatGeneratorStatus,
        maker_key="Status ext. WEZ Heizen",
        maker_category="Externer Wärmeerzeuger",
        description="External heat generator state for heating",
    )
    """State of the external heat generator for heating."""

    heating_mode = enum(
        201,
        ExternalHeatGeneratorMode,
        writable=True,
        maker_key="Betriebsart ext. WEZ Hz",
        maker_category="Externer Wärmeerzeuger",
        description="External heat generator operating type for heating",
    )
    """How the external heat generator may be used for heating."""

    hot_water_status = enum(
        202,
        ExternalHeatGeneratorStatus,
        maker_key="Status ext. WEZ TWE",
        maker_category="Externer Wärmeerzeuger",
        description="External heat generator state for hot water",
    )
    """State of the external heat generator for hot water."""

    hot_water_mode = enum(
        203,
        ExternalHeatGeneratorMode,
        writable=True,
        maker_key="Betriebsart ext. TWE",
        maker_category="Externer Wärmeerzeuger",
        description="External heat generator operating type for hot water",
    )
    """How the external heat generator may be used for hot water."""


class Sensors(KermiComponent):
    """Module temperature inputs. Manufacturer section "Status".

    Inputs that are not fitted read as the unfitted-sensor sentinel and decode
    to ``None``.
    """

    register_ranges = ((250, 255),)

    t1 = temperature(
        250,
        maker_key="T1 (X13) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T1 on terminal X13",
    )
    """Temperature input T1 (terminal X13)."""

    t2 = temperature(
        251,
        maker_key="T2 (X12) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T2 on terminal X12",
    )
    """Temperature input T2 (terminal X12)."""

    t3 = temperature(
        252,
        maker_key="T3 (X11) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T3 on terminal X11",
    )
    """Temperature input T3 (terminal X11)."""

    t4 = temperature(
        253,
        maker_key="T4 (X10) Temperaturfühler",
        maker_category="Status",
        description="Temperature input T4 on terminal X10",
    )
    """Temperature input T4 (terminal X10)."""

    outdoor_temperature = temperature(
        254,
        maker_key="Außentemperatur",
        maker_category="Status",
        description="Outdoor temperature",
    )
    """Outdoor temperature as seen by this module."""

    outdoor_temperature_averaged = temperature(
        255,
        maker_key="Gemittelte Außentemperatur",
        maker_category="Status",
        description="Averaged outdoor temperature",
    )
    """Averaged outdoor temperature used by the heating curve."""


class StorageHours(KermiComponent):
    """Run time counters. Manufacturer section "Betriebsstunden"."""

    register_ranges = ((300, 301),)

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

    external_heat_generator = gauge(
        301,
        0.1,
        unit="h",
        signed=False,  # the counters run past 32767
        min_value=0,
        max_value=6553.5,
        range_documented=False,
        maker_key="Ext. WEZ Laufzeit",
        maker_category="Betriebsstunden",
        description="External heat generator run time",
    )
    """Total external heat generator run time."""


class StorageModule:
    """Every sub-system of one storage system module."""

    def __init__(self, unit: object, /) -> None:
        """Bind each sub-system to *unit*."""
        self.storage = StorageTemperatures(unit)  # type: ignore[arg-type]
        self.hot_water = HotWater(unit)  # type: ignore[arg-type]
        self.heating_circuit = HeatingCircuit(unit)  # type: ignore[arg-type]
        self.external_heat_generator = ExternalHeatGenerator(unit)  # type: ignore[arg-type]
        self.sensors = Sensors(unit)  # type: ignore[arg-type]
        self.operating_hours = StorageHours(unit)  # type: ignore[arg-type]

    #: Sub-systems refreshed on every poll.
    READINGS = (
        "storage",
        "hot_water",
        "heating_circuit",
        "external_heat_generator",
        "sensors",
    )
    #: Sub-systems that change slowly and can be polled less often.
    SLOW = ("operating_hours",)
