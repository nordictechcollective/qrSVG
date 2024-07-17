from __future__ import annotations

import re
from enum import IntEnum
from types import MappingProxyType
from typing import NamedTuple

from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q

FROM_PX = MappingProxyType(
    {
        "px": lambda x: x,
        "pt": lambda x: x / 1.25,
        "pc": lambda x: x / 15.0,
        "in": lambda x: x / 90.0,
        "mm": lambda x: x / 3.543307,
        "cm": lambda x: x / 35.43307,
        "%": lambda x: x * -100.0,
    }
)

TO_PX = MappingProxyType(
    {
        "px": lambda x: x,
        "pt": lambda x: x * 1.25,
        "pc": lambda x: x * 15.0,
        "in": lambda x: x * 90.0,
        "mm": lambda x: x * 3.543307,
        "cm": lambda x: x * 35.43307,
        "%": lambda x: x / -100.0,
    }
)


def _to_pixels(value: str, def_units="px") -> float:
    """Parses value as SVG length and returns it in pixels"""
    size = re.compile(
        rf"""
            ^\s*
            (?P<number>-?\d+(?:\.\d+)?)
            \s*
            (?P<unit>{'|'.join(TO_PX.keys())})?
        """,
        re.VERBOSE,
    )

    if not value:
        return 0.0

    if not (parts := size.match(value)):
        raise Exception(f'Unknown length format: "{value}"')

    try:
        unit = parts["unit"] or def_units
        return TO_PX[unit](float(parts["number"]))
    except KeyError as e:
        raise Exception(f"Unknown length units: {parts['unit']}") from e


class ViewBox(NamedTuple):
    x: float
    y: float
    width: float
    height: float

    def __str__(self) -> str:
        return f"{self.x:f} {self.y:f} {self.width:f} {self.height:f}"

    @classmethod
    def from_string(cls, string: str) -> ViewBox | None:  # type: ignore
        separators = re.compile(r"[ ,\t]+")
        try:
            x, y, width, height = map(_to_pixels, separators.split(string.strip()))
        except ValueError:
            return None

        if width * height <= 0.0:
            return None

        return cls(x, y, width, height)


class Size(NamedTuple):
    width: float
    height: float
    unit: str = "px"

    @classmethod
    def from_string(cls, width: str, height: str, unit: str):
        w, h = map(_to_pixels, (width, height))
        return cls(
            width=FROM_PX[unit](w),
            height=FROM_PX[unit](h),
            unit=unit,
        )


class Offset(NamedTuple):
    x: float
    y: float


class CorrectionLevel(IntEnum):
    L = ERROR_CORRECT_L
    M = ERROR_CORRECT_M
    Q = ERROR_CORRECT_Q
    H = ERROR_CORRECT_H

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s: str):
        try:
            return CorrectionLevel[s.upper()]
        except KeyError as e:
            raise ValueError() from e
