"""ZIP file discovery and path resolution for PLEXOS solution archives."""

from __future__ import annotations

from pathlib import Path


def _select_xml_entry(zip_path: Path, entries: list[str], model_name: str | None = None) -> str:
    """Select the best XML entry from a solution ZIP file listing."""
    xml_entries = [name for name in entries if name.lower().endswith(".xml")]
    if not xml_entries:
        raise FileNotFoundError("No XML file found in the solution ZIP.")

    stem = zip_path.stem
    for name in xml_entries:
        if Path(name).stem == stem:
            return name

    normalized_model_name = model_name.lower() if model_name else ""
    if normalized_model_name:
        for name in xml_entries:
            if normalized_model_name in Path(name).stem.lower():
                return name

    return xml_entries[0]


def _resolve_input_zip_path(input_path: str | Path) -> Path:
    """Resolve an input path to a single existing solution ZIP file."""
    path = Path(input_path)
    if path.is_file():
        if path.suffix.lower() != ".zip":
            raise ValueError(f"Input file must be a .zip solution file: {path}")
        return path
    if path.is_dir():
        zip_files = sorted(path.glob("*.zip"))
        if len(zip_files) == 1:
            return zip_files[0]
        if len(zip_files) == 0:
            raise FileNotFoundError(f"No .zip files found in directory: {path}")
        raise ValueError(f"Multiple .zip files found in directory: {path}")
    raise FileNotFoundError(f"Input path does not exist: {path}")
