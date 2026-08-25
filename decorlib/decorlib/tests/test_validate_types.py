from typing import List, Optional, Union

import pytest
from decorlib import validate_types
from decorlib.validate_types import TypeValidationError


def test_validate_types_bare_usage_passes():
    @validate_types
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_validate_types_rejects_bad_argument():
    @validate_types
    def add(a: int, b: int) -> int:
        return a + b

    with pytest.raises(TypeValidationError):
        add("1", 2)


def test_validate_types_rejects_bad_return():
    @validate_types
    def bad_return(a: int) -> str:
        return a  # not a str

    with pytest.raises(TypeValidationError):
        bad_return(5)


def test_validate_types_supports_optional():
    @validate_types
    def greet(name: Optional[str] = None) -> str:
        return name or "world"

    assert greet() == "world"
    assert greet("Ada") == "Ada"
    with pytest.raises(TypeValidationError):
        greet(123)


def test_validate_types_supports_union():
    @validate_types
    def to_str(value: Union[int, str]) -> str:
        return str(value)

    assert to_str(5) == "5"
    assert to_str("five") == "five"
    with pytest.raises(TypeValidationError):
        to_str(5.5)


def test_validate_types_supports_list_of():
    @validate_types
    def total(values: List[int]) -> int:
        return sum(values)

    assert total([1, 2, 3]) == 6
    with pytest.raises(TypeValidationError):
        total([1, "2", 3])


def test_validate_types_check_return_false_skips_return_check():
    @validate_types(check_return=False)
    def bad_return(a: int) -> str:
        return a

    assert bad_return(5) == 5
