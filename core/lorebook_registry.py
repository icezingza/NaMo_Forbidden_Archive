"""Manifest-aware lorebook registry for the NaMo runtime."""

from __future__ import annotations

import gzip
import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LOREBOOK_DIR = Path("core/lorebooks")
DEFAULT_BASE_LOREBOOK = DEFAULT_LOREBOOK_DIR / "Sex_Positions_Kinks_SlowBurn_TH_v10.json"
DEFAULT_ROLEPLAY000_MANIFEST = DEFAULT_LOREBOOK_DIR / "ROLEPLAY000_IMPORT_MANIFEST_TH.json"
ROLEPLAY000_FILES = {
    "Story_Engine_TH.json",
    "Simple_Personality_Traits_TH.json",
    "Sex_Acts_TH.json",
    "Most_Useful_Items_TH.json",
}


class LorebookRegistryError(ValueError):
    """Raised when a lorebook source or manifest is malformed/incomplete."""


@dataclass(frozen=True, slots=True)
class LorebookSource:
    path: Path
    declared_entries: int | None = None
    source_archive_name: str | None = None


class LorebookRegistry:
    """Load multiple list[entry] lorebooks while preserving logical source identity.

    A manifest may name ``foo.json`` while the repository stores it losslessly as
    ``foo.json.gz`` or split ``foo.json.gz.partNN`` chunks. This is a storage detail only;
    runtime metadata and manifest validation continue to use the logical ``foo.json`` name.
    """

    def __init__(self, sources: Iterable[LorebookSource]) -> None:
        self.sources = tuple(sources)
        self.entries: list[dict[str, Any]] = []
        self.source_counts: dict[str, int] = {}
        self._load_sources()

    @classmethod
    def default(cls) -> LorebookRegistry:
        sources: list[LorebookSource] = []
        if DEFAULT_BASE_LOREBOOK.exists():
            sources.append(LorebookSource(DEFAULT_BASE_LOREBOOK))
        if DEFAULT_ROLEPLAY000_MANIFEST.exists():
            sources.extend(cls.sources_from_manifest(DEFAULT_ROLEPLAY000_MANIFEST))
        return cls(sources)

    @classmethod
    def from_single_file(cls, path: str | Path) -> LorebookRegistry:
        return cls([LorebookSource(Path(path))])

    @classmethod
    def from_manifest(
        cls, manifest_path: str | Path, *, include_base_lorebook: bool = False
    ) -> LorebookRegistry:
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
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("files"), list):
            raise LorebookRegistryError("Lorebook manifest must contain a 'files' list")

        sources: list[LorebookSource] = []
        for item in data["files"]:
            if not isinstance(item, dict) or not item.get("file"):
                raise LorebookRegistryError("Every manifest file record must contain 'file'")
            if item.get("schema") not in (None, "list[entry]"):
                raise LorebookRegistryError(
                    f"Unsupported lorebook schema for {item['file']}: {item.get('schema')}"
                )
            declared = item.get("entries")
            sources.append(
                LorebookSource(
                    path=path.parent / str(item["file"]),
                    declared_entries=int(declared) if declared is not None else None,
                    source_archive_name=str(item.get("source") or "") or None,
                )
            )
        return sources

    @staticmethod
    def _clean_entry(entry: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for key, value in entry.items():
            key = str(key).strip()
            if isinstance(value, str):
                value = value.strip()
            elif isinstance(value, list):
                value = [item.strip() if isinstance(item, str) else item for item in value]
            cleaned[key] = value
        return cleaned

    @staticmethod
    def _read_source(source: LorebookSource) -> tuple[list[Any], str] | None:
        logical = source.path
        if logical.exists():
            raw = json.loads(logical.read_text(encoding="utf-8"))
            return raw, str(logical)

        gzip_path = logical.with_name(logical.name + ".gz")
        if gzip_path.exists():
            with gzip.open(gzip_path, "rt", encoding="utf-8") as fh:
                return json.load(fh), str(gzip_path)

        parts = sorted(logical.parent.glob(logical.name + ".gz.part*"))
        if parts:
            compressed = b"".join(part.read_bytes() for part in parts)
            return json.loads(gzip.decompress(compressed).decode("utf-8")), ",".join(
                str(part) for part in parts
            )

        if source.declared_entries is not None:
            raise LorebookRegistryError(f"Declared lorebook source is missing: {logical}")
        logger.warning("Lorebook source not found: %s", logical)
        return None

    def _load_sources(self) -> None:
        for source_index, source in enumerate(self.sources):
            loaded = self._read_source(source)
            if loaded is None:
                continue
            raw, physical_source = loaded
            logical_name = source.path.name
            if not isinstance(raw, list):
                raise LorebookRegistryError(f"Lorebook must use list[entry] schema: {logical_name}")
            if source.declared_entries is not None and len(raw) != source.declared_entries:
                raise LorebookRegistryError(
                    f"Manifest count mismatch for {logical_name}: "
                    f"declared={source.declared_entries}, actual={len(raw)}"
                )

            self.source_counts[logical_name] = len(raw)
            for entry_index, raw_entry in enumerate(raw):
                if not isinstance(raw_entry, dict):
                    raise LorebookRegistryError(
                        f"Lorebook entry {entry_index} in {logical_name} must be an object"
                    )
                entry = self._clean_entry(raw_entry)
                entry["_source_lorebook"] = logical_name
                entry["_source_path"] = physical_source
                entry["_source_index"] = source_index
                entry["_entry_index"] = entry_index
                self.entries.append(entry)

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
        return sum(count for name, count in self.source_counts.items() if name in ROLEPLAY000_FILES)
