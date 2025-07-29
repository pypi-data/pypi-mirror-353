from typing import Tuple, TYPE_CHECKING
import ida_strlist
import ida_bytes
import ida_nalt
import ida_idaapi

if TYPE_CHECKING:
    from .database import Database


class Strings:
    """
    Provides access to string-related operations in the IDA database.
    """

    class Iterator:
        """Iterator for strings extracted from the IDA database."""

        def __init__(self, database: "Database"):
            """
            Constructs a string iterator for the given database.

            Args:
                database: Reference to the active IDA database.
            """
            self.m_database = database
            self.current_index = 0

        def get_first(self) -> Tuple[int, str]:
            """
            Retrieves the first string in the database.

            Returns:
                A pair (effective address, string content). If none found, the string is empty.
            """
            self.current_index = 0

            if ida_strlist.get_strlist_qty() > 0:
                si = ida_strlist.string_info_t()
                if ida_strlist.get_strlist_item(si, 0):
                    return (si.ea, ida_bytes.get_strlit_contents(si.ea, -1, ida_nalt.STRTYPE_C).decode('utf-8'))

            return (ida_idaapi.BADADDR, "")  # BADADDR, empty string

        def __iter__(self):
            """Python iterator protocol - matches SWIG extension."""
            ea, string = self.get_first()
            while string:
                yield (ea, string)
                ea, string = self.get_next()

        def get_next(self) -> Tuple[int, str]:
            """
            Retrieves the next string in the database.

            Returns:
                A pair (effective address, string content). If no more strings, the string is empty.
            """
            self.current_index += 1

            if self.current_index < ida_strlist.get_strlist_qty():
                si = ida_strlist.string_info_t()
                if ida_strlist.get_strlist_item(si, self.current_index):
                    return (si.ea, ida_bytes.get_strlit_contents(si.ea, -1, ida_nalt.STRTYPE_C).decode('utf-8'))

            return (ida_idaapi.BADADDR, "")  # BADADDR, empty string

    def __init__(self, database: "Database"):
        """
        Constructs a strings handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get_count(self) -> int:
        """
        Retrieves the total number of extracted strings.

        Returns:
            The number of stored strings.
        """
        return ida_strlist.get_strlist_qty()

    def get_at_index(self, index: int) -> Tuple["ea_t", str]:
        """
        Retrieves the string at the specified index.

        Args:
            index: Index of the string to retrieve.

        Returns:
            A pair (effective address, string content) at the given index.
        """
        if index < ida_strlist.get_strlist_qty():
            si = ida_strlist.string_info_t()
            if ida_strlist.get_strlist_item(si, index):
                return (si.ea, ida_bytes.get_strlit_contents(si.ea, -1, ida_nalt.STRTYPE_C).decode('utf-8'))
        return (ida_idaapi.BADADDR, "")

    def get_at(self, ea: "ea_t") -> Tuple[bool, str]:
        """
        Retrieves the string located at the specified address.

        Args:
            ea: The effective address.

        Returns:
            A pair (success, string content). If not found, success is false.
        """
        ret = ida_bytes.get_strlit_contents(ea, -1, ida_nalt.STRTYPE_C)
        if ret is not None:
            return (True, ret.decode('utf-8'))
        return (False, None)

    def get_all(self) -> "Iterator":
        """
        Retrieves an iterator over all extracted strings in the database.

        Returns:
            A StringsIterator instance.
        """
        return self.Iterator(self.m_database)
