"""
Version information for the IDA Domain API.
"""

import ida_kernwin

class VersionInfo:
    """
    Provides library version information.
    """

    # IDA Domain API major version
    major_version = 0

    # IDA Domain API minor version
    minor_version = 0

    # IDA Domain API patch version
    patch_version = 1

    # IDA Domain API full version string (includes pre-release tags, if any)
    api_version_full = "0.0.1-dev.19"

    # IDA Domain API semantic version string
    api_version = "0.0.1"

    # IDA SDK version string
    @property
    def sdk_version(self) -> str:
        """Get the IDA SDK version string."""
        return str(ida_kernwin.get_kernel_version())

    def __init__(self):
        """Deleted constructor to prevent instantiation."""
        raise NotImplementedError("VersionInfo cannot be instantiated")
