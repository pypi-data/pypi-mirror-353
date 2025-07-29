import pytest

from schemautil.a import (
    make_array,
    make_complex_union,
    make_enum,
    make_primitive,
    make_primitive_union,
    make_type,
    nullable_type,
    object_schema,
)


class TestBasicObjectSchema:
    """Tests for basic object schema generation"""

    def test_simple_object_schema(self):
        """Test the example from README: obj_schema({"a": "string", "b": "string"})"""
        obj = {"a": "string", "b": "string"}
        expected = {
            "type": "object",
            "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
            "required": ["a", "b"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_mixed_primitive_types(self):
        """Test object with different primitive types"""
        obj = {"name": "string", "age": "number", "active": "boolean"}
        expected = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "active": {"type": "boolean"},
            },
            "required": ["name", "age", "active"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected


class TestNullableFields:
    """Tests for nullable fields (ending with ?)"""

    def test_nullable_field(self):
        """Test field with ? suffix for nullable types"""
        obj = {"a": "string", "b?": "string"}
        expected = {
            "type": "object",
            "properties": {"a": {"type": "string"}, "b": {"type": ["string", "null"]}},
            "required": ["a", "b"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_multiple_nullable_fields(self):
        """Test multiple nullable fields"""
        obj = {"required": "string", "optional1?": "number", "optional2?": "boolean"}
        expected = {
            "type": "object",
            "properties": {
                "required": {"type": "string"},
                "optional1": {"type": ["number", "null"]},
                "optional2": {"type": ["boolean", "null"]},
            },
            "required": ["required", "optional1", "optional2"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected


class TestArrayTypes:
    """Tests for array types (wrapped in [])"""

    def test_string_array(self):
        """Test array of strings"""
        obj = {"items": ["string"]}
        expected = {
            "type": "object",
            "properties": {"items": {"type": "array", "items": {"type": "string"}}},
            "required": ["items"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_mixed_arrays(self):
        """Test different array types"""
        obj = {"strings": ["string"], "numbers": ["number"], "booleans": ["boolean"]}
        expected = {
            "type": "object",
            "properties": {
                "strings": {"type": "array", "items": {"type": "string"}},
                "numbers": {"type": "array", "items": {"type": "number"}},
                "booleans": {"type": "array", "items": {"type": "boolean"}},
            },
            "required": ["strings", "numbers", "booleans"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_nullable_array(self):
        """Test nullable array field"""
        obj = {"items?": ["string"]}
        expected = {
            "type": "object",
            "properties": {
                "items": {"type": ["array", "null"], "items": {"type": "string"}}
            },
            "required": ["items"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected


class TestUnionTypes:
    """Tests for union types (multiple types in [])"""

    def test_simple_union(self):
        """Test union of string and number"""
        obj = {"value": ["string", "number"]}
        expected = {
            "type": "object",
            "properties": {"value": {"type": ["string", "number"]}},
            "required": ["value"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_three_type_union(self):
        """Test union of all primitive types"""
        obj = {"value": ["string", "number", "boolean"]}
        expected = {
            "type": "object",
            "properties": {"value": {"type": ["string", "number", "boolean"]}},
            "required": ["value"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_nullable_union(self):
        """Test nullable union field"""
        obj = {"value?": ["string", "number"]}
        expected = {
            "type": "object",
            "properties": {"value": {"type": ["string", "number", "null"]}},
            "required": ["value"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected


class TestNestedObjects:
    """Tests for nested object schemas"""

    def test_nested_object(self):
        """Test object containing another object"""
        obj = {"user": {"name": "string", "age": "number"}}
        expected = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                    },
                    "required": ["name", "age"],
                    "additionalProperties": False,
                }
            },
            "required": ["user"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_nullable_nested_object(self):
        """Test nullable nested object"""
        obj = {"user?": {"name": "string"}}
        expected = {
            "type": "object",
            "properties": {
                "user": {
                    "type": ["object", "null"],
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                    "additionalProperties": False,
                }
            },
            "required": ["user"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected


class TestComplexCombinations:
    """Tests for complex combinations of features"""

    def test_complex_schema(self):
        """Test complex schema with arrays, unions, and nullable fields"""
        obj = {
            "id": "string",
            "tags": ["string"],
            "metadata?": {"key": "string", "value": ["string", "number"]},
            "status": ["string", "number"],
            "items?": [{"name": "string", "count?": "number"}],
        }
        expected = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "metadata": {
                    "type": ["object", "null"],
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": ["string", "number"]},
                    },
                    "required": ["key", "value"],
                    "additionalProperties": False,
                },
                "status": {"type": ["string", "number"]},
                "items": {
                    "type": ["array", "null"],
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "count": {"type": ["number", "null"]},
                        },
                        "required": ["name", "count"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["id", "tags", "metadata", "status", "items"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_array_of_objects(self):
        """Test array containing objects"""
        obj = {"users": [{"name": "string", "email?": "string"}]}
        expected = {
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": ["string", "null"]},
                        },
                        "required": ["name", "email"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["users"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected


class TestEnumTypes:
    """Tests for enum types (string lists that are not primitives)"""

    def test_simple_enum(self):
        """Test simple string enum"""
        obj = {"status": ["enum", "pending", "approved", "rejected"]}
        expected = {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "approved", "rejected"],
                }
            },
            "required": ["status"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_nullable_enum(self):
        """Test nullable enum field"""
        obj = {"color?": ["enum", "red", "green", "blue"]}
        expected = {
            "type": "object",
            "properties": {
                "color": {"type": "string", "enum": ["red", "green", "blue"]}
            },
            "required": ["color"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_two_value_enum(self):
        """Test enum with only two values"""
        obj = {"enabled": ["enum", "yes", "no"]}
        expected = {
            "type": "object",
            "properties": {"enabled": {"type": "string", "enum": ["yes", "no"]}},
            "required": ["enabled"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected

    def test_enum_vs_primitive_union(self):
        """Test that primitive union and enum are handled differently"""
        # This should be a primitive union
        obj_primitive = {"value": ["string", "number"]}
        expected_primitive = {
            "type": "object",
            "properties": {"value": {"type": ["string", "number"]}},
            "required": ["value"],
            "additionalProperties": False,
        }
        assert object_schema(obj_primitive) == expected_primitive

        # This should be an enum
        obj_enum = {"status": ["enum", "active", "inactive"]}
        expected_enum = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "inactive"]}
            },
            "required": ["status"],
            "additionalProperties": False,
        }
        assert object_schema(obj_enum) == expected_enum

    def test_complex_enum_example(self):
        """Test enum in a more complex schema"""
        obj = {
            "id": "string",
            "status": ["enum", "draft", "published", "archived"],
            "priority?": ["enum", "low", "medium", "high", "urgent"],
        }
        expected = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["draft", "published", "archived"],
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "urgent"],
                },
            },
            "required": ["id", "status", "priority"],
            "additionalProperties": False,
        }
        assert object_schema(obj) == expected


class TestHelperFunctions:
    """Tests for individual helper functions"""

    def test_nullable_type(self):
        """Test nullable_type helper function"""
        assert nullable_type("string", False) == "string"
        assert nullable_type("string", True) == ["string", "null"]
        assert nullable_type("number", True) == ["number", "null"]

    def test_make_primitive(self):
        """Test make_primitive helper function"""
        assert make_primitive("string", False) == {"type": "string"}
        assert make_primitive("number", True) == {"type": ["number", "null"]}

    def test_make_array(self):
        """Test make_array helper function"""
        result = make_array(["string"], False)
        expected = {"type": "array", "items": {"type": "string"}}
        assert result == expected

        result_nullable = make_array(["number"], True)
        expected_nullable = {"type": ["array", "null"], "items": {"type": "number"}}
        assert result_nullable == expected_nullable

    def test_make_primitive_union(self):
        """Test make_primitive_union helper function"""
        # Simple primitive union
        result = make_primitive_union(["string", "number"], False)
        assert result == {"type": ["string", "number"]}

        # Nullable primitive union
        result_nullable = make_primitive_union(["string", "number"], True)
        assert result_nullable == {"type": ["string", "number", "null"]}

    def test_make_enum(self):
        """Test make_enum helper function"""
        # Simple enum
        result = make_enum(["pending", "approved", "rejected"], False)
        expected = {"type": "string", "enum": ["pending", "approved", "rejected"]}
        assert result == expected

        # Nullable enum (note: the nullable parameter doesn't affect the enum itself)
        result_nullable = make_enum(["active", "inactive"], True)
        expected_nullable = {"type": "string", "enum": ["active", "inactive"]}
        assert result_nullable == expected_nullable

    def test_make_complex_union(self):
        """Test make_complex_union helper function"""
        # Union of mixed types (not all primitives)
        items = [{"name": "string"}, ["string"]]
        result = make_complex_union(items, False)
        expected = {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                    "additionalProperties": False,
                },
                {"type": "array", "items": {"type": "string"}},
            ]
        }
        assert result == expected

        # Nullable complex union
        result_nullable = make_complex_union([{"id": "string"}, "string"], True)
        expected_nullable = {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                    "required": ["id"],
                    "additionalProperties": False,
                },
                {"type": "string"},
                {"type": "null"},
            ]
        }
        assert result_nullable == expected_nullable


class TestErrorCases:
    """Tests for error conditions and edge cases"""

    def test_unsupported_type(self):
        """Test that unsupported types raise ValueError"""
        with pytest.raises(ValueError, match="Unsupported value type"):
            make_type(123, False)  # Integer not supported

        with pytest.raises(ValueError, match="Unsupported value type"):
            make_type("invalid_type", False)  # Invalid string type

    def test_empty_array_error(self):
        """Test that empty arrays cause assertion errors"""
        with pytest.raises(AssertionError):
            make_array([], False)

    def test_invalid_primitive(self):
        """Test that invalid primitive types cause assertion errors"""
        with pytest.raises(AssertionError):
            make_primitive("invalid", False)

    def test_enum_with_single_item_error(self):
        """Test that enum with single item causes assertion error"""
        with pytest.raises(AssertionError):
            make_enum(["single"], False)

    def test_enum_with_empty_list_error(self):
        """Test that enum with empty list causes assertion error"""
        with pytest.raises(AssertionError):
            make_enum([], False)

    def test_enum_with_non_string_items_error(self):
        """Test that enum with non-string items causes assertion error"""
        with pytest.raises(AssertionError):
            make_enum(["valid", 123, "string"], False)
