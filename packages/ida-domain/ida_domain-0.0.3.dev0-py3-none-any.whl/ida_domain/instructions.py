from typing import Tuple, TYPE_CHECKING
import inspect
import ida_ua
import ida_bytes
import ida_lines
import ida_kernwin
import ida_idaapi

if TYPE_CHECKING:
    from .database import Database


class Instructions:
    """
    Provides access to instruction-related operations.
    """

    class Iterator:
        """Iterator for instructions within a specified address range."""

        def __init__(self, database: "Database", start_ea: int, end_ea: int):
            """
            Constructs an instructions iterator for the specified range.

            Args:
                database: Reference to the active IDA database.
                start_ea: Start address of the range.
                end_ea: End address of the range.
            """
            self.m_database = database
            self.m_start_ea = start_ea
            self.m_end_ea = end_ea
            self.m_current_ea = ida_idaapi.BADADDR  # BADADDR equivalent

        def get_first(self) -> Tuple[bool, object]:
            """
            Retrieves the first instruction in the range.

            Returns:
                A pair <bool, insn_t>. If decoding fails, the bool is false.
            """
            if not self.m_database.is_open():
                ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
                return (False, ida_ua.insn_t())

            self.m_current_ea = self.m_start_ea
            return self.get_next()

        def __iter__(self):
            """Python iterator protocol - matches SWIG extension."""
            success, insn = self.get_first()
            while success:
                yield insn
                success, insn = self.get_next()

        def get_next(self) -> Tuple[bool, object]:
            """
            Retrieves the next instruction in the range.

            Returns:
                A pair <bool, insn_t>. If decoding fails, the bool is false.
            """
            if not self.m_database.is_open():
                ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
                return (False, ida_ua.insn_t())

            while self.m_current_ea < self.m_end_ea:
                insn = ida_ua.insn_t()
                if ida_ua.decode_insn(insn, self.m_current_ea) > 0:
                    # Move to next instruction for next call
                    next_ea = ida_bytes.next_head(self.m_current_ea, self.m_end_ea)
                    self.m_current_ea = next_ea
                    return (True, insn)

                self.m_current_ea = ida_bytes.next_head(self.m_current_ea, self.m_end_ea)

            return (False, ida_ua.insn_t())

    def __init__(self, database: "Database"):
        """
        Constructs an instructions handler for the given database.

        Args:
            database: Reference to the active IDA database.
        """
        self.m_database = database

    def is_valid(self, insn: object) -> bool:
        """
        Checks if the given instruction is valid.

        Args:
            insn: The instruction to validate.

        Returns:
            `true` if the instruction is valid, `false` otherwise.
        """
        if not self.m_database.is_open():
            ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
            return False

        if insn is None:
            return False

        # Check if instruction has valid itype (instruction type)
        try:
            return hasattr(insn, 'itype') and insn.itype != 0
        except:
            return False

    def decode(self, ea: int) -> Tuple[bool, object]:
        """
        Decodes the instruction at the specified address.

        Args:
            ea: The effective address of the instruction.

        Returns:
            A pair <bool, insn_t>. The bool indicates success; if false, the instruction is invalid.
        """
        if not self.m_database.is_open():
            ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
            return (False, ida_ua.insn_t())

        insn = ida_ua.insn_t()
        ret = ida_ua.decode_insn(insn, ea) > 0
        return (ret, insn)

    def get_disassembly(self, insn: object) -> Tuple[bool, str]:
        """
        Retrieves the disassembled string representation of the given instruction.

        Args:
            insn: The instruction to disassemble.

        Returns:
            A pair <bool, string>. If disassembly fails, the bool is false.
        """
        if not self.m_database.is_open():
            ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Database is not loaded. Please open a database first.")
            return (False, "")

        if not self.is_valid(insn):
            return (False, "")

        try:
            # Generate disassembly line
            line = ida_lines.generate_disasm_line(insn.ea, ida_lines.GENDSM_MULTI_LINE | ida_lines.GENDSM_REMOVE_TAGS)
            if line:
                return (True, line)
            else:
                ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Failed to generate disasm line for address 0x{insn.ea:x}")
                return (False, "")
        except:
            ida_kernwin.warning(f"{inspect.currentframe().f_code.co_name}: Failed to generate disasm line for address 0x{insn.ea:x}")
            return (False, "")

    def get_between(self, start: int, end: int) -> "Iterator":
        """
        Retrieves instructions between the specified addresses.

        Args:
            start: Start of the address range.
            end: End of the address range.

        Returns:
            An instruction iterator.
        """
        return self.Iterator(self.m_database, start, end)
