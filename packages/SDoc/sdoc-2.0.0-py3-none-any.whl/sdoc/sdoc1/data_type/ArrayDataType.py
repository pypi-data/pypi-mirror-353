import copy
from typing import Any, Dict

from sdoc.sdoc1.data_type.DataType import DataType
from sdoc.sdoc1.error import DataTypeError


class ArrayDataType(DataType):
    """
    Class for array data types.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, elements: Dict[Any, DataType] | None = None):
        """
        Object constructor.

        :param elements: The elements of this array.
        """

        self._elements = copy.deepcopy(elements) if elements else {}
        """
        The elements in this array.
        """

    # ------------------------------------------------------------------------------------------------------------------
    def debug(self, indent: int = 0) -> str:
        """
        Returns a string for debugging.

        :param indent: The indentation level.
        """
        ret = '[\n'
        sep = " => "
        longest = 0
        brace_indent = indent
        first = True

        # Find the length of the longest key.
        for key in self._elements:
            if len(f'{key!s}') >= longest:
                longest = len(f'{key!s}')
                if isinstance(key, str):
                    # The longest key is a string. Add 2 positions for quotes.
                    longest += 2

        for key in sorted(self._elements, key=lambda x: str(x)):
            # Checking the key type, and setting quotes.
            if isinstance(key, int):
                str1 = " " + " " * indent + f"{key}".ljust(longest, " ")
            elif isinstance(key, str):
                str1 = " " + " " * indent + f"'{key}'".ljust(longest, " ")
            else:
                raise ValueError()

            # Creating indentation level.
            if isinstance(self._elements[key], ArrayDataType):
                # Need this check if we have many nested nodes.
                if first:
                    indent += len(str1 + sep)
                else:
                    indent = len(str1 + sep)
                str2 = f"{self._elements[key].debug(indent)}".ljust(longest, " ")
                ret += str1 + sep + str2
            else:
                str2 = f"{self._elements[key].debug()}".strip()
                ret += str1 + sep + str2 + "\n"

            first = False

        return ret + brace_indent * " " + "]\n"

    # ------------------------------------------------------------------------------------------------------------------
    def dereference(self):
        """
        Returns a clone of this array.
        """
        return ArrayDataType(self._elements)

    # ------------------------------------------------------------------------------------------------------------------
    def get_array(self, key: int | str):
        """
        Adds a new elements to this array. If the key holds an element that is already the element will be replaced.

        :param int|str key: The key of the new element. Must be a scalar data type.
        """
        if key not in self._elements:
            # Variable is not defined: create a new array.
            self._elements[key] = ArrayDataType()

        else:
            # Variable is defined.
            element = self._elements[key]
            if not isinstance(element, ArrayDataType):
                # Variable is defined but not an array: replace the element.
                self._elements[key] = ArrayDataType()

        return self._elements[key]

    # ------------------------------------------------------------------------------------------------------------------
    def add_element(self, key, value):
        """
        Adds a new elements to this array. If the key holds an element already the element will be replaced.

        :param key: The key of the new element. Must be a scalar data type.
        :param value: The value of the new element.
        """
        if not key.is_scalar():
            raise DataTypeError(f"Key '{str(key)!s}' is not a scalar.")

        self._elements[key.get_value()] = value.dereference()

        return self._elements[key.get_value()]

    # ------------------------------------------------------------------------------------------------------------------
    def get_reference(self, name: int | str):
        """
        Returns a reference to an element in this array.

        :param name: The name of the elements
        """
        if name not in self._elements:
            raise DataTypeError(f"Identifier '{name!s}' does not have a value.")

        return self._elements[name]

    # ------------------------------------------------------------------------------------------------------------------
    def get_value(self):
        """
        Not implemented.
        """
        raise RuntimeError()

    # ------------------------------------------------------------------------------------------------------------------
    def get_type_id(self) -> int:
        """
        Returns the ID of this data type.
        """
        return DataType.ARRAY

    # ------------------------------------------------------------------------------------------------------------------
    def has_element(self, name: int | str) -> bool:
        """
        Returns True if this array has a specified element.

        :param name: The name of the element.
        """
        return name in self._elements

    # ------------------------------------------------------------------------------------------------------------------
    def is_constant(self) -> bool:
        """
        Returns False always.
        """
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def is_defined(self) -> bool:
        """
        Returns True always.
        """
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def is_scalar(self) -> bool:
        """
        Returns False always.
        """
        return False

    # ------------------------------------------------------------------------------------------------------------------
    def is_true(self) -> bool:
        """
        Returns True if this array holds 1 or more elements. Returns False otherwise.
        """
        return len(self._elements) > 0

# ----------------------------------------------------------------------------------------------------------------------
