"""FireTuner TCP client for sending Lua commands to Civilization VI."""

from __future__ import annotations

import socket
import struct

from civ6_bridge.constants import RESULT_BEGIN, RESULT_END, TUNER_HOST, TUNER_MSG_TYPE, TUNER_PORT
from civ6_bridge.exceptions import TunerCommandError, TunerConnectionError


def build_message(lua_code: str, context: int = 0) -> bytes:
    """Build a FireTuner wire-protocol message.

    Format: [4-byte LE payload length][4-byte LE message type] + CMD:{context}:{lua_code}\\x00
    """
    payload = f"CMD:{context}:{lua_code}\x00".encode()
    header = struct.pack("<II", len(payload), TUNER_MSG_TYPE)
    return header + payload


def parse_response(data: bytes) -> str:
    """Extract the result string from a FireTuner binary response.

    Looks for printable ASCII, then extracts text between RESULT_BEGIN and RESULT_END sentinels.
    Raises TunerCommandError if the result starts with 'ERR:'.
    """
    # Extract printable ASCII characters from the binary response
    text = "".join(chr(b) for b in data if 32 <= b < 127)

    begin_idx = text.find(RESULT_BEGIN)
    end_idx = text.find(RESULT_END)

    if begin_idx == -1 or end_idx == -1:
        return text

    result = text[begin_idx + len(RESULT_BEGIN) : end_idx]

    if result.startswith("ERR:"):
        raise TunerCommandError(result[4:])

    return result


class TunerClient:
    """Short-lived TCP client for the Civ6 FireTuner debug server."""

    def __init__(self, host: str = TUNER_HOST, port: int = TUNER_PORT, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_command(self, lua_code: str, context: int = 0) -> str:
        """Send a Lua command and return the response.

        Opens a short-lived TCP connection (connect → send → recv → close).
        """
        message = build_message(lua_code, context)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                sock.sendall(message)
                chunks: list[bytes] = []
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                return parse_response(b"".join(chunks))
        except ConnectionRefusedError as e:
            raise TunerConnectionError(f"Cannot connect to FireTuner at {self.host}:{self.port}") from e
        except TimeoutError as e:
            raise TunerConnectionError(f"Connection to FireTuner at {self.host}:{self.port} timed out") from e

    def is_connected(self) -> bool:
        """Check if the FireTuner server is reachable."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                return True
        except (TimeoutError, ConnectionRefusedError, OSError):
            return False
