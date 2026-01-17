# Mission
`pyrf-budget-toolbox` is a Python library for RF budget analysis, designed for educational clarity, Jupyter-based visualization, and as an open-source alternative to commercial RF tools.

# Critical Commands
- **Install (Dev):** `pip install -e .`
- **Test:** `uv run pytest`
- **Lint:** `ruff check .` (or use your preferred linter)

# Directory Map
- `src/rfbudget/`: Core library logic.
- `src/rfbudget/__init__.py`: Primary entry point and class definitions.
- `tests/`: Unit tests for RF calculations.
- `examples/`: Reference implementations and Jupyter notebooks.

# Documentation Index
Read these files in `agent_docs/` for deep-context:
- [architecture.md](agent_docs/architecture.md): Data flow and object model.
- [testing_guidelines.md](agent_docs/testing_guidelines.md): How to verify calculations.
- [conventions.md](agent_docs/conventions.md): Code style and logic patterns.

> [!IMPORTANT]
> ALWAYS verify calculations using `uv run pytest` before finalizing changes.
