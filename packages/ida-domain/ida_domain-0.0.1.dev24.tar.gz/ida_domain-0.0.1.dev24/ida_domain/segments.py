from typing import Optional, TYPE_CHECKING
import ida_segment

if TYPE_CHECKING:
    from .database import Database


class Segments:
    """
    Provides access to segment-related operations in the IDA database.
    """

    class Iterator:
        """Iterator for segments in the IDA database."""

        def __init__(self, database: "Database"):
            """
            Constructs a segments iterator for the given database.

            Args:
                database: Reference to the active IDA database.
            """
            self.m_database = database
            self.m_current_ea = 0
            self.current_index = 0

        def get_first(self) -> Optional[object]:
            """
            Retrieves the first segment in the database.

            Returns:
                A pointer to the first segment, or None if none exist.
            """
            self.current_index = 0
            self.m_current_ea = 0
            if ida_segment.get_segm_qty() > 0:
                seg = ida_segment.getnseg(0)
                if seg:
                    self.m_current_ea = seg.start_ea
                return seg
            return None

        def __iter__(self):
            """Python iterator protocol - matches SWIG extension."""
            seg = self.get_first()
            while seg:
                yield seg
                seg = self.get_next()

        def get_next(self) -> Optional[object]:
            """
            Retrieves the next segment in the database.

            Returns:
                A pointer to the next segment, or None if no more segments are available.
            """
            self.current_index += 1
            if self.current_index < ida_segment.get_segm_qty():
                seg = ida_segment.getnseg(self.current_index)
                if seg:
                    self.m_current_ea = seg.start_ea
                return seg
            return None

    def __init__(self, database: "Database"):
        """
        Constructs a segments handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def get_at(self, ea: int) -> Optional[object]:
        """
        Retrieves the segment that contains the given address.

        Args:
            ea: The effective address to search.

        Returns:
            A pointer to the containing segment, or None if none found.
        """
        return ida_segment.getseg(ea)

    def get_name(self, segment: object) -> str:
        """
        Retrieves the name of the given segment.

        Args:
            segment: Pointer to the segment.

        Returns:
            The segment name as a string, or an empty string if unavailable.
        """
        if segment is None:
            return ""
        return ida_segment.get_segm_name(segment)

    def set_name(self, segment: object, name: str) -> bool:
        """
        Renames a segment.

        Args:
            segment: Pointer to the segment to rename.
            name: The new name to assign to the segment.

        Returns:
            True if the rename operation succeeded, false otherwise.
        """
        if segment is None:
            return False
        return ida_segment.set_segm_name(segment, name)

    def get_all(self) -> "Iterator":
        """
        Retrieves an iterator over all segments in the database.

        Returns:
            A SegmentsIterator instance.
        """
        return self.Iterator(self.m_database)

    # Additional Python-friendly properties
    def get_label(self, segment: object) -> str:
        """Alias for get_name to match SWIG extension pattern."""
        return self.get_name(segment)