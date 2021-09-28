from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from lona.view import LonaView


@dataclass
class ViewEvent:
    name: str
    data: dict
    view_classes: list[type[LonaView]]
