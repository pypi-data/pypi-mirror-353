from dataclasses import dataclass
from typing import Any, Self
import re

__all__ = [
    'JsonPointerParsingError',
    'JsonPointerMissingSlash',
    'JsonPointerInvalidEscape',
    'AfterEndOfArray',
    'AFTER_END_OF_ARRAY',
    'JsonPointerPart',
    'JsonPointer',
    'decode_part',
    'encode_part',
]


class JsonPointerParsingError(Exception):
    pass


class JsonPointerMissingSlash(JsonPointerParsingError):
    pass


class JsonPointerInvalidEscape(JsonPointerParsingError):
    pass


class AfterEndOfArray:
    """
    Singleton with no data, no slots, but on which `str()` returns '-'.
    See `type JsonPointerPart` for details.
    """

    __slots__ = ()

    def __str__(self):
        return '-'

    def __repr__(self):
        return type(self).__name__ + '()'

    def __new__(cls):
        if cls is not AfterEndOfArray:
            raise TypeError(f'Subclassing {AfterEndOfArray.__name__} prohibited.')
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance


AFTER_END_OF_ARRAY = AfterEndOfArray()
"""
Alternatively to `isinstance(part, AfterEndOfArray)`, you may safely check
`part is AFTER_END_OF_ARRAY` since it is a singleton.
"""

type JsonPointerPart = str | int | AfterEndOfArray
"""
A syntactically valid, unescaped, type-converted part of an RFC 6901 JSON Pointer.

- int: A part that could represent an array index, if the targeted parent is an array.
  - Found if: Original part is '0', or digits with no leading zeros.

- AfterEndOfArray: A part that could represent a non-existent member after the last
  element of an array, if the targeted parent is an array.
  - Found if: Original part is '-', and is the last part in the pointer.

- str: Any part that doesn't meet the criteria for the other types. The string is
  unescaped, so it can include '/' and '~' characters, which are escaped in the
  part's raw form as '~1' and '~0', respectively.
"""


@dataclass(frozen=True, slots=True)
class JsonPointer:
    """
    A lightweight, immutable dataclass to represent an RFC 6901 JSON Pointer
    as validated, pre-processed, type-converted parts, ready for document eval.

    Has a simple API: `.parts`, `.from_string(cls)`, `.to_string(self)`.

    How Early Type Conversion Works
    -------------------------------
    In addition to validating and unescaping the pointer, the `from_string()`
    parser unambiguously converts parts to appropriate types for potential array
    operations, without having knowledge of the target document structure.

    This eliminates the need for any further inspection or analysis of the pointer
    part's contents during document evaluation, letting the user safely rely on
    simple type checking to determine whether, and how, a part may be used in an
    array context.

    This example shows all the ways a part can be modified by the parser,
    including unescaping and type conversion:

    >>> pointer = JsonPointer.from_string('/~01~1bar/10 /001/100/-/-')
    >>> pointer.parts
    ('~1/bar', '10 ', '001', 100, '-', AfterEndOfArray())

    Here is each part, before and after parsing:

        '~01~1bar'   '~1/bar'     Unescaped ~0 and ~1
        '10 '        '10 '        No change
        '001'        '001'        No change
        '100'        100          Type change. Can be used as array index.
        '-'          '-'          No change
        '-'          AfterEn...   Type change. Can represent new array member.

    More Examples
    -------------
    Encode parts into raw pointer
    >>> JsonPointer(parts=('data', 'foo/bar', 1000)).to_string()
    '/data/foo~1bar/1000'

    Parse raw pointer into parts
    >>> JsonPointer.from_string('/data/foo~1bar/1000')
    JsonPointer(parts=('data', 'foo/bar', 1000))

    Empty pointer is stored as an empty parts list.
    >>> () == JsonPointer().parts == JsonPointer.from_string('').parts
    True

    Non-empty pointer missing leading slash
    >>> JsonPointer.from_string('foo')
    Traceback (most recent call last):
        ...
    jsonpointerparse.JsonPointerMissingSlash: Non-empty pointer must start with a `/`

    Invalid escape sequence
    >>> JsonPointer.from_string('/bad~5escape')
    Traceback (most recent call last):
        ...
    jsonpointerparse.JsonPointerInvalidEscape: Part 'bad~5escape' has invalid escape sequence '~5'
    """

    parts: tuple[JsonPointerPart, ...] = ()
    """
    Pointer parts, relative to the root. When empty, represents a "" pointer.
    """

    @classmethod
    def from_string(cls, pointer: str) -> Self:
        """
        Create from a JSON Pointer. Validates the pointer and preprocesses its parts.
        """
        parts = pointer.split('/')
        if parts.pop(0) != '':
            raise JsonPointerMissingSlash('Non-empty pointer must start with a `/`')

        decoded: list[JsonPointerPart] = [decode_part(p) for p in parts]
        if decoded and decoded[-1] == '-':
            decoded[-1] = AFTER_END_OF_ARRAY
        return cls(tuple(decoded))

    def to_string(self) -> str:
        """Convert to a valid, escaped JSON Pointer string."""
        return '/'.join([''] + [encode_part(p) for p in self.parts])

    @property
    def is_root(self) -> bool:
        """Whether this pointer represents the root of a document."""
        return not self.parts


# Matches an unsigned int. Must use with `re.fullmatch()`.
_RE_UINT = re.compile('0|[1-9][0-9]*')
# Matches an escape sequence prohibited by RFC 6901.
_RE_INVALID_ESCAPE = re.compile('(~[^01]|~$)')


def decode_part(part: str) -> int | str:
    """Validate, unescape, and type-convert a raw JSON Pointer part."""
    if _RE_UINT.fullmatch(part):
        return int(part)
    if match := _RE_INVALID_ESCAPE.search(part):
        raise JsonPointerInvalidEscape(
            f"Part '{part}' has invalid escape sequence '{match.group()}'"
        )
    return part.replace('~1', '/').replace('~0', '~')


def encode_part(part: Any) -> str:
    """
    Convert a JSON Pointer part to a valid, escaped string.
    Accepts any input type, using `str(input)` as the unescaped value.
    """
    return str(part).replace('~', '~0').replace('/', '~1')
