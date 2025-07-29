import pytest

# import doctest
from jsonpointerparse import JsonPointer, AfterEndOfArray


def test_after_end_of_array():
    class Sub(AfterEndOfArray):
        pass

    with pytest.raises(TypeError):
        Sub()

    x = AfterEndOfArray()
    x = AfterEndOfArray()

    assert repr(x).startswith(AfterEndOfArray.__name__)
    assert str(x) == '-'


def test_extras():
    pointer = JsonPointer()
    assert pointer.is_root is True
