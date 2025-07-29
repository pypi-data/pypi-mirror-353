from typing import Tuple, TYPE_CHECKING
import inspect
import ida_bytes
import ida_kernwin
import ida_idaapi

if TYPE_CHECKING:
    from .database import Database


class Comments:
    """
    Provides access to user-defined comments in the IDA database.
    """

    class Iterator:
        """Iterator for user-defined comments in the IDA database."""

        def __init__(self, database: "Database", include_repeatable: bool = False):
            """
            Constructs a comment iterator for the given database.

            Args:
                database: Reference to the active IDA database.
                include_repeatable: Whether to include repeatable comments during iteration.
            """
            self.m_database = database
            self.include_repeatable = include_repeatable
            self.m_current_ea = 0

        def get_first(self) -> Tuple[int, str]:
            """
            Retrieves the first comment in the database.

            Returns:
                A pair (address, comment string). If no comments exist, the string is empty.
            """
            if not self.m_database.is_open():
                ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
                return (ida_idaapi.BADADDR, "")
            from ida_ida import inf_get_min_ea, inf_get_max_ea

            self.m_current_ea = inf_get_min_ea()

            # Find first comment
            while self.m_current_ea < inf_get_max_ea():
                comment = ida_bytes.get_cmt(self.m_current_ea, False)
                if comment:
                    return (self.m_current_ea, comment)

                if self.include_repeatable:
                    rep_comment = ida_bytes.get_cmt(self.m_current_ea, True)
                    if rep_comment:
                        return (self.m_current_ea, rep_comment)

                self.m_current_ea = ida_bytes.next_head(self.m_current_ea, inf_get_max_ea())

            return (ida_idaapi.BADADDR, "")  # BADADDR, empty string

        def __iter__(self):
            """Python iterator protocol - matches SWIG extension."""
            ea, comment = self.get_first()
            while comment:
                yield (ea, comment)
                ea, comment = self.get_next()

        def get_next(self) -> Tuple[int, str]:
            """
            Retrieves the next comment in the database.

            Returns:
                A pair (address, comment string). If no more comments exist, the string is empty.
            """
            if not self.m_database.is_open():
                ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
                return (ida_idaapi.BADADDR, "")
            from ida_ida import inf_get_max_ea

            if self.m_current_ea == ida_idaapi.BADADDR:
                return (ida_idaapi.BADADDR, "")

            # Move to next address
            self.m_current_ea = ida_bytes.next_head(self.m_current_ea, inf_get_max_ea())

            # Find next comment
            while self.m_current_ea < inf_get_max_ea():
                comment = ida_bytes.get_cmt(self.m_current_ea, False)
                if comment:
                    return (self.m_current_ea, comment)

                if self.include_repeatable:
                    rep_comment = ida_bytes.get_cmt(self.m_current_ea, True)
                    if rep_comment:
                        return (self.m_current_ea, rep_comment)

                self.m_current_ea = ida_bytes.next_head(self.m_current_ea, inf_get_max_ea())

            return (ida_idaapi.BADADDR, "")  # BADADDR, empty string

    def __init__(self, database: "Database"):
        """
        Constructs a comment manager for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get(self, ea: int) -> Tuple[bool, str]:
        """
        Retrieves the comment at the specified address.

        Args:
            ea: The effective address.

        Returns:
            A pair (success, comment string). If no comment exists, success is false.
        """
        if not self.m_database.is_open():
            ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
            return (False, "")

        comment = ida_bytes.get_cmt(ea, False)
        if comment:
            return (True, comment)

        # Try repeatable comment
        rep_comment = ida_bytes.get_cmt(ea, True)
        if rep_comment:
            return (True, rep_comment)

        return (False, "")

    def set(self, ea: int, comment: str) -> bool:
        """
        Sets a comment at the specified address.

        Args:
            ea: The effective address.
            comment: The comment text to assign.

        Returns:
            True if the comment was successfully set, false otherwise.
        """
        if not self.m_database.is_open():
            ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
            return False
        return ida_bytes.set_cmt(ea, comment, False)

    def get_all(self, include_repeatable: bool) -> "Iterator":
        """
        Creates an iterator for all comments in the database.

        Args:
            include_repeatable: Whether to include repeatable comments during iteration.

        Returns:
            A CommentsIterator instance.
        """
        return self.Iterator(self.m_database, include_repeatable)
