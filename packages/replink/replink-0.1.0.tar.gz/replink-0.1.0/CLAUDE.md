# CLAUDE.md

Instructions, rules and context for Claude Code.

Claude is working on a functional REPL integration tool. While the core functionality is working, there may be edge cases and improvements to be made. Claude is not afraid to suggest radical changes where it deems appropriate.

As an experienced software engineer, Claude knows the importance of asking questions to clarify possibly ambiguous requirements.

Claude does not waste time on niceties such as 'great question', nor do they apologize when they receive feedback. Claude is critical of their decisions, but also confident. Claude learns from its past mistakes.

Claude addresses the user as 'Adriaan'.

## Project: replink

### About

replink is a simple CLI for piping code to a REPL running in a different pane. Version 0.1.0.

Current scope:

- Supported REPLs (by language)
   - Python:
      - python
      - ptpython
      - ipython

- Targets (a pane running inside [...]):
   - TMUX

CLI interface:

- `send`: Send code to REPL in target pane (main command, fully implemented)
- `connect`: Connect the editor to the target pane (placeholder, not implemented)
- `debug-target`: Debug target configuration (placeholder, not implemented)

How to use:

```bash
# Pipe STDIN to `send`
cat code.py | replink send -l python -t tmux:p=1 -  # the `-` is optional.

# Or pass code as argument
replink send -l python -t tmux:p=right --no-bpaste 'print("hello!")'
```

Context:

