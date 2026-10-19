# XML record contract

`plexosdb.element_to_record(element, rename=...)` extracts one row's direct
child fields into an `XMLRecord` (`dict[str, str | None]`). Both `XMLHandler`
and the solution ZIP reader use this function.

- Field names use the local XML name, regardless of namespace prefix or URI.
- A missing field has no dictionary entry. An empty element has value `None`.
  Whitespace-only elements retain their whitespace.
- Text retains the spelling parsed by ElementTree. XML escapes are decoded and
  XML line endings are normalized by the XML parser. Numeric, Boolean, quoted,
  container-looking, and Unicode text receive no literal interpretation.
- Renaming applies to local field names. Duplicate local names and rename
  collisions keep the last field in document order. Nested markup is not
  flattened, so only the direct child's `.text` is returned.
- Extraction does not modify elements, select rows, or remove repeated rows.

`XMLHandler` retains its tree, cache, filtering, renaming, and export API. Model
import applies destination SQLite affinity and converts Boolean text only for
BIT columns. Attribute value export retains its existing integer formatting
policy. The solution reader stores XML fields as TEXT, discovers tables and
columns while streaming, clears completed rows, and flushes bounded batches per
table. Missing columns become SQL NULL. New fields in later batches now extend
the table rather than failing at a batch boundary. Each source row is inserted
once, including identical repeated rows, in source order per table. BIN decoding
and derived table materialization remain separate operations.

SQLite column names use ASCII case-insensitive identity. The solution loader
retains the first spelling of each column and binds later ASCII case variants to
it. If one row contains both spellings, the last field wins. Unicode names
outside ASCII remain distinct. This destination policy does not alter raw XML
records, whose field names are case-sensitive.

Optional BIN period offsets containing only whitespace decode as zero. This
conversion happens in the BIN decoder and preserves the imported offset text.
Optional `phase_id`, `is_summary`, and fallback `period_type_id` values treat
blank text as missing during materialization. Stored XML fields remain
unchanged.

Numeric reference joins treat Unicode-whitespace-only values as missing and keep
explicit zero valid. Matching expression indexes use the same native SQLite
normalization. Blank summary names fall back to property names so distinct
properties retain distinct result tables.

Report timestamp conversion trims surrounding Unicode whitespace before
converting ISO or day/month/year dates. The imported XML and derived data
datetime fields retain their original text. This fixes padded report dates
without changing raw extraction policy.
