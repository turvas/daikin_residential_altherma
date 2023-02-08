from __future__ import annotations

from collections.abc import Mapping
from contextvars import ContextVar
from util import uuid as uuid_util
from typing import Any
from helpers.typing import UNDEFINED, UndefinedType
from types import MappingProxyType
from light_helpers import callback

SOURCE_IMPORT = "import"


class ConfigEntry:
    """Hold a configuration entry."""

    __slots__ = (
        "entry_id",
        "version",
        "domain",
        "title",
        "data",
    )

    def __init__(
        self,
        version: int,
        domain: str,
        title: str,
        data: Mapping[str, Any],
        entry_id: str | None = None,
    ) -> None:
        """Initialize a config entry."""
        # Unique id of the config entry
        self.entry_id = entry_id or uuid_util.random_uuid_hex()

        # Version of the configuration.
        self.version = version

        # Domain the configuration belongs to
        self.domain = domain

        # Title of the configuration
        self.title = title

        # Config data
        self.data = MappingProxyType(data)

    async def async_setup(
        self,
        hass,
        *,
        integration = None,
        tries: int = 0,
    ) -> None:
        """Set up an entry."""
        current_entry.set(self)


current_entry: ContextVar[ConfigEntry | None] = ContextVar(
    "current_entry", default=None
)


class ConfigEntries:
    """Manage the configuration entries.
    An instance of this object is available via `hass.config_entries`. """

    def __init__(self, hass, hass_config) -> None:   # : ConfigType
        """Initialize the entry manager."""
        self.hass = hass
        self._hass_config = hass_config
        self._entries: dict[str, ConfigEntry] = {}
        self._domain_index: dict[str, list[str]] = {}

    async def async_add(self, entry: ConfigEntry) -> None:
        """Add and setup an entry."""
        if entry.entry_id in self._entries:
            raise Exception( f"An entry with the id {entry.entry_id} already exists.")
        self._entries[entry.entry_id] = entry

    @callback
    def async_get_entry(self, entry_id: str) -> ConfigEntry | None:
        """Return entry with matching entry_id."""
        return self._entries.get(entry_id)

    @callback
    def async_entries(self, domain: str | None = None) -> list[ConfigEntry]:
        """Return all entries or entries for a specific domain."""
        if domain is None:
            return list(self._entries.values())
        return [
            self._entries[entry_id] for entry_id in self._domain_index.get(domain, [])
        ]

    async def async_forward_entry_setup(
        self, entry: ConfigEntry, domain: str
    ) -> bool:
        """Forward the setup of an entry to a different component."""
        await entry.async_setup(self.hass)
        return True

    @callback
    def async_update_entry(
            self,
            entry: ConfigEntry,
            *,
            data: Mapping[str, Any] | UndefinedType = UNDEFINED,
    ) -> bool:
        """Update a config entry."""
        return True

    async def async_forward_entry_setup(
        self, entry: ConfigEntry, domain: str
    ) -> bool:
        """Forward the setup of an entry to a different component."""

        return True

