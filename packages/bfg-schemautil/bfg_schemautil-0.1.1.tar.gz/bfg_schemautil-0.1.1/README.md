# schemautil

A set of utilities to generate JSON Schema from simple JSON objects.

## Example

### Basic Object Schema

Given the following object schema:

```json
{
  "type": "object",
  "properties": {
    "a": { "type": "string" },
    "b": { "type": "string" }
  },
  "required": ["a", "b"],
  "additionalProperties": false
}
```

You can generate this schema using:

```python
obj_schema({"a": "string", "b": "string"})
```

### Enum Example

For an enum field:

```python
obj_schema({"status": ["pending", "approved", "rejected"]})
```

Generates:

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["pending", "approved", "rejected"]
    }
  },
  "required": ["status"],
  "additionalProperties": false
}
```

## Rules

- **All fields are required** and `additionalProperties` is always set to `false`.
- To make a field nullable, add a `?` to the end of its name.
  Example: `{"a": "string", "b?": "string"}` (`b` is nullable)
- To define an array, wrap the type in brackets.
  Example: `{"a": "string", "b": ["string"]}` (`b` is an array of strings)
  _Note: There should be only one type in the array._
- To define a field that can be one of multiple types, list the types in brackets.
  Example: `{"a": "string", "b": ["string", "number"]}` (`b` can be a string or a number)
- To define an enum (restricted set of string values), list the allowed string values in brackets.
  Example: `{"status": ["pending", "approved", "rejected"]}` (`status` must be one of these specific strings)

  **Note:** The library distinguishes between type unions and enums:
  - `["string", "number"]` → Type union (can be any string or any number)
  - `["pending", "approved"]` → String enum (must be exactly one of these values)
