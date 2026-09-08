"""The top-level object a consumer works with."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from modbus_connection import ModbusConnectionError, ModbusError, ModbusTimeoutError

from .devices.heat_pump import UNIT_ID as HEAT_PUMP_UNIT_ID, HeatPump
from .devices.pv_feed import UNIT_ID as PV_FEED_UNIT_ID, PvFeed
from .devices.storage import UNIT_ID_HEATING, UNIT_ID_HOT_WATER, StorageModule
from .devices.universal import UNIT_ID as UNIVERSAL_UNIT_ID, UniversalModule
from .probe import async_module_present

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

__all__ = ["DEFAULT_UNIT_IDS", "KermiXCenter", "UpdateReport"]

#: The device addresses the manufacturer ships, keyed by the attribute each
#: one becomes on :class:`KermiXCenter`.
DEFAULT_UNIT_IDS: Mapping[str, int] = {
    "pv_feed": PV_FEED_UNIT_ID,
    "universal_module": UNIVERSAL_UNIT_ID,
    "heat_pump": HEAT_PUMP_UNIT_ID,
    "storage_heating": UNIT_ID_HEATING,
    "storage_hot_water": UNIT_ID_HOT_WATER,
}

#: One register known to exist on each module, used to decide whether it is
#: fitted. For the feed-in module this is its only register.
_PROBE_REGISTER: Mapping[str, int] = {
    "pv_feed": 1,
    "universal_module": 150,
    "heat_pump": 3,
    "storage_heating": 100,
    "storage_hot_water": 100,
}


@dataclass
class UpdateReport:
    """What one poll managed to refresh."""

    updated: list[str] = field(default_factory=list)
    failed: dict[str, ModbusError] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """Return whether every sub-system refreshed."""
        return not self.failed


class KermiXCenter:
    """An x-center installation reached over one Modbus connection.

    Unlike a single-address device, an x-center spreads across several Modbus
    device addresses that share one link. So this takes a **mapping of device
    address to unit** rather than a single unit; each module still binds
    exactly one unit, keeping every component backend-neutral.

        units = {uid: connection.for_unit(uid) for uid in DEFAULT_UNIT_IDS.values()}
        xcenter = KermiXCenter(units)
        await xcenter.async_update()

    Which modules an installation actually has is settled on the first update
    by probing each one; absent modules stay ``None``. The photovoltaic feed-in
    module is only present where the manufacturer has enabled it.
    """

    def __init__(
        self,
        units: Mapping[int, ModbusUnit],
        *,
        unit_ids: Mapping[str, int] | None = None,
    ) -> None:
        """Bind the modules whose device address appears in *units*.

        *unit_ids* overrides the shipped device addresses where an installer
        has changed them.
        """
        self._units = dict(units)
        self._unit_ids = dict(unit_ids or DEFAULT_UNIT_IDS)

        self.heat_pump: HeatPump | None = None
        self.storage_heating: StorageModule | None = None
        self.storage_hot_water: StorageModule | None = None
        self.universal_module: UniversalModule | None = None
        self.pv_feed: PvFeed | None = None

        self._modules: tuple[str, ...] | None = None

    # -- setup ---------------------------------------------------------------

    def _unit(self, name: str) -> ModbusUnit | None:
        """Return the unit for module *name*, if its address was supplied."""
        return self._units.get(self._unit_ids.get(name, -1))

    async def _async_setup(self) -> None:
        """Settle which modules this installation has.

        Runs on the first update, and again on the next one if the controller
        was unreachable, so a device that was powered down is picked up later.
        """
        builders: dict[str, Any] = {
            "heat_pump": HeatPump,
            "storage_heating": StorageModule,
            "storage_hot_water": StorageModule,
            "universal_module": UniversalModule,
            "pv_feed": PvFeed,
        }
        present: list[str] = []
        for name, builder in builders.items():
            unit = self._unit(name)
            if unit is None:
                continue
            if not await async_module_present(unit, _PROBE_REGISTER[name]):
                continue
            setattr(self, name, builder(unit))
            present.append(name)
        self._modules = tuple(present)

    async def async_setup(self) -> tuple[str, ...]:
        """Probe the installation and return the modules that answered."""
        await self._async_setup()
        assert self._modules is not None
        return self._modules

    @property
    def modules(self) -> tuple[str, ...]:
        """Modules found on the last setup; empty before the first update."""
        return self._modules or ()

    # -- polling -------------------------------------------------------------

    def _components(self, module: str, slow: bool) -> list[tuple[str, Any]]:
        """Return the (label, component) pairs of *module* to refresh."""
        owner = getattr(self, module)
        if owner is None:
            return []
        if isinstance(owner, PvFeed):
            # A single component rather than a container of them.
            return [] if slow else [(module, owner)]
        names = owner.SLOW if slow else owner.READINGS
        return [(f"{module}.{name}", getattr(owner, name)) for name in names]

    async def _async_poll(self, targets: list[tuple[str, Any]]) -> UpdateReport:
        """Read each component on its own, recording what happened."""
        report = UpdateReport()
        for label, component in targets:
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:
                raise  # the link is down; the rest would only wait for timeouts
            except ModbusTimeoutError as err:
                if not report.updated and not report.failed:
                    raise  # nothing has answered yet: assume the rest time out too
                report.failed[label] = err
            except ModbusError as err:
                report.failed[label] = err
            else:
                report.updated.append(label)
                component.notify()
        return report

    async def _async_targets(self, *, slow: bool) -> list[tuple[str, Any]]:
        if self._modules is None:
            await self._async_setup()
        assert self._modules is not None
        targets: list[tuple[str, Any]] = []
        for module in self._modules:
            targets.extend(self._components(module, slow))
        return targets

    async def async_update(self) -> UpdateReport:
        """Refresh everything the installation reports."""
        fast = await self._async_targets(slow=False)
        slow = await self._async_targets(slow=True)
        report = await self._async_poll(fast + slow)
        return report

    async def async_update_readings(self) -> UpdateReport:
        """Refresh only what changes between polls."""
        return await self._async_poll(await self._async_targets(slow=False))

    async def async_update_counters(self) -> UpdateReport:
        """Refresh the run time counters, which move slowly."""
        return await self._async_poll(await self._async_targets(slow=True))

    # -- diagnostics ---------------------------------------------------------

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Every register this installation reads, undecoded."""
        raw: dict[str, dict[int, int | bool]] = {}
        targets = await self._async_targets(slow=False)
        targets += await self._async_targets(slow=True)
        for label, component in targets:
            try:
                read = await component.async_read_raw(notify=False)
            except ModbusError:
                continue
            for space, values in read.items():
                raw.setdefault(f"{label}:{space}", {}).update(values)
        return raw
