"""The heat pump itself — device address 40.

Section headings and register numbers follow ``Modbusliste - Wärmepumpe`` in the
manufacturer's integration guide.
"""

from __future__ import annotations

from ..data_model import KermiComponent, boolean, enum, gauge, integer, temperature
from ..enums import HeatPumpStatus

__all__ = [
    "ChargingCircuit",
    "EnergySource",
    "HeatPump",
    "OperatingHours",
    "PowerEfficiency",
    "PvModulation",
    "Status",
]

#: Default device address of the heat pump.
UNIT_ID = 40


class EnergySource(KermiComponent):
    """Brine/air side temperatures. Manufacturer section "Energiequelle"."""

    register_ranges = ((1, 3),)

    exit_temperature = temperature(
        1,
        maker_key="B14 - Energiequelle Austrittstemperatur",
        maker_category="Energiequelle",
        description="Energy source outlet temperature",
    )
    """Temperature leaving the energy source (B14)."""

    inlet_temperature = temperature(
        2,
        maker_key="B15 - Energiequelle Eintrittstemperatur",
        maker_category="Energiequelle",
        description="Energy source inlet temperature",
    )
    """Temperature entering the energy source (B15)."""

    outdoor_temperature = temperature(
        3,
        maker_key="BOT - Außentemperaturfühler",
        maker_category="Energiequelle",
        description="Outdoor temperature sensor",
    )
    """Outdoor air temperature (BOT)."""


class ChargingCircuit(KermiComponent):
    """Heat pump flow side. Manufacturer section "Ladekreis"."""

    register_ranges = ((50, 52),)

    flow_temperature = temperature(
        50,
        maker_key="B16 - Vorlauftemperatur WP",
        maker_category="Ladekreis",
        description="Heat pump flow temperature",
    )
    """Flow (supply) temperature of the heat pump (B16)."""

    return_temperature = temperature(
        51,
        maker_key="B17 - Rücklauftemperatur WP",
        maker_category="Ladekreis",
        description="Heat pump return temperature",
    )
    """Return temperature of the heat pump (B17)."""

    flow_rate = gauge(
        52,
        0.1,
        unit="l/min",
        maker_key="P13 - Durchfluss WP",
        maker_category="Ladekreis",
        description="Heat pump volumetric flow",
    )
    """Volumetric flow through the heat pump (P13)."""


class PowerEfficiency(KermiComponent):
    """Coefficients of performance and thermal/electrical power.

    Manufacturer section "Leistung und Effizienz".
    """

    register_ranges = ((100, 111),)

    cop = gauge(
        100,
        0.1,
        maker_key="Aktueller COP",
        maker_category="Leistung und Effizienz",
        description="Current coefficient of performance, all modes",
    )
    """Current overall coefficient of performance."""

    cop_heating = gauge(
        101,
        0.1,
        maker_key="Aktueller COP Heizen",
        maker_category="Leistung und Effizienz",
        description="Current coefficient of performance while heating",
    )
    """Current coefficient of performance in heating mode."""

    cop_hot_water = gauge(
        102,
        0.1,
        maker_key="Aktueller COP TWE",
        maker_category="Leistung und Effizienz",
        description="Current coefficient of performance while heating hot water",
    )
    """Current coefficient of performance in hot water mode."""

    cop_cooling = gauge(
        103,
        0.1,
        maker_key="Aktueller COP Kühlen",
        maker_category="Leistung und Effizienz",
        description="Current coefficient of performance while cooling",
    )
    """Current coefficient of performance in cooling mode."""

    thermal_power = gauge(
        104,
        0.1,
        unit="kW",
        maker_key="Aktuelle Leistung",
        maker_category="Leistung und Effizienz",
        description="Current thermal output, all modes",
    )
    """Current thermal output."""

    thermal_power_heating = gauge(
        105,
        0.1,
        unit="kW",
        maker_key="Aktuelle Leistung Heizen",
        maker_category="Leistung und Effizienz",
        description="Current thermal output while heating",
    )
    """Current thermal output in heating mode."""

    thermal_power_hot_water = gauge(
        106,
        0.1,
        unit="kW",
        maker_key="Aktuelle Leistung TWE",
        maker_category="Leistung und Effizienz",
        description="Current thermal output while heating hot water",
    )
    """Current thermal output in hot water mode."""

    thermal_power_cooling = gauge(
        107,
        0.1,
        unit="kW",
        maker_key="Aktuelle Leistung Kühlen",
        maker_category="Leistung und Effizienz",
        description="Current thermal output while cooling",
    )
    """Current thermal output in cooling mode."""

    electrical_power = gauge(
        108,
        0.1,
        unit="kW",
        maker_key="Akt. elektr. Leistung",
        maker_category="Leistung und Effizienz",
        description="Current electrical input, all modes",
    )
    """Current electrical power draw."""

    electrical_power_heating = gauge(
        109,
        0.1,
        unit="kW",
        maker_key="Akt. elektr. Leistung Heizen",
        maker_category="Leistung und Effizienz",
        description="Current electrical input while heating",
    )
    """Current electrical power draw in heating mode."""

    electrical_power_hot_water = gauge(
        110,
        0.1,
        unit="kW",
        maker_key="Akt. elektr. Leistung TWE",
        maker_category="Leistung und Effizienz",
        description="Current electrical input while heating hot water",
    )
    """Current electrical power draw in hot water mode."""

    electrical_power_cooling = gauge(
        111,
        0.1,
        unit="kW",
        maker_key="Akt. elektr. Leistung Kühlen",
        maker_category="Leistung und Effizienz",
        description="Current electrical input while cooling",
    )
    """Current electrical power draw in cooling mode."""


