"""Vendor-neutral metadata carried alongside each datapoint.

A field declaration states where a value lives on the wire. The metadata here
states what the manufacturer says about it: the printed name, the section of
the integration guide it came from, its range, and its precision. Keeping the
two together means the model doubles as the datasheet, and a consumer can build
a UI without a second table to maintain.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Literal

__all__ = [
    "BooleanMetadata",
    "DatapointMetadata",
    "EnumMetadata",
    "NumberMetadata",
    "OptionMetadata",
    "ValueKind",
    "attach_metadata",
    "datapoint_metadata",
    "step_from_digits",
]

ValueKind = Literal["number", "enum", "boolean", "raw"]

#: Attribute the metadata is stashed under on a field object.
METADATA_ATTRIBUTE = "kermi_metadata"


@dataclass(frozen=True)
class NumberMetadata:
    """Range and precision of a numeric datapoint."""

    min_value: float | int | None = None
    max_value: float | int | None = None
    step: float | int | None = None
    digits: int | None = None
    unit: str | None = None
    default: float | int | None = None
    #: False where the manufacturer publishes no range and the bounds here are
    #: derived from the register width or a comparable documented datapoint.
    #: The bounds still apply — an unbounded write to a heat pump is worse than
    #: a conservative one — but a consumer can tell them apart.
    range_documented: bool = True


@dataclass(frozen=True)
class OptionMetadata:
    """One selectable value of a discrete datapoint."""

    key: str
    value: int
    label: str | None = None


@dataclass(frozen=True)
class EnumMetadata:
    """Discrete datapoint backed by an ``IntEnum``."""

    enum_type: type[IntEnum]
    options: tuple[OptionMetadata, ...]


@dataclass(frozen=True)
class BooleanMetadata:
    """Two-state datapoint held in a 0/1 register."""

    false_key: str = "no"
    true_key: str = "yes"


@dataclass(frozen=True)
class DatapointMetadata:
    """Everything the manufacturer publishes about one datapoint."""

    value_kind: ValueKind
    #: Register number as printed in the integration guide.
    maker_reference: int | None = None
    #: The manufacturer's own (German) name for the datapoint.
    maker_key: str | None = None
    #: Section heading it appears under, e.g. "Leistung und Effizienz".
    maker_category: str | None = None
    description: str | None = None
    writable: bool = False
    #: False when the mapping is inferred rather than printed in the guide.
    documented: bool = True
    number: NumberMetadata | None = None
    enum: EnumMetadata | None = None
    boolean: BooleanMetadata | None = None


def step_from_digits(digits: int | None) -> float | int | None:
    """Return the natural write/UI step for a given decimal precision."""
    if digits is None:
        return None
    if digits <= 0:
        return 1
    return 10**-digits


def attach_metadata(field: Any, metadata: DatapointMetadata) -> Any:
    """Attach *metadata* to a modbus-connection field and return the field."""
    setattr(field, METADATA_ATTRIBUTE, metadata)
    return field


def datapoint_metadata(field: Any) -> DatapointMetadata | None:
    """Return the metadata attached to *field*, or None if it carries none."""
    return getattr(field, METADATA_ATTRIBUTE, None)


def options_from_enum(enum_type: type[IntEnum]) -> tuple[OptionMetadata, ...]:
    """Derive option metadata from the members of *enum_type*."""
    return tuple(
        OptionMetadata(
            key=member.name.lower(),
            value=int(member),
            label=member.name.replace("_", " ").title(),
        )
        for member in enum_type
    )
