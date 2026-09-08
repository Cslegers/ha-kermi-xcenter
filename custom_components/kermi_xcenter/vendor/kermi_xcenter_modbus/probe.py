"""Deciding whether a module is fitted.

The controller does not answer a read of registers it does not serve with a
Modbus exception. It replies with the *normal* function code, a byte count of
two, and no payload — a well-framed but malformed response. A client cannot
read that as ``IllegalDataAddressError``; it surfaces as a protocol error
instead. Captured from a real controller::

    unit 30, read holding 150 x1   ->  pdu 0302   (2 bytes, truncated)
    unit 40, read holding   3 x1   ->  pdu 030200d8

A spec-compliant refusal would have been ``0x83 0x02``. Because the MBAP length
field is still correct the transaction stays framed, so the link recovers by
itself and the next request succeeds.

This module centralises the "is it there?" question so no caller has to know
that. See ``docs/register-verification.md`` for the full capture.
"""

from __future__ import annotations

from modbus_connection import (
    ModbusConnectionError,
    ModbusError,
    ModbusProtocolError,
    ModbusTimeoutError,
    ModbusUnit,
)

__all__ = ["MODULE_ABSENT_ERRORS", "async_module_present"]

#: Errors that mean "this module is not fitted" rather than "the link is bad".
#:
#: ``ModbusProtocolError`` is in here because of the truncated response
#: described above; ``ModbusExceptionError`` covers a controller that answers
#: correctly. Connection and timeout errors are deliberately excluded — they
#: say nothing about whether the module exists.
MODULE_ABSENT_ERRORS = (ModbusProtocolError, ModbusError)


async def async_module_present(unit: ModbusUnit, address: int) -> bool:
    """Return whether *unit* serves *address*.

    Raises ``ModbusConnectionError`` or ``ModbusTimeoutError`` unchanged: a
    module cannot be judged absent over a link that is not working.
    """
    try:
        await unit.read_holding_registers(address, 1)
    except (ModbusConnectionError, ModbusTimeoutError):
        raise
    except ModbusError:
        return False
    return True
