# Testing Guidelines

## Framework
The project uses `pytest` for all unit and integration tests.

## Running Tests
Always use `uv` to ensure consistency:
```bash
uv run pytest
```

## Writing Tests
- **Location**: Place new tests in the `tests/` directory.
- **Pattern**: Most tests follow the pattern of creating a budget and asserting specific cumulative properties (e.g., gain or noise figure) at the final stage.
- **Example**: [test_oip3.py](tests/test_oip3.py) demonstrates verifying the OIP3 calculation for a cascaded system.

## Validation Data
When adding new features, prefer validating against known textbook examples or commercial tool outputs (e.g., ADIsimRF). Reference the source in a comment.

> [!TIP]
> Use `pytest.approx()` for floating point comparisons to avoid precision issues.
