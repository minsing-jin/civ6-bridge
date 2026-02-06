# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
uv run pytest

# Run a single test file or test
uv run pytest tests/test_models.py
uv run pytest tests/test_log_parser.py::TestExtractFrames::test_single_frame

# Lint and format
uv run ruff check .
uv run ruff format .

# Full QA (format + lint + type check + test)
just qa

# CLI smoke test
uv run civ6_bridge status --log-path tests/fixtures/sample_lua_log.txt

# Build package
uv build
```

## Architecture

This project bridges Civilization VI and Python. Civ6's Lua engine has **no sockets or JSON library**, so communication works through a one-way log file protocol:

```
Lua mod (print → Lua.log)  →  Python SDK (tail + parse)
```

**Lua side** (`civ6_mod/Scripts/`): `event_hooks.lua` subscribes to game events (`PlayerTurnStarted`, `LoadScreenClose`), which call `ExportGameState()` in `game_state.lua`. That function serializes the full game state using a hand-rolled `json.lua` encoder and writes it to `Lua.log` wrapped in sentinel delimiters: `[CIV6BRIDGE_BEGIN_v1]` + JSON + `[CIV6BRIDGE_END_v1]`.

**Python side** (`src/civ6_bridge/`): `log_parser.py` extracts sentinel-delimited frames from raw log text and validates JSON + schema version. `game_state.py` converts parsed dicts into a tree of frozen dataclasses defined in `models.py` (GameState → Player → Treasury/City/Unit/etc). `log_watcher.py` provides file-tailing with truncation detection. `civ6_bridge.py` is the facade class (`Civ6Bridge`) that ties it all together. `cli.py` exposes `status` (one-shot) and `watch` (live tail) commands via Typer.

**Data flow**: `LogWatcher.read_latest()` → `extract_frames()` → `parse_frame()` → `from_dict()` → `GameState`

## Key Conventions

- Python models are **frozen dataclasses** with `slots=True`; collections use `tuple` for immutability
- Schema version is `1` (defined in `constants.py`); `SchemaVersionError` is raised on mismatch
- Ruff config: line-length 120, rules E/W/F/I/B/UP
- Pre-commit hooks: trailing whitespace, end-of-file fixer, ruff lint+format
- Test fixtures live in `tests/fixtures/` (sample JSON and simulated Lua.log)
- Lua files use `include()` (Civ6's module system), not `require()`
