---
title: "Enumerations"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.enums

#### Schema

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L7)

Enum that defines the Plexos Schema.

##### Methods

###### name

```text
name(self) -> str
```

Table name associated with this schema element.

###### label

```text
label(self) -> str | None
```

Primary label column name for the schema element, if any.

#### ClassEnum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L59)

Enum that defines the different Plexos classes.

Full reference: [`ClassEnum`](/plexosdb/reference/python-api/classenum/).

#### plexos_class_mapping

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L93)

```text
plexos_class_mapping = {enum_member.name: enum_member.value for enum_member in ClassEnum}
```

#### CollectionEnum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L96)

Enum that defines the different Plexos colections via Collection Name.

Full reference: [`CollectionEnum`](/plexosdb/reference/python-api/collectionenum/).

#### PhaseEnum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L140)

PLEXOS solve phases used in result table names.

Full reference: [`PhaseEnum`](/plexosdb/reference/python-api/phaseenum/).

#### PeriodEnum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L149)

PLEXOS result periods used in result table names.

Full reference: [`PeriodEnum`](/plexosdb/reference/python-api/periodenum/).

#### TableTypeEnum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L161)

DuckDB information_schema table types used by solution results.

Full reference: [`TableTypeEnum`](/plexosdb/reference/python-api/tabletypeenum/).

#### str2enum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L168)

Convert string to enum.

```text
str2enum(string: str, schema_enum: type[Enum]=Schema) -> Schema | None
```

#### get_default_collection

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L176)

Return default collection for class.

```text
get_default_collection(class_enum: ClassEnum) -> CollectionEnum
```

#### parse_class_enum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L214)

Parse a string or ClassEnum to a ClassEnum instance.

```text
parse_class_enum(value: str | ClassEnum) -> ClassEnum
```

#### parse_collection_enum

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/enums.py#L219)

Parse a string or CollectionEnum to a CollectionEnum instance.

```text
parse_collection_enum(value: str | CollectionEnum) -> CollectionEnum
```

<!-- End generated API reference -->
