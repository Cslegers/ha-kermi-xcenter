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

from ..data_model import KermiComponent, integer

__all__ = ["PvFeed", "UNIT_ID"]

#: Device address the manufacturer enables the feed-in register on.
UNIT_ID = 2


class PvFeed(KermiComponent):
    """The single register that accepts photovoltaic surplus power.

    The value is **whole watts**: writing 3500 offers 3500 W of surplus. That
    is not documented anywhere; it is what the installation this was developed
    against feeds the register, with the heat pump modulating correctly against
    it.

    Note this differs from the temperature registers on the controller, which
    are tenths of a degree. The rule across the device is that temperatures,
    coefficients of performance and kilowatt figures are scaled by 1/10, while
    watt figures are whole numbers.
    """

    register_ranges = ((1, 1),)

    surplus_power = integer(
        1,
        unit="W",
        signed=False,
        min_value=0,
        max_value=65535,
        default=0,
        writable=True,
        range_documented=False,
        maker_key="Leistungsübermittlung zur PV-Modulation",
        maker_category="PV Modulation",
        description="Photovoltaic surplus power made available to the heat pump",
        documented=False,
    )
    """Photovoltaic surplus currently offered to the heat pump."""

    async def async_set_surplus(self, watts: int) -> None:
        """Offer *watts* of photovoltaic surplus to the heat pump."""
        await self.write("surplus_power", round(watts))
