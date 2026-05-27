"""Shared type aliases for the property insertion pipeline."""

from datetime import datetime
from typing import TypeAlias

PropValue: TypeAlias = int | float | str | None
MetadataValue: TypeAlias = str | int | float | datetime | None
PropertyParams: TypeAlias = list[tuple[int, int, PropValue]]
MetadataMap: TypeAlias = dict[tuple[int, int, PropValue, int], dict[str, MetadataValue]]
DataIdMap: TypeAlias = dict[tuple[int, int, PropValue, int], tuple[int, str]]
