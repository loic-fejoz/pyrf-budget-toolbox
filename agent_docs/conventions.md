# Conventions

## Naming
- **Classes**: PascalCase (e.g., `Amplifier`, `Loss`).
- **Functions/Variables**: snake_case (e.g., `input_freq`, `budget()`).
## Units & Physical Quantities

### Internal Standards
The library logic internally uses the following standard units:
- **Frequency**: Hertz (Hz)
- **Distance**: Meters (m)
- **Angles**: Degrees (°)
- **Power**: Decibel-milliwatts (dBm) or Linear Watts (context dependent)
- **Ratios/Gain**: Decibels (dB)

### Unit Tagging
We use `typing.NewType` for explicit unit declaration. This provides better IDE support and serves as a "tag" for the user.
- `Hz`, `dB`, `dBm`, `m`, `deg`, `kelvin` are available tags.

### SI Prefixes & Helpers
Use the provided helper functions to declare units. They convert to internal standards where necessary:
- `MHz(144)` -> Returns `144,000,000.0` (tagged as `Hz`).
- `km(10)` -> Returns `10,000.0` (tagged as `m`).
- `dB(10)` -> Returns `10.0` (tagged as `dB`).
- `degree(45)` -> Returns `45.0` (tagged as `deg`).

> [!IMPORTANT]
> Always use these helpers when passing values to `Budget` or `Element` constructors to ensure unit consistency.

## Code Style
Follow PEP 8. Use `ruff check .` to verify compliance.
Avoid complex inheritance; favor composition by adding elements to a budget.
