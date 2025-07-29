from typing import Tuple, TYPE_CHECKING
import ida_xref

if TYPE_CHECKING:
    from .database import Database


class Xrefs:
    """
    Provides access to cross-reference (xref) analysis in the IDA database.
    """

    class ToIterator:
        """Iterator for incoming cross-references (to the specified address)."""

        def __init__(self, database: "Database", ea: int):
            """
            Constructs an iterator for cross-references **to** a given address.

            Args:
                database: Reference to the active IDA database.
                ea: The target effective address.
            """
            self.m_database = database
            self.target_ea = ea
            self.xref = ida_xref.xrefblk_t()

        def get_first(self) -> Tuple[bool, object]:
            """
            Retrieves the first incoming xref.

            Returns:
                A pair <bool, xrefblk_t>. The bool is false if no xref is found.
            """
            if self.xref.first_to(self.target_ea, ida_xref.XREF_ALL):
                return (True, self.xref)
            return (False, ida_xref.xrefblk_t())

        def __iter__(self):
            """Python iterator protocol - matches SWIG extension."""
            success, xref = self.get_first()
            while success:
                yield xref
                success, xref = self.get_next()

        def get_next(self) -> Tuple[bool, object]:
            """
            Retrieves the next incoming xref.

            Returns:
                A pair <bool, xrefblk_t>. The bool is false if no more xrefs exist.
            """
            if self.xref.next_to():
                return (True, self.xref)
            return (False, ida_xref.xrefblk_t())

    class FromIterator:
        """Iterator for outgoing cross-references (from the specified address)."""

        def __init__(self, database: "Database", ea: int):
            """
            Constructs an iterator for cross-references **from** a given address.

            Args:
                database: Reference to the active IDA database.
                ea: The source effective address.
            """
            self.m_database = database
            self.source_ea = ea
            self.xref = ida_xref.xrefblk_t()

        def get_first(self) -> Tuple[bool, object]:
            """
            Retrieves the first outgoing xref.

            Returns:
                A pair <bool, xrefblk_t>. The bool is false if no xref is found.
            """
            if self.xref.first_from(self.source_ea, ida_xref.XREF_ALL):
                return (True, self.xref)
            return (False, ida_xref.xrefblk_t())

        def __iter__(self):
            """Python iterator protocol - matches SWIG extension."""
            success, xref = self.get_first()
            while success:
                yield xref
                success, xref = self.get_next()

        def get_next(self) -> Tuple[bool, object]:
            """
            Retrieves the next outgoing xref.

            Returns:
                A pair <bool, xrefblk_t>. The bool is false if no more xrefs exist.
            """
            if self.xref.next_from():
                return (True, self.xref)
            return (False, ida_xref.xrefblk_t())

    def __init__(self, database: "Database"):
        """
        Constructs an xrefs handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get_to(self, ea: int) -> "ToIterator":
        """
        Creates an iterator over all xrefs pointing to a given address.

        Args:
            ea: Target effective address.

        Returns:
            An iterator over incoming xrefs.
        """
        return self.ToIterator(self.m_database, ea)

    def get_from(self, ea: int) -> "FromIterator":
        """
        Creates an iterator over all xrefs originating from a given address.

        Args:
            ea: Source effective address.

        Returns:
            An iterator over outgoing xrefs.
        """
        return self.FromIterator(self.m_database, ea)