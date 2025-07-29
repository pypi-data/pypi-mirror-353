from __future__ import annotations

from typing import Any

from .data_model import DataModel


class ComponentContext(DataModel):
    type: str
    handle: str


class ProviderContext(DataModel):
    type: str
    handle: str | None = None


class Context(DataModel):
    id: str
    component: ComponentContext | None = None
    provider: ProviderContext | None = None
    data: dict[str, Any] | None = None
