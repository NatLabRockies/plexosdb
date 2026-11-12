---
title: "Exceptions"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.exceptions

#### NotFoundError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L10)

Raised when the database cannot locate a requested entry.

#### MultlipleElementsError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L14)

Raised when a query unexpectedly returns multiple elements.

#### ModelError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L18)

Raised for generic errors related to model relationships.

#### DatabaseValidationCategory

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L22)

Stable categories for database validation findings.

Full reference: [`DatabaseValidationCategory`](/plexosdb/reference/python-api/databasevalidationcategory/).

#### DatabaseValidationFinding

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L36)

One structured finding produced by database validation.

Full reference: [`DatabaseValidationFinding`](/plexosdb/reference/python-api/databasevalidationfinding/).

#### DatabaseValidationError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L43)

Raised when database validation finds integrity or consistency issues.

WARN labels are yellow when stderr is a terminal, unless NO_COLOR is set.
Redirected output remains plain text.

Full reference: [`DatabaseValidationError`](/plexosdb/reference/python-api/databasevalidationerror/).

#### MultipleFilesError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L62)

Raised when multiple files are provided but only one is expected.

#### NameError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L66)

Raised when an object name is invalid or missing in context.

#### NoPropertiesError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L70)

Raised when a lookup finds no properties for a given object.

#### PropertyError

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/exceptions.py#L74)

Raised when we have a problem with a property.

<!-- End generated API reference -->
