from typing import Tuple, TYPE_CHECKING
import ida_typeinf

if TYPE_CHECKING:
    from .database import Database


class Types:
    """
    Provides access to type information and manipulation in the IDA database.
    """

    class Iterator:
        """Iterator for user-defined types in the IDA type system."""

        def __init__(self, database: "Database"):
            """
            Constructs a type iterator for the given database.

            Args:
                database: Reference to the active IDA database.
            """
            self.m_database = database
            self.current_index = 1  # Type indices start from 1

        def get_first(self) -> Tuple[bool, object]:
            """
            Retrieves the first user-defined type in the database.

            Returns:
                A pair <bool, tinfo_t>. If no type is found, the bool is false.
            """
            self.current_index = 1

            tinfo = ida_typeinf.tinfo_t()
            if tinfo.get_numbered_type(self.current_index):
                return (True, tinfo)

            return (False, ida_typeinf.tinfo_t())

        def __iter__(self):
            """Python iterator protocol - matches SWIG extension."""
            success, tinfo = self.get_first()
            while success:
                yield tinfo
                success, tinfo = self.get_next()

        def get_next(self) -> Tuple[bool, "tinfo_t"]:
            """
            Retrieves the next user-defined type in the database.

            Returns:
                A pair <bool, tinfo_t>. If no more types, the bool is false.
            """
            self.current_index += 1

            tinfo = ida_typeinf.tinfo_t()
            if ida_typeinf.get_numbered_type(None, self.current_index, ida_typeinf.BTF_TYPEDEF, tinfo):
                return (True, tinfo)

            return (False, ida_typeinf.tinfo_t())

    def __init__(self, database: "Database"):
        """
        Constructs a types handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get_type_name(self, ea: "ea_t") -> Tuple[bool, str]:
        """
        Retrieves the type information of the item at the given address.

        Args:
            ea: The effective address.

        Returns:
            A pair (success, string representing the type name). If not found, success is false.
        """
        name = ida_typeinf.idc_get_type(ea)
        if ( name is not None ):
            return (True, name )
        return (False, "")

    def apply_named_type(self, ea: "ea_t", type: "str"):
        """
        Applies a named type to the given address.

        Args:
            ea: The effective address.
            type: The name of the type to apply.

        Returns:
            True if the type was applied successfully, false otherwise.
        """
        return ida_typeinf.apply_named_type(ea, type)

    def get_all(self) -> "Iterator":
        """
        Retrieves an iterator over all user-defined types in the database.

        Returns:
            A TypesIterator instance.
        """
        return self.Iterator(self.m_database)