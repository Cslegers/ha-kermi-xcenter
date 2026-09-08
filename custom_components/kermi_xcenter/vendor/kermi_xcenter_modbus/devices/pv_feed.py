"""Photovoltaic surplus feed-in — device address 2.

**This endpoint is not in the manufacturer's integration guide.** It is enabled
per installation on request, and the address is communicated directly by the
manufacturer's support desk. The wording used was:

    "ich habe für die Leistungsübermittlung zur PV-Modulation folgende Adresse
    freigegeben: Port 502 Geräteadresse 2 Adresse 1"

Writing the current surplus here lets the controller modulate the heat pump
against available solar power, which is the whole point of the interface.

Two things behave differently from every documented module, both confirmed
against real hardware (see ``docs/register-verification.md``):

* The module exposes exactly **one** register. Reading address 0, or anything
  from 2 upwards, is refused.
* Where a documented module is absent the controller returns a malformed
  response rather than a Modbus exception, so probing needs
  :func:`kermi_xcenter_modbus.probe.async_module_present` rather than a plain
  ``IllegalDataAddressError`` check.
"""

from __future__ import annotations

from ..data_model import KermiComponent, gauge

__all__ = ["PvFeed", "UNIT_ID"]

#: Device address the manufacturer enables the feed-in register on.
UNIT_ID = 2


class PvFeed(KermiComponent):
    """The single register that accepts photovoltaic surplus power.

    The scaling is **not** documented. It is modelled as tenths of a watt to
    match the manufacturer's own Loxone template for the equivalent register on
    the heat pump (unit 40, register 301), but this has not been confirmed
    against a controller that was actually modulating. Confirm on your own
    installation before relying on the absolute value: write a known surplus,
    then read ``PvModulation.power`` on unit 40 back.
    """

    register_ranges = ((1, 1),)

    surplus_power = gauge(
        1,
        0.1,
        unit="W",
        min_value=0,
        max_value=6553.5,
        default=0,
        writable=True,
        range_documented=False,
        maker_key="Leistungsübermittlung zur PV-Modulation",
        maker_category="PV Modulation",
        description="Photovoltaic surplus power made available to the heat pump",
        documented=False,
    )
    """Photovoltaic surplus currently offered to the heat pump."""

    async def async_set_surplus(self, watts: float) -> None:
        """Offer *watts* of photovoltaic surplus to the heat pump."""
        await self.write("surplus_power", watts)
