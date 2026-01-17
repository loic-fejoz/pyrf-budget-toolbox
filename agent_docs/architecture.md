## Modular Structure
The codebase is organized into several focused modules to ensure maintainability and separation of concerns:

- `src/rfbudget/core.py`: Contains the `Element` base class and the `Budget` solver logic.
- `src/rfbudget/elements.py`: Implementation of standard RF components (`Amplifier`, `Loss`, `Modulator`, `Filter`).
- `src/rfbudget/propagation.py`: Specialized `PathLoss` models (Free Space, Okumura-Hata, Radar).
- `src/rfbudget/physics.py`: Orbital mechanics and slant range calculation logic.
- `src/rfbudget/utils.py`: Unit types (`NewType`), conversion helpers, and physical constants.
- `src/rfbudget/visualizer.py`: Consolidated logic for `schemdraw` generation.

The public API is re-exported in `src/rfbudget/__init__.py` for backward compatibility.

## Data Flow
1. **Element Definition**: Users define components using classes from `elements.py` or `propagation.py`.
2. **Budget Creation**: Elements are passed to the `Budget` class (defined in `core.py`).
3. **Solver**: The `Budget.update()` method computes cascaded results using Friis formulas.
4. **Calculations**: Results (Noise Figure, SNR, Power) are arrays representing cumulative values at each cascade stage.

## Visualization
Visualization is decoupled from the core logic. While `Element` and `Budget` classes have `.schemdraw()` methods for convenience, the actual rendering logic resides in `visualizer.py`.
- **Schematics**: Generated via `schemdraw`.
- **Interactive**: `Budget.display()` renders HTML tables for Jupyter/IPython.
- Example: [test1.py](examples/test1.py) shows how to build and display a budget.
