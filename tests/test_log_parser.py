"""Tests for civ6_bridge.log_parser — frame extraction, validation."""

import json

import pytest

from civ6_bridge.constants import SENTINEL_BEGIN, SENTINEL_END
from civ6_bridge.exceptions import ParseError, SchemaVersionError
from civ6_bridge.log_parser import extract_frames, parse_frame


class TestExtractFrames:
    def test_single_frame(self):
        text = f'junk\n{SENTINEL_BEGIN}\n{{"version":1}}\n{SENTINEL_END}\nmore junk'
        frames = extract_frames(text)
        assert len(frames) == 1
        assert frames[0] == '{"version":1}'

    def test_multiple_frames(self):
        frame1 = f'{SENTINEL_BEGIN}\n{{"version":1,"turn":1}}\n{SENTINEL_END}'
        frame2 = f'{SENTINEL_BEGIN}\n{{"version":1,"turn":2}}\n{SENTINEL_END}'
        text = f"log\n{frame1}\nstuff\n{frame2}\nend"
        frames = extract_frames(text)
        assert len(frames) == 2
        assert '"turn":1' in frames[0]
        assert '"turn":2' in frames[1]

    def test_empty_log(self):
        assert extract_frames("") == []
        assert extract_frames("just some regular log output\nno sentinels here") == []

    def test_truncated_frame(self):
        text = f'{SENTINEL_BEGIN}\n{{"version":1}}\n'  # no END sentinel
        frames = extract_frames(text)
        assert frames == []

    def test_begin_without_payload(self):
        text = f"{SENTINEL_BEGIN}\n{SENTINEL_END}"
        frames = extract_frames(text)
        assert frames == []

    def test_from_fixture(self, sample_lua_log):
        frames = extract_frames(sample_lua_log)
        assert len(frames) == 2
        for raw in frames:
            data = json.loads(raw)
            assert data["version"] == 1


class TestParseFrame:
    def test_valid_frame(self):
        raw = '{"version":1,"turn":42,"players":[]}'
        data = parse_frame(raw)
        assert data["version"] == 1
        assert data["turn"] == 42

    def test_invalid_json(self):
        with pytest.raises(ParseError, match="Invalid JSON"):
            parse_frame("{not valid json}")

    def test_not_an_object(self):
        with pytest.raises(ParseError, match="Expected JSON object"):
            parse_frame("[1, 2, 3]")

    def test_wrong_version(self):
        raw = '{"version":99,"turn":1}'
        with pytest.raises(SchemaVersionError) as exc_info:
            parse_frame(raw)
        assert exc_info.value.expected == 1
        assert exc_info.value.got == 99

    def test_missing_version(self):
        raw = '{"turn":1}'
        with pytest.raises(SchemaVersionError):
            parse_frame(raw)


@pytest.fixture
def sample_lua_log():
    from pathlib import Path

    fixture = Path(__file__).parent / "fixtures" / "sample_lua_log.txt"
    return fixture.read_text()
