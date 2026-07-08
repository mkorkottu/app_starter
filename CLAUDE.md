# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python package implementing document-related tools (conversion, processing), exposed through an MCP server (`main.py`) for use by AI assistants. Built with `uv` and the `mcp[cli]` SDK's `FastMCP`.

## Commands

```bash
# Create/activate the virtual env (already exists in this repo; only needed once)
uv venv
source .venv/bin/activate

# Install the package in editable/development mode (run after adding/changing dependencies)
uv pip install -e .

# Start the MCP server (stdio transport — runs persistently, doesn't exit on its own)
uv run main.py

# Run all tests
uv run pytest

# Run a single test file / test
uv run pytest tests/test_document.py
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_docx
```

## Architecture

- `main.py` creates the `FastMCP("docs")` server instance and registers tools onto it via `mcp.tool()(function)`. This is the single wiring point — a function existing in `tools/` does **not** make it available to MCP clients; it must be explicitly registered here. Currently only `add` (from `tools/math.py`) is registered — `tools/document.py`'s `binary_document_to_markdown` is implemented and tested but not yet registered as an MCP tool.
- `tools/` contains the actual tool implementations as plain Python functions, grouped by domain (`math.py`, `document.py`). Each function is the single source of truth for both its logic and its MCP-facing schema/description (see below) — there is no separate registration/schema layer.
- `tools/document.py` wraps the `markitdown` library to convert binary document data (docx, pdf, etc.) to markdown text, via `MarkItDown().convert()` on an in-memory `BytesIO` stream with an explicit `StreamInfo(extension=file_type)`.
- Tests in `tests/` exercise the `tools/` functions directly (not through the MCP server), using binary fixture files in `tests/fixtures/` (`mcp_docs.docx`, `mcp_docs.pdf`).

## Defining new MCP tools

Tool functions doubles as the MCP tool contract: its signature, `Field` descriptions, and docstring together become what the MCP client (and the LLM driving it) sees, so they must be complete and precise, not just adequate Python documentation.

1. Implement the function in the appropriate `tools/*.py` module (create a new module per domain if none fits).
2. Type-annotate every parameter and the return value.
3. Give each parameter a `pydantic.Field(description=...)` default that explains what it does — this is what the calling LLM reads to know how to fill it in:

   ```python
   from pydantic import Field

   def my_tool(
       param1: str = Field(description="Detailed description of this parameter"),
       param2: int = Field(description="Explain what this parameter does"),
   ) -> ReturnType:
       """Comprehensive docstring here"""
       ...
   ```

4. Write the docstring to:
   - Begin with a one-line summary.
   - Provide a detailed explanation of functionality.
   - Explain when to use (and not use) the tool.
   - Include usage examples with expected input/output.
5. Register the function in `main.py`: `mcp.tool()(my_function)`.
6. Add tests under `tests/` that call the function directly (see `tests/test_document.py` for the pattern of using binary fixtures from `tests/fixtures/`).
