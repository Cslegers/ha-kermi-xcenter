"""Discrete value mappings published by the x-center controller.

Every mapping here is taken verbatim from the manufacturer's integration guide
(``Kurzanleitung - Einbindung in externe Systeme``, D00028482/05-2024). The
German source labels are kept in comments so a reader can check a member
against the printed table without translating back.
"""

from __future__ import annotations

from enum import IntEnum

__all__ = [
    "EnergyMode",
    "ExternalHeatGeneratorMode",
    "ExternalHeatGeneratorStatus",
    "HeatPumpStatus",
    "HeatingCircuitStatus",
    "OperatingMode",
    "OperatingType",
    "SeasonSelection",
]


class HeatPumpStatus(IntEnum):
    """Heat pump run state (unit 40, register 200)."""

    STANDBY = 0  # Standby
    ALARM = 1  # Alarm
    HOT_WATER = 2  # TWE (Trinkwassererwärmung)
    COOLING = 3  # Kühlen
    HEATING = 4  # Heizen
    DEFROST = 5  # Abtauung
    PREPARING = 6  # Vorbereitung
    BLOCKED = 7  # Blockiert
    UTILITY_LOCK = 8  # EVU Sperre
    UNAVAILABLE = 9  # nicht verfügbar


class HeatingCircuitStatus(IntEnum):
    """Heating circuit state (storage/universal modules, register 150)."""

    OFF = 0  # Aus
    HEATING = 1  # Heizen
    COOLING = 2  # Kühlen
    DEW_POINT = 3  # Taupunkt
    PUMP_SERVICE_RUN = 4  # Pumpenwartungslauf
    FROST_PROTECTION = 5  # Frostschutz
    MANUAL = 6  # Handbetrieb
    TEST = 7  # Testmodus
    INITIALIZING = 8  # Initialisierung
    SAFETY_STATE = 9  # Sicherheitszustand


class OperatingMode(IntEnum):
    """Reported heating circuit mode (register 153, read-only)."""

    OFF = 0  # Aus
    HEATING = 1  # Heizen
    COOLING = 2  # Kühlen


class OperatingType(IntEnum):
    """Selected heating circuit operating type (register 154, writable).

    The manufacturer's table labels value 1 as ``Heizen`` for the storage
    system module and ``Aus`` for the universal module. The member name follows
    the storage module; on a universal module read it as "not automatic".
    """

    AUTO = 0  # Auto
    HEATING = 1  # Heizen (universal module: Aus)


class EnergyMode(IntEnum):
    """Energy/comfort level of a heating circuit (register 155, writable)."""

    OFF = 0  # Off
    ECO = 1  # Eco
    NORMAL = 2  # Normal
    COMFORT = 3  # Comfort
    CUSTOM = 4  # Benutzerdefiniert


class SeasonSelection(IntEnum):
    """Manual season override (register 157, writable)."""

    AUTO = 0  # Auto
    HEATING = 1  # Heizen
    COOLING = 2  # Kühlen
    OFF = 3  # Aus


class ExternalHeatGeneratorMode(IntEnum):
    """External heat generator operating type (registers 201/203, writable)."""

    AUTO = 0  # Auto
    HEAT_PUMP_ONLY = 1  # Nur WP
    BOTH = 2  # Beide
    SECONDARY_ONLY = 3  # Sekundärer WEZ


class ExternalHeatGeneratorStatus(IntEnum):
    """External heat generator state (registers 200/202, read-only).

    The manufacturer groups these by hundreds: 0 no demand, 1xx demand, 2xx
    standby with a reason, 3xx demand with a reason.
    """

    NO_DEMAND = 0  # keine Anforderung
    DEMAND = 100  # Anforderung

    STANDBY_AUTO_PARALLEL = 200  # Bereitschaft Auto Parallel
    STANDBY_AUTO_ALTERNATIVE = 201  # Bereitschaft Auto Alternativ
    STANDBY_FAULT = 204  # Bereitschaft wg. Störung
    STANDBY_MANUAL_PARALLEL = 205  # Bereitschaft Handbetrieb Parallel
    STANDBY_DUE_TO_MANUAL_PARALLEL = 206  # Bereitschaft wg. Handbetrieb Parallel
    STANDBY_UTILITY_LOCK = 207  # Bereitschaft EVU Sperre

    DEMAND_AUTO_PARALLEL = 300  # Anforderung Auto Parallel
    DEMAND_AUTO_ALTERNATIVE = 301  # Anforderung Auto Alternativ
    DEMAND_FAULT = 304  # Anforderung wg. Störung
    DEMAND_MANUAL_PARALLEL = 305  # Anforderung Handbetrieb Parallel
    DEMAND_DUE_TO_MANUAL_PARALLEL = 306  # Anforderung wg. Handbetrieb Parallel
    DEMAND_UTILITY_LOCK = 307  # Anforderung EVU Sperre
