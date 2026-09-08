"""Field constructors that carry the manufacturer's datasheet with them.

These wrap the generic ``modbus_connection.model`` field helpers so every
declaration in :mod:`kermi_xcenter_modbus.devices` states the register, the
scaling, the documented range *and* the manufacturer's own label in one place.
A writable field automatically gets a validator built from its documented
range, so an out-of-range value is rejected before it reaches the controller.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum
from typing import Any

from modbus_connection.model import (
    Component,
    boolean as _modbus_boolean,
    enum as _modbus_enum,
    gauge as _modbus_gauge,
    integer as _modbus_integer,
)

from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    attach_metadata,
    options_from_enum,
    step_from_digits,
)

__all__ = [
    "NAN_SENSOR",
    "KermiComponent",
    "boolean",
    "enum",
    "gauge",
    "integer",
    "temperature",
]

#: Raw word the controller returns for a temperature sensor that is not
#: fitted. It reads as -9999 signed (-999.9 °C after scaling), which is not a
#: value any consumer should see, so it decodes to ``None`` instead.
#:
#: Observed on x-center IFM against unfitted T2/T3/T4 inputs on units 50 and
#: 51; it is not printed in the manufacturer's integration guide.
NAN_SENSOR = 0xD8F1


def _range_validator(
    min_value: float | int | None,
    max_value: float | int | None,
) -> Callable[[Any], Any] | None:
    """Build a validator rejecting values outside the documented range."""
    if min_value is None and max_value is None:
        return None

    def validate(value: Any) -> Any:
        number = float(value)
        if min_value is not None and number < min_value:
            raise ValueError(f"{number} is below the documented minimum {min_value}")
        if max_value is not None and number > max_value:
            raise ValueError(f"{number} is above the documented maximum {max_value}")
        return value

    return validate


def _writable(
    writable: bool | Callable[[Any], Any],
    min_value: float | int | None,
    max_value: float | int | None,
) -> bool | Callable[[Any], Any]:
    """Combine a ``writable`` flag with a range check, where one applies."""
    if writable is False:
        return False
    validator = _range_validator(min_value, max_value)
    if validator is None:
        return writable
    if writable is True:
        return validator

    def chained(value: Any) -> Any:
        return validator(writable(value))  # type: ignore[operator]

    return chained


def _number_metadata(
    *,
    address: int,
    maker_key: str | None,
    maker_category: str | None,
    description: str | None,
    writable: bool | Callable[[Any], Any],
    min_value: float | int | None,
    max_value: float | int | None,
    digits: int | None,
    unit: str | None,
    default: float | int | None,
    documented: bool,
    range_documented: bool,
) -> DatapointMetadata:
    return DatapointMetadata(
        value_kind="number",
        maker_reference=address,
        maker_key=maker_key,
        maker_category=maker_category,
        description=description,
        writable=writable is not False,
        documented=documented,
        number=NumberMetadata(
            min_value=min_value,
            max_value=max_value,
            step=step_from_digits(digits),
            digits=digits,
            unit=unit,
            default=default,
            range_documented=range_documented,
        ),
    )


def gauge(
    address: int,
    scale: float,
    *,
    unit: str | None = None,
    digits: int | None = 1,
    signed: bool = True,
    nan: int | None = None,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    default: float | int | None = None,
    writable: bool | Callable[[Any], Any] = False,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
    documented: bool = True,
    range_documented: bool = True,
) -> Any:
    """Create a scaled numeric register field."""
    field = _modbus_gauge(
        address,
        scale,
        signed=signed,
        nan=nan,
        unit=unit,
        writable=_writable(writable, min_value, max_value),
    )
    return attach_metadata(
        field,
        _number_metadata(
            address=address,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=writable,
            min_value=min_value,
            max_value=max_value,
            digits=digits,
            unit=unit,
            default=default,
            documented=documented,
            range_documented=range_documented,
        ),
    )


def temperature(
    address: int,
    *,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    default: float | int | None = None,
    writable: bool | Callable[[Any], Any] = False,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
    range_documented: bool = True,
) -> Any:
    """Create a temperature field in tenths of a degree.

    Decodes the unfitted-sensor sentinel to ``None``.
    """
    return gauge(
        address,
        0.1,
        unit="°C",
        digits=1,
        signed=True,
        nan=NAN_SENSOR,
        min_value=min_value,
        max_value=max_value,
        default=default,
        writable=writable,
        maker_key=maker_key,
        maker_category=maker_category,
        description=description,
        range_documented=range_documented,
    )


def integer(
    address: int,
    *,
    unit: str | None = None,
    signed: bool = False,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    default: float | int | None = None,
    writable: bool | Callable[[Any], Any] = False,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
    documented: bool = True,
    range_documented: bool = True,
) -> Any:
    """Create an unscaled integer register field."""
    field = _modbus_integer(
        address,
        signed=signed,
        unit=unit,
        writable=_writable(writable, min_value, max_value),
    )
    return attach_metadata(
        field,
        _number_metadata(
            address=address,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=writable,
            min_value=min_value,
            max_value=max_value,
            digits=0,
            unit=unit,
            default=default,
            documented=documented,
            range_documented=range_documented,
        ),
    )


def enum(
    address: int,
    enum_type: type[IntEnum],
    *,
    writable: bool = False,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
) -> Any:
    """Create a register field whose value maps onto an ``IntEnum``."""
    field = _modbus_enum(address, enum_type, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="enum",
            maker_reference=address,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=writable,
            enum=EnumMetadata(
                enum_type=enum_type, options=options_from_enum(enum_type)
            ),
        ),
    )


def boolean(
    address: int,
    *,
    writable: bool = False,
    false_key: str = "no",
    true_key: str = "yes",
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
) -> Any:
    """Create a 0/1 register field decoding to ``bool``."""
    field = _modbus_boolean(address, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="boolean",
            maker_reference=address,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=writable,
            boolean=BooleanMetadata(false_key=false_key, true_key=true_key),
        ),
    )


class KermiComponent(Component):
    """Base for every x-center sub-system.

    ``register_ranges`` is declared on each subclass rather than relying on gap
    planning. The controller does not answer a read that reaches outside a
    documented block, and it signals that with a malformed response rather than
    a clean Modbus exception (see ``docs/register-verification.md``), so a
    block read must never cross into unmapped registers.
    """

    def datapoints(self) -> dict[str, DatapointMetadata]:
        """Return the manufacturer metadata for every field on this component."""
        from .metadata import datapoint_metadata

        result: dict[str, DatapointMetadata] = {}
        for name in self.declared_fields:
            metadata = datapoint_metadata(getattr(type(self), name, None))
            if metadata is not None:
                result[name] = metadata
        return result