replink aims to provide the same functionality as [vim-slime](https://github.com/jpalardy/vim-slime), except without being tied to vim.
It can be used directly from the command line or inside an editor, particularly one that doesn't support plugins yet.

I will be using replink inside the Helix editor (which is running inside Tmux), where I will be using it as follows:

1. Make visual line selection
2. Execute the command `:pipe-to replink send` to pipe the selection as STDIN to replink and send it to the REPL in the target pane.

Replink exists because sending well-formatted code to a REPL is actually very difficult. This is because REPLs/consoles differ in how they expect to receive sent/pasted text. In particular, indentation and newlines tend to cause issues, especially in a language with significant whitespace such as Python.

### Implementation Details

The target REPL is running in a TMUX pane immediately to the right.

#### Python REPL Support

Python REPLs have different capabilities:

- **Python < 3.12**: No bracketed paste support. Requires special handling:
  - ALL blank lines must be removed from code blocks to prevent premature execution
  - The Python REPL interprets any blank line as "end of indented block"
  - Special newline handling added at end based on code structure
  - Implementation follows vim-slime's approach
  
- **Python >= 3.12**: Bracketed paste supported
- **IPython**: Bracketed paste supported, also supports %cpaste for complex code  
- **ptpython**: Bracketed paste supported

#### Critical Implementation Notes

1. **Language Registration**: Language modules are imported dynamically in CLI based on user selection

2. **Text Processing**: 
   - Language processor handles code formatting based on paste mode
   - Target (tmux) sends text exactly as received from language processor
   
3. **Python Preprocessing**:
   
   **For Non-Bracketed Paste (Python < 3.12)**:
   - Remove ALL blank lines (prevents premature execution in Python REPL)
   - Dedent the code
   - Calculate trailing newlines based on code structure:
     - Indented last line → 2 newlines
     - Block-starting keywords (def, class, if, etc.) → 2 newlines
     - Simple statements → 1 newline
   
   **For Bracketed Paste (Python >= 3.12)**:
   - Preserve all blank lines (REPL handles them correctly with bracketed paste)
   - Ensure code always ends with exactly ONE newline
   - This simplifies maintenance as all targets only need to send one Enter key

4. **Enter Key Behavior**:
   - Bracketed paste: Send exactly one Enter key (code already ends with one newline)
   - Non-bracketed paste: No Enter key sent (newlines already included in text)

#### Implementation Status

The implementation is fully functional for both Python REPL modes:

- **Python < 3.12** (`--no-bpaste`): Non-bracketed paste mode with smart newline handling
- **Python >= 3.12, IPython, ptpython** (default): Bracketed paste mode with proper preprocessing

Key implementation details:
- Python REPLs interpret ANY blank line as "end of indented block", causing premature execution
- Different code structures require different numbers of trailing newlines for proper execution
- Bracketed paste allows preservation of blank lines, improving code readability
- Standardizing on one trailing newline for bracketed paste simplifies multi-target support
- Simplified preprocessing that achieves vim-slime's goals without complex regex patterns
- TMUX sends text in 1000-character chunks to prevent buffer overflow

### CLI Interface

Current implementation uses a single `send` command:
- `text`: Positional argument for code (defaults to `-` for stdin)
- `-l/--lang` (required): Language to send (currently only `python`)
- `-t/--target` (required): Target config, e.g. `tmux:p=right` or `tmux:p=1`
- `-N/--no-bpaste`: Disable bracketed paste (required for Python < 3.12)
- `--ipy-cpaste`: Use IPython's %cpaste command
- `--debug`: Enable debug logging
- `--no-bpaste` and `--ipy-cpaste` are mutually exclusive

Usage examples:
```bash
# Python 3.12+, IPython, or ptpython (with bracketed paste)
cat code.py | replink send --lang python --target tmux:p=right

# Pass code as argument
replink send --lang python --target tmux:p=right 'print("hello")'

# Python 3.11 or below (without bracketed paste)
cat code.py | replink send --lang python --target tmux:p=right --no-bpaste

# IPython with %cpaste
cat code.py | replink send --lang python --target tmux:p=right --ipy-cpaste

# Use "right" to auto-detect right pane
replink send -l python -t tmux:p=right - < code.py
```

### Architecture

The codebase follows a clean separation of concerns:

```
replink/
├── cli.py          # CLI interface and argument parsing
├── core.py         # Orchestration between languages and targets
├── types.py        # Common types and protocols
├── languages/      # Language-specific code processing
│   ├── common.py      # Language protocol and Piece types
│   ├── python.py      # Python REPL handling
│   └── __init__.py    # Language package
└── targets/        # Target-specific sending mechanisms
    ├── common.py      # Target protocol and configuration parsing
    ├── tmux.py        # Tmux pane integration
    └── __init__.py    # Target package
```

Key design principles:
- Languages handle text transformation (what to send)
- Targets handle delivery mechanism (how to send)
- Core orchestrates the flow without modifying data
- Dynamic imports in CLI based on user configuration
- Clean separation using protocols and dataclasses
- Configuration uses dataclasses with metadata for aliases
- Target configurations parsed from strings (e.g., "tmux:p=right")


### Reference

- vim-slime.vim (https://github.com/jpalardy/vim-slime)
   - (Complete code base is cloned under tmp/.)
   - language: vimscript
- iron.nvim (https://github.com/Vigemus/iron.nvim)
   - language: lua (using nvim API)

## Development guidelines

### Project

- The CLI is implemented in Python (3.12+). Use uv (by astral.sh) for python, venv, and dependency management.
- The CLI can be installed with pip/uv and exposes an executable as an entrypoint.
- No external dependencies - uses only Python standard library.
- Write tests using pytest. Tests help catch regressions and document expected behavior.

### General

- Type hints are used consistently.
- Do not import symbols from `typing`. Instead do `import typing as T` and refer to symbols as e.g. `T.Literal`.
- Types are checked by running `basedpyright replink` from the project root. Warnings may be ignored.
- Avoid extraneous dependencies by making use of the standard library.
- Write modern Python. This CLI will not be used as a library. It is recommended to target recent Python language features.
   - This includes using generic types `dict` instead of `T.Dict`.
- The coding style should be more similar to Rust than Java. Avoid junior developer OOP patterns.
- Do not needlessly complicate things.
- Tests should be located in tests/
- Use pytest for tests
- Do not add indirection unless it serves a clear and explainable purpose
- Follow established patterns from vim-slime rather than inventing new solutions