class OperatingHours(KermiComponent):
    """Lifetime run time counters. Manufacturer section "Betriebsstunden".

    Scaled by 1/10 and read unsigned, like every other quantity here. Both
    manufacturer sources say otherwise — the Loxone template maps these 1:1 and
    the guide gives the sibling counters a range of 0-65535 h — but the
    controller's own web interface reports register 152 reading 49898 as
    4989.8 h, matching to the decimal. The 0-65535 in the guide is the raw
    register range, not the range of the value. See
    ``docs/register-verification.md``.
    """

    register_ranges = ((150, 152),)

    fan = gauge(
        150,
        0.1,
        unit="h",
        signed=False,  # the counters run past 32767
        min_value=0,
        max_value=6553.5,
        range_documented=False,
        maker_key="Betriebsstunden - Lüfter",
        maker_category="Betriebsstunden",
        description="Fan run time",
    )
    """Total fan run time."""

    storage_loading_pump = gauge(
        151,
        0.1,
        unit="h",
        signed=False,  # the counters run past 32767
        min_value=0,
        max_value=6553.5,
        range_documented=False,
        maker_key="Betriebsstunden - Speicherladepumpe",
        maker_category="Betriebsstunden",
        description="Storage loading pump run time",
    )
    """Total storage loading pump run time."""

    compressor = gauge(
        152,
        0.1,
        unit="h",
        signed=False,  # the counters run past 32767
        min_value=0,
        max_value=6553.5,
        range_documented=False,
        maker_key="Betriebsstunden - Verdichter",
        maker_category="Betriebsstunden",
        description="Compressor run time",
    )
    """Total compressor run time."""


class Status(KermiComponent):
    """Run state and the global alarm flag.

    Manufacturer sections "Status" and "Statusmeldungen". The two registers sit
    50 apart, so the planner issues them as two reads.
    """

    register_ranges = ((200, 200), (250, 250))

    state = enum(
        200,
        HeatPumpStatus,
        maker_key="Status Wärmepumpe",
        maker_category="Status",
        description="Heat pump run state",
    )
    """What the heat pump is currently doing."""

    alarm = boolean(
        250,
        maker_key="Globaler Alarm",
        maker_category="Statusmeldungen",
        description="Global alarm flag",
    )
    """True while any alarm is active."""


class PvModulation(KermiComponent):
    """Photovoltaic modulation as reported by the heat pump.

    Manufacturer section "PV Modulation Wärmepumpe". Registers 301-303 are
    documented read/write. Note that on an installation where Kermi has enabled
    the separate feed-in endpoint, surplus power is written *there* rather than
    to register 301 — see :mod:`kermi_xcenter_modbus.devices.pv_feed`.
    """

    register_ranges = ((300, 303),)

    active = boolean(
        300,
        maker_key="Status PV Modulation",
        maker_category="PV Modulation Wärmepumpe",
        description="Whether PV modulation is currently active",
    )
    """True while the heat pump is modulating on PV surplus."""

    # The guide gives no range for 301-303. The bounds below come from the
    # register width and, for the setpoints, from the documented 0-85 °C range
    # of the comparable hot water setpoint. They are marked as not published so
    # a consumer can tell them from the manufacturer's own limits.
    #
    # Register 301 is whole watts, not tenths: it is the same quantity as the
    # feed-in register, which is known to be whole watts. The setpoints below
    # are tenths of a degree, confirmed against hardware. Temperatures scale,
    # watts do not.
    power = integer(
        301,
        unit="W",
        signed=False,
        min_value=0,
        max_value=65535,
        default=0,
        writable=True,
        range_documented=False,
        maker_key="Aktuelle Leistung",
        maker_category="PV Modulation Wärmepumpe",
        description="PV power currently applied to modulation",
    )
    """PV power the heat pump is modulating against."""

    heating_setpoint = gauge(
        302,
        0.1,
        unit="°C",
        min_value=0,
        max_value=85,
        default=50,
        writable=True,
        range_documented=False,
        maker_key="Solltemperatur Hz PV Modulation",
        maker_category="PV Modulation Wärmepumpe",
        description="Heating target temperature while PV modulating",
    )
    """Heating target temperature used while PV modulation is active."""

    hot_water_setpoint = gauge(
        303,
        0.1,
        unit="°C",
        min_value=0,
        max_value=85,
        default=50,
        writable=True,
        range_documented=False,
        maker_key="Solltemperatur TWE PV Modulation",
        maker_category="PV Modulation Wärmepumpe",
        description="Hot water target temperature while PV modulating",
    )
    """Hot water target temperature used while PV modulation is active."""


class HeatPump:
    """Every sub-system of the heat pump at one device address."""

    def __init__(self, unit: object, /) -> None:
        """Bind each sub-system to *unit*."""
        self.energy_source = EnergySource(unit)  # type: ignore[arg-type]
        self.charging_circuit = ChargingCircuit(unit)  # type: ignore[arg-type]
        self.power = PowerEfficiency(unit)  # type: ignore[arg-type]
        self.operating_hours = OperatingHours(unit)  # type: ignore[arg-type]
        self.status = Status(unit)  # type: ignore[arg-type]
        self.pv_modulation = PvModulation(unit)  # type: ignore[arg-type]

    #: Sub-systems refreshed on every poll.
    READINGS = (
        "energy_source",
        "charging_circuit",
        "power",
        "status",
        "pv_modulation",
    )
    #: Sub-systems that change slowly and can be polled less often.
    SLOW = ("operating_hours",)
