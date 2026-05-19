"""Runtime data types for virtual_ams."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .coordinator import VirtualAmsCoordinator

type VirtualAmsConfigEntry = ConfigEntry[VirtualAmsData]


@dataclass
class VirtualAmsData:
    """Runtime data attached to each Virtual AMS config entry."""

    coordinator: VirtualAmsCoordinator


@dataclass
class SpoolRegistrationData:
    """Parameters for registering or updating a spool in the inventory."""

    fingerprint: str
    name: str
    color_hex: str
    material: str
    weight: float
    initial_weight: float | None = field(default=None)
    friendly_name: str | None = field(default=None)
