"""Tests for the FireTuner TCP client."""

import struct
from unittest.mock import MagicMock, patch

import pytest

from civ6_bridge.constants import TUNER_MSG_TYPE
from civ6_bridge.exceptions import TunerCommandError, TunerConnectionError
from civ6_bridge.tuner_client import TunerClient, build_message, parse_response


class TestBuildMessage:
    def test_default_context(self):
        msg = build_message("print('hi')")
        payload = b"CMD:0:print('hi')\x00"
        expected_header = struct.pack("<II", len(payload), TUNER_MSG_TYPE)
        assert msg == expected_header + payload

    def test_custom_context(self):
        msg = build_message("x()", context=2)
        payload = b"CMD:2:x()\x00"
        expected_header = struct.pack("<II", len(payload), TUNER_MSG_TYPE)
        assert msg == expected_header + payload

    def test_header_is_8_bytes(self):
        msg = build_message("a()")
        assert len(msg[:8]) == 8

    def test_payload_length_field(self):
        lua = "Game.AgentPing()"
        msg = build_message(lua)
        length_field = struct.unpack("<I", msg[:4])[0]
        expected_payload = f"CMD:0:{lua}\x00".encode()
        assert length_field == len(expected_payload)

    def test_msg_type_field(self):
        msg = build_message("x()")
        msg_type = struct.unpack("<I", msg[4:8])[0]
        assert msg_type == TUNER_MSG_TYPE

    def test_null_terminator(self):
        msg = build_message("foo()")
        assert msg[-1:] == b"\x00"


class TestParseResponse:
    def test_extracts_sentinel_result(self):
        data = b"\x00\x01some junk CIV6BRIDGE_RESULT:PONG:CIV6BRIDGE_END more junk"
        assert parse_response(data) == "PONG"

    def test_extracts_ok_result(self):
        data = b"CIV6BRIDGE_RESULT:OK:move_unit:CIV6BRIDGE_END"
        assert parse_response(data) == "OK:move_unit"

    def test_no_sentinels_returns_text(self):
        data = b"just some plain text"
        result = parse_response(data)
        assert result == "just some plain text"

    def test_error_raises_command_error(self):
        data = b"CIV6BRIDGE_RESULT:ERR:unit not found 99:CIV6BRIDGE_END"
        with pytest.raises(TunerCommandError, match="unit not found 99"):
            parse_response(data)

    def test_strips_non_printable(self):
        data = bytes([0x00, 0x01, 0x7F]) + b"hello"
        result = parse_response(data)
        assert result == "hello"

    def test_empty_response(self):
        assert parse_response(b"") == ""


class TestSendCommand:
    @patch("civ6_bridge.tuner_client.socket.socket")
    def test_send_command_flow(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_sock.recv.side_effect = [b"CIV6BRIDGE_RESULT:PONG:CIV6BRIDGE_END", b""]

        client = TunerClient()
        result = client.send_command("Game.AgentPing()")

        mock_sock.connect.assert_called_once_with(("127.0.0.1", 4318))
        mock_sock.sendall.assert_called_once()
        assert result == "PONG"

    @patch("civ6_bridge.tuner_client.socket.socket")
    def test_connection_refused(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_sock.connect.side_effect = ConnectionRefusedError()

        client = TunerClient()
        with pytest.raises(TunerConnectionError, match="Cannot connect"):
            client.send_command("x()")


class TestIsConnected:
    @patch("civ6_bridge.tuner_client.socket.socket")
    def test_connected(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

        client = TunerClient()
        assert client.is_connected() is True

    @patch("civ6_bridge.tuner_client.socket.socket")
    def test_not_connected(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_sock.connect.side_effect = ConnectionRefusedError()

        client = TunerClient()
        assert client.is_connected() is False
