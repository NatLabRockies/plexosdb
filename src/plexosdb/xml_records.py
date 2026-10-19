"""Schema-independent extraction of PLEXOS XML rows."""

import xml.etree.ElementTree as ET
from collections.abc import Mapping

from .types import XMLRecord


def local_name(tag: str, /) -> str:
    """Return an ElementTree tag's local name, ignoring its namespace URI."""
    return tag.rsplit("}", 1)[-1]


def element_to_record(element: ET.Element, /, *, rename: Mapping[str, str] | None = None) -> XMLRecord:
    """Extract direct fields without interpreting text or modifying the element.

    Missing fields are absent. Empty elements produce None. Whitespace and all
    other text remain as parsed by ElementTree, including Unicode and decoded
    XML escapes. Namespace URIs are removed before applying optional renames.
    Repeated local names and rename collisions use the last field in document
    order, matching the readers' dictionary behavior. Nested markup is not
    flattened. Row selection, schema conversion, and batching belong to callers.
    """
    record: XMLRecord = {}
    for child in element:
        name = local_name(child.tag)
        if rename is not None:
            name = rename.get(name, name)
        record[name] = child.text
    return record
