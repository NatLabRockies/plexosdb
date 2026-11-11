---
title: "PropertyRecord"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L60)

Type definition for property records returned by iterate_properties.

**Attributes**

- `parent_class : str`
  Name of the parent class
- `child_class : str`
  Name of the child class
- `parent_id : int`
  ID of the parent object
- `object_id : int`
  ID of the child object
- `name : str`
  Name of the object
- `category : str`
  Category name of the object
- `property : str`
  Property name
- `unit : str`
  Unit of measurement
- `value : float | str | None`
  Property value
- `band : int`
  Band ID (defaults to 1)
- `date_from : str | None`
  Start date for the property
- `date_to : str | None`
  End date for the property
- `text : str | None`
  Associated text data
- `text_class_name : str | None`
  Class name of the text
- `timeslice_id : str | None`
  Name of associated timeslice
- `datafile_name : str | None`
  Name of associated data file
- `datafile_id : int | None`
  ID of associated data file
- `variable_name : str | None`
  Name of associated variable
- `variable_id : int | None`
  ID of associated variable
- `action : str | None`
  Action symbol
- `scenario_name : str | None`
  Name of associated scenario

## Import

```python
from plexosdb import PropertyRecord
```

## Declared methods and properties
