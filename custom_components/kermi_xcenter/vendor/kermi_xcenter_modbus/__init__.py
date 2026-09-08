"""Read and control a Kermi x-center heat pump controller over Modbus.

The controller spreads across several Modbus device addresses on one link, so
the entry point takes a mapping of device address to ``ModbusUnit``:

    import asyncio
    from modbus_connection import ModbusTcpParams
    from modbus_connection.tmodbus import ModbusConnection
    from kermi_xcenter_modbus import DEFAULT_UNIT_IDS, KermiXCenter

    async def main() -> None:
        connection = ModbusConnection(ModbusTcpParams(host="192.168.1.50"))
        try:
            units = {uid: connection.for_unit(uid) for uid in DEFAULT_UNIT_IDS.values()}
            xcenter = KermiXCenter(units)
            await xcenter.async_update()
            print("Outdoor:", xcenter.heat_pump.energy_source.outdoor_temperature)
            print("COP:", xcenter.heat_pump.power.cop)
        finally:
            await connection.close()

    asyncio.run(main())

The caller owns the connection and closes it; this library only reads and
writes registers on the units it is handed.
"""

from __future__ import annotations

from .data_model import NAN_SENSOR, KermiComponent
from .devices import (
    HeatingCircuit,
    HeatPump,
    PvFeed,
    StorageModule,
    UniversalModule,
)
from .enums import (
    EnergyMode,
    ExternalHeatGeneratorMode,
    ExternalHeatGeneratorStatus,
    HeatingCircuitStatus,
    HeatPumpStatus,
    OperatingMode,
    OperatingType,
    SeasonSelection,
)
from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    OptionMetadata,
    datapoint_metadata,
)
from .probe import async_module_present
from .xcenter import DEFAULT_UNIT_IDS, KermiXCenter, UpdateReport

__all__ = [
    "DEFAULT_UNIT_IDS",
    "NAN_SENSOR",
    "BooleanMetadata",
    "DatapointMetadata",
    "EnergyMode",
    "EnumMetadata",
    "ExternalHeatGeneratorMode",
    "ExternalHeatGeneratorStatus",
    "HeatPump",
    "HeatPumpStatus",
    "HeatingCircuit",
    "HeatingCircuitStatus",
    "KermiComponent",
    "KermiXCenter",
    "NumberMetadata",
    "OperatingMode",
    "OperatingType",
    "OptionMetadata",
    "PvFeed",
    "SeasonSelection",
    "StorageModule",
    "UniversalModule",
    "UpdateReport",
    "async_module_present",
    "datapoint_metadata",
]
