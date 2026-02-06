"""Custom exceptions for civ6_bridge."""


class Civ6BridgeError(Exception):
    """Base exception for all civ6_bridge errors."""


class ParseError(Civ6BridgeError):
    """Raised when a JSON frame from Lua.log cannot be parsed."""


class SchemaVersionError(Civ6BridgeError):
    """Raised when the schema version in a frame does not match the expected version."""

    def __init__(self, expected: int, got: int):
        self.expected = expected
        self.got = got
        super().__init__(f"Expected schema version {expected}, got {got}")


class LogNotFoundError(Civ6BridgeError):
    """Raised when the Lua.log file cannot be found."""


class TunerConnectionError(Civ6BridgeError):
    """Raised when a connection to the FireTuner TCP server fails."""


class TunerCommandError(Civ6BridgeError):
    """Raised when a command sent via FireTuner returns an error."""
