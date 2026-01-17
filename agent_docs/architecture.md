# Architecture

## Core Concept
The toolbox follows a cascade-based analysis approach. Elements (Amplifiers, Filters, Mixers, etc.) are defined individually and then arranged in a sequence (the budget).

## Data Flow
1. **Element Definition**: Users define components with specific RF parameters (gain, noise figure, IP3).
2. **Budget Creation**: Elements are passed to the `budget()` function along with input conditions (frequency, power, bandwidth).
3. **Solver**: The toolbox uses the Friis formulas to compute cascaded results.
    - See `src/rfbudget/__init__.py` for the `budget` class logic.
4. **Calculations**: Results like Noise Figure, SNR, and Output Power are stored as arrays, representing the cumulative value at each stage of the cascade.

## Key Classes
- `Element`: Base class for all RF components.
- `Amplifier`, `Loss`, `Mixer`: Specialized element types.
- `budget`: Container that performs the analysis and stores results.

## Visualization
Schematic diagrams are generated using `schemdraw`. Most elements have a `.draw()` method to contribute to the overall schematic.
- Example: [test1.py](examples/test1.py) shows how to build and display a budget.
