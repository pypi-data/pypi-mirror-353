Examples
========

This section provides practical examples of using the IDA Domain API for common reverse engineering tasks.

Basic Database Operations
-------------------------

Opening and Exploring a Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ida_domain import Database

   def explore_database(db_path):
       db = Database()
       if not db.open(db_path):
           print(f"Failed to open database: {db_path}")
           return

       try:
           # Get basic information
           print(f"Entry point: {hex(db.entry_point())}")
           print(f"Address range: {hex(db.minimum_ea())} - {hex(db.maximum_ea())}")

           # Get metadata
           metadata = db.metadata()
           print("Database metadata:")
           for key, value in metadata.items():
               print(f"  {key}: {value}")

           # Count functions
           function_count = 0
           for _ in db.functions.get_all():
               function_count += 1
           print(f"Total functions: {function_count}")

       finally:
           db.close(save=False)

Function Analysis
-----------------

Finding and Analyzing Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ida_domain import Database

   def analyze_functions(db_path, pattern="main"):
       db = Database()
       if not db.open(db_path):
           return

       try:
           functions = db.functions

           # Find functions matching a pattern
           matching_functions = []
           for func in functions.get_all():
               name = functions.get_name(func)
               if pattern.lower() in name.lower():
                   matching_functions.append((func, name))

           print(f"Found {len(matching_functions)} functions matching '{pattern}':")

           for func, name in matching_functions:
               print(f"\nFunction: {name}")
               print(f"Address: {hex(func.start_ea)} - {hex(func.end_ea)}")

               # Get signature
               signature = functions.get_signature(func)
               print(f"Signature: {signature}")

               # Get basic blocks
               bb_count = 0
               for _ in functions.get_basic_blocks(func):
                   bb_count += 1
               print(f"Basic blocks: {bb_count}")

               # Show first few lines of disassembly
               disasm = functions.get_disassembly(func)
               print("Disassembly (first 5 lines):")
               for line in disasm[:5]:
                   print(f"  {line}")

       finally:
           db.close(save=False)

String Analysis
---------------

Finding and Analyzing Strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ida_domain import Database

   def analyze_strings(db_path, min_length=5):
       db = Database()
       if not db.open(db_path):
           return

       try:
           strings = db.strings

           print(f"Analyzing strings (minimum length: {min_length}):")

           string_count = 0
           for addr, string_value in strings.get_all():
               if len(string_value) >= min_length:
                   print(f"{hex(addr)}: {repr(string_value)}")
                   string_count += 1

                   if string_count >= 20:  # Limit output
                       print("... (showing first 20 strings)")
                       break

           print(f"Total strings found: {strings.get_count()}")

       finally:
           db.close(save=False)

Cross-Reference Analysis
------------------------

Analyzing Cross-References
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ida_domain import Database

   def analyze_xrefs(db_path, target_addr):
       db = Database()
       if not db.open(db_path):
           return

       try:
           xrefs = db.xrefs

           print(f"Cross-references to {hex(target_addr)}:")

           # Get references TO the target address
           xref_count = 0
           for success, xref in xrefs.get_to(target_addr):
               if success:
                   print(f"  From {hex(xref.frm)} to {hex(xref.to)} (type: {xref.type})")
                   xref_count += 1

           if xref_count == 0:
               print("  No cross-references found")
           else:
               print(f"  Total: {xref_count} references")

           print(f"\nCross-references from {hex(target_addr)}:")

           # Get references FROM the target address
           xref_count = 0
           for success, xref in xrefs.get_from(target_addr):
               if success:
                   print(f"  From {hex(xref.frm)} to {hex(xref.to)} (type: {xref.type})")
                   xref_count += 1

           if xref_count == 0:
               print("  No outgoing references found")
           else:
               print(f"  Total: {xref_count} outgoing references")

       finally:
           db.close(save=False)

Complete Analysis Example
-------------------------

Comprehensive Binary Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates a complete analysis workflow:

.. code-block:: python

   from ida_domain import Database

   def comprehensive_analysis(db_path):
       """Perform comprehensive analysis of a binary."""
       db = Database()
       if not db.open(db_path):
           print(f"Failed to open: {db_path}")
           return

       try:
           print("=== IDA Domain API - Comprehensive Analysis ===\n")

           # Basic information
           print("1. Basic Information:")
           print(f"   Entry point: {hex(db.entry_point())}")
           print(f"   Address range: {hex(db.minimum_ea())} - {hex(db.maximum_ea())}")

           # Segments
           print("\n2. Segments:")
           segments = db.segments
           for segment in segments.get_all():
               if segment:
                   name = segments.get_name(segment)
                   print(f"   {name}: {hex(segment.start_ea)} - {hex(segment.end_ea)}")

           # Functions summary
           print("\n3. Functions Summary:")
           functions = db.functions
           func_count = 0
           named_funcs = 0

           for func in functions.get_all():
               func_count += 1
               name = functions.get_name(func)
               if not name.startswith("sub_"):
                   named_funcs += 1

           print(f"   Total functions: {func_count}")
           print(f"   Named functions: {named_funcs}")
           print(f"   Unnamed functions: {func_count - named_funcs}")

           # Strings summary
           print("\n4. Strings Summary:")
           strings = db.strings
           total_strings = strings.get_count()
           print(f"   Total strings: {total_strings}")

           # Show interesting strings
           interesting_strings = []
           for addr, string_value in strings.get_all():
               lower_str = string_value.lower()
               if any(keyword in lower_str for keyword in ['password', 'key', 'secret', 'token', 'api']):
                   interesting_strings.append((addr, string_value))

           if interesting_strings:
               print("   Interesting strings found:")
               for addr, string_value in interesting_strings[:5]:
                   print(f"     {hex(addr)}: {repr(string_value)}")

           # Comments summary
           print("\n5. Comments Summary:")
           comments = db.comments
           comment_count = 0
           for addr, comment in comments.get_all(include_repeatable=True):
               comment_count += 1
           print(f"   Total comments: {comment_count}")

           print("\n=== Analysis Complete ===")

       finally:
           db.close(save=False)

   # Usage example
   if __name__ == "__main__":
       # Replace with your binary path
       binary_path = "/path/to/your/binary.exe"
       comprehensive_analysis(binary_path)

Running the Examples
--------------------

To run these examples, save them to Python files and execute them with your IDA database path:

.. code-block:: bash

   python example_script.py

Make sure you have:

1. Set the ``IDADIR`` environment variable
2. Installed the ida-domain package
3. A valid IDA database file to analyze

.. note::
   These examples assume you have a valid IDA database file. The examples will work with any supported binary format that IDA can analyze.
