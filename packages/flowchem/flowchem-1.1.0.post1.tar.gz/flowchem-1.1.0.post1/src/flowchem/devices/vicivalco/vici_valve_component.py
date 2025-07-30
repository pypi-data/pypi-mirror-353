"""Vici valve component."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .vici_valve import ViciValve
from flowchem.components.valves.injection_valves import SixPortTwoPositionValve


class ViciInjectionValve(SixPortTwoPositionValve):
    hw_device: ViciValve  # for typing's sake

    # todo this needs to be adapted to new code
    def _change_connections(self, raw_position: int | str, reverse: bool = False) -> str:
        # TODO maybe needs addition of one, not sure
        if not reverse:
            translated = str(raw_position)
        else:
            translated = str(raw_position)
        return translated
