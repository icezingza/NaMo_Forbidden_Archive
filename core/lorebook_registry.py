"""Manifest-aware lorebook registry for NaMo runtime.

The registry keeps source files immutable, validates the list[entry] schema used by the
NaMo lorebook loader, and annotates entries with source metadata for observability.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

DEFAULT_LOREBOOK_DIR = Path("core/lorebooks")
DEFAULT_BASE_LOREBOOK = DEFAULT_LOREBOOK_DIR / "Sex_Positions_Kinks_SlowBurn_TH_v10.json"
DEFAULT_ROLEPLAY000_MANIFEST = DEFAULT_LOREBOOK_DIR / "ROLEPLAY000_IMPORT_MANIFEST_TH.json"


class LorebookRegistryError(ValueError):
    """Raised when a lorebook source or manifest is malformed."""


@dataclass(frozen=True, slots=True)
class LorebookSource:
    path: Path
    declared_entries: int | None = None
    source_archive_name: str | None = None


class LorebookRegistry:
    """Load and combine multiple NaMo list-compatible lorebooks.

    Source text is not rewritten. Entries are shallow-normalized only for whitespace and
    receive private runtime metadata keys prefixed with ``_source_``.
    """

    def __init__(self, sources: Iterable[LorebookSource]) -> None:
        self.sources = tuple(sources)
        self.entries: list[dict[str, Any]] = []
        self.source_counts: dict[str, int] = {}
        self._load_sources()

    @classmethod
    def default(cls) -> "LorebookRegistry":
        sources: list[LorebookSource] = []
        if DEFAULT_BASE_LOREBOOK.exists():
            sources.append(LorebookSource(DEFAULT_BASE_LOREBOOK))
        if DEFAULT_ROLEPLAY000_MANIFEST.exists():
            sources.extend(cls.sources_from_manifest(DEFAULT_ROLEPLAY000_MANIFEST))
        return cls(sources)

    @classmethod
    def from_single_file(cls, path: str | Path) -> "LorebookRegistry":
        return cls([LorebookSource(Path(path))])

    @classmethod
    def from_manifest(
        cls,
        manifest_path: str | Path,
        *,
        include_base_lorebook: bool = False,
    ) -> "LorebookRegistry":
        manifest = Path(manifest_path)
        sources: list[LorebookSource] = []
        if include_base_lorebook and DEFAULT_BASE_LOREBOOK.exists():
            sources.append(LorebookSource(DEFAULT_BASE_LOREBOOK))
        sources.extend(cls.sources_from_manifest(manifest))
        return cls(sources)

    @staticmethod
    def sources_from_manifest(manifest_path: str | Path) -> list[LorebookSource]:
        path = Path(manifest_path)
        if not path.exists():
            raise LorebookRegistryError(f"Lorebook manifest not found: {path}")
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise LorebookRegistryError("Lorebook manifest must be a JSON object")

        files = data.get("files")
        if not isinstance(files, list):
            raise LorebookRegistryError("Lorebook manifest field 'files' must be a list")

        sources: list[LorebookSource] = []
        for item in files:
            if not isinstance(item, dict) or not item.get("file"):
                raise LorebookRegistryError("Every manifest file record must contain 'file'")
            schema = item.get("schema")
            if schema not in (None, "list[entry]"):
                raise LorebookRegistryError(
                    f"Unsupported lorebook schema for {item['file']}: {schema}"
                )
            declared = item.get("entries")
            declared_entries = int(declared) if declared is not None else None
            sources.append(
                LorebookSource(
                    path=path.parent / str(item["file"]),
                    declared_entries=declared_entries,
                    source_archive_name=str(item.get("source") or "") or None,
                )
            )
        return sources

    @staticmethod
    def _clean_entry(entry: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for key, value in entry.items():
            clean_key = str(key).strip()
            if isinstance(value, str):
                clean_value: Any = value.strip()
            elif isinstance(value, list):
                clean_value = [item.strip() if isinstance(item, str) else item for item in value]
            else:
                clean_value = value
            cleaned[clean_key] = clean_value
        return cleaned

    def _load_sources(self) -> None:
        source_index = 0
        for source in self.sources:
            path = source.path
            if not path.exists():
                logger.warning("Lorebook source not found: %s", path)
                continue
            with path.open(encoding="utf-8") as fh:
                raw = json.load(fh)
            if not isinstance(raw, list):
                raise LorebookRegistryError(
                    f"Lorebook must use list[entry] schema: {path}"
                )
            if source.declared_entries is not None and len(raw) != source.declared_entries:
                raise LorebookRegistryError(
                    f"Manifest count mismatch for {path.name}: "
                    f"declared={source.declared_entries}, actual={len(raw)}"
                )

            self.source_counts[path.name] = len(raw)
            for entry_index, raw_entry in enumerate(raw):
                if not isinstance(raw_entry, dict):
                    raise LorebookRegistryError(
                        f"Lorebook entry {entry_index} in {path} must be an object"
                    )
                entry = self._clean_entry(raw_entry)
                entry["_source_lorebook"] = path.name
                entry["_source_path"] = str(path)
                entry["_source_index"] = source_index
                entry["_entry_index"] = entry_index
                self.entries.append(entry)
            source_index += 1

        self.entries.sort(
            key=lambda item: (
                int(item.get("insertion_order", item.get("order", 100)) or 100),
                int(item.get("_source_index", 0)),
                int(item.get("_entry_index", 0)),
            )
        )

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    @property
    def roleplay000_entries(self) -> int:
        return sum(
            count
            for name, count in self.source_counts.items()
            if name
            in {
                "Story_Engine_TH.json",
                "Simple_Personality_Traits_TH.json",
                "Sex_Acts_TH.json",
                "Most_Useful_Items_TH.json",
            }
        )
