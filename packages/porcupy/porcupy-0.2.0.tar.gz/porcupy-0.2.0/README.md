# Porcupy: Crested Porcupine Optimizer

![CPO](https://github.com/user-attachments/assets/af843836-1338-4609-bec9-09ea15852294)

[![PyPI version](https://img.shields.io/pypi/v/porcupy.svg)](https://pypi.org/project/porcupy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![codecov](https://codecov.io/gh/SammanSarkar/Porcupy/graph/badge.svg?token=W0VM41CPL2)](https://codecov.io/gh/SammanSarkar/Porcupy)
[![PyPI Downloads](https://static.pepy.tech/badge/porcupy)](https://pepy.tech/projects/porcupy)

## Overview

Porcupy implements the Crested Porcupine Optimizer (CPO), a nature-inspired metaheuristic that mimics porcupine defense mechanisms for optimization. It offers both object-oriented and procedural interfaces with comprehensive testing and documentation.

## Installation

```bash
pip install porcupy
```

## Quick Start

```python
from porcupy import CPO
from porcupy.functions import sphere

# Define search space
dim = 10
bounds = [(-5.12, 5.12)] * dim

# Initialize and run optimizer
optimizer = CPO(dimensions=dim, bounds=bounds, max_iter=100)
best_solution, best_fitness, _ = optimizer.optimize(sphere)

print(f"Best solution: {best_solution}")
print(f"Fitness: {best_fitness}")
```

## Features

- **Multiple Interfaces**: Object-oriented (`CPO` class) and procedural (`cpo` function)
- **GPU Acceleration**: Optional CUDA support for large-scale problems
- **Visualization**: Built-in plotting for 2D/3D optimization landscapes
- **Benchmark Functions**: 20+ test functions included
- **Population Management**: Adaptive population sizing and reduction strategies

## GPU Support

For GPU acceleration, install with CUDA support:

```bash
pip install "porcupy[cuda]"
# Or for specific CUDA version
# pip install "porcupy[cuda]" cupy-cuda11x
```

Example usage:

```python
from porcupy import GPUCPO

optimizer = GPUCPO(dimensions=30, bounds=([-5.12]*30, [5.12]*30))
best_pos, best_cost, _ = optimizer.optimize(sphere)
```

## Documentation

Full documentation is available at [https://porcupy-cpo.readthedocs.io](https://porcupy-cpo.readthedocs.io).

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
  - Contour and surface plots
  - Real-time population tracking
  - Defense mechanism visualization
- **Convergence Analysis**
  - Cost vs iteration plots
  - Population diversity metrics
- **Export Options**
  - Save as GIF/MP4/PNG/PDF
  - Customizable figure sizes

### Benchmark Functions
- **Unimodal functions**: Sphere, Rosenbrock, Schwefel 2.22, Schwefel 1.2, Schwefel 2.21, Step, Quartic
- **Multimodal functions**: Rastrigin, Ackley, Griewank, Schwefel, Michalewicz
- **Function utilities**: Easy access to function bounds and optima

### Testing and Documentation
- **Comprehensive test suite** with high code coverage
- **API Reference** with detailed docstrings
- **User Guide** with examples and tutorials
- **Interactive examples** for quick start

## Installation

```bash
pip install porcupy
```

For visualization support, install with the plotting extras:

```bash
pip install porcupy[plotting]
```

For development, install with the dev extras:

```bash
pip install porcupy[dev]
```

## Quick Start

### Object-Oriented Interface

```python
import numpy as np
from porcupy import CPO
from porcupy.functions import sphere, get_function_bounds
from porcupy.utils.visualization_manager import CPOVisualizer

# Define the problem
dimensions = 2  # Using 2D for visualization
lb = [-5.12] * dimensions  # Lower bounds for sphere function
ub = [5.12] * dimensions   # Upper bounds for sphere function
bounds = (np.array(lb), np.array(ub))

# Create the optimizer with custom options
optimizer = CPO(
    dimensions=dimensions,
    bounds=bounds,
    pop_size=30,
    max_iter=100,
    options={
        'reduction_strategy': 'cosine',  # Population reduction strategy
        'min_pop_size': 10,              # Minimum population size
        'parallel': True,                # Enable parallel processing
        'defense_weights': [0.3, 0.3, 0.2, 0.2]  # Custom defense mechanism weights
    },
    ftol=1e-6,  # Convergence tolerance
    ftol_iter=5  # Number of iterations for convergence check
)

# Run the optimization with progress tracking
best_pos, best_cost, cost_history = optimizer.optimize(
    objective_func=sphere,
    verbose=True,
    track_history=True  # Enable history tracking for visualization
)

print(f"Best position: {best_pos}")
print(f"Best cost: {best_cost}")

# Create visualizer
visualizer = CPOVisualizer(objective_func=sphere, bounds=bounds)

# Visualize the optimization process
if dimensions == 2:
    # Create animation of the optimization process
    visualizer.animate_optimization(
        position_history=optimizer.positions_history,
        best_pos_history=optimizer.best_positions_history,
        save_path='optimization_animation.gif'
    )
    
    # Show convergence plot
    visualizer.plot_convergence(cost_history)
    
    # Show search space with final positions
    visualizer.plot_search_space(positions=optimizer.positions, best_pos=best_pos)
```

### Procedural Interface

```python
import numpy as np
from porcupy.cpo import cpo
from porcupy.functions import rastrigin
from porcupy.utils.visualization_manager import CPOVisualizer

# Define the problem
dimensions = 2  # Using 2D for visualization
lb = [-5.12] * dimensions  # Lower bounds for Rastrigin function
ub = [5.12] * dimensions   # Upper bounds for Rastrigin function

# Run the optimization with default parameters
best_pos, best_cost, cost_history = cpo(
    objective_func=rastrigin,
    lb=lb,
    ub=ub,
    pop_size=30,
    max_iter=100,
    verbose=True,
    track_history=True  # Enable history tracking for visualization
)

print(f"Best position: {best_pos}")
print(f"Best cost: {best_cost}")

# Create visualizer
visualizer = CPOVisualizer(objective_func=rastrigin, bounds=(np.array(lb), np.array(ub)))

# Visualize the optimization process
if dimensions == 2:
    # Create animation of the optimization process
    visualizer.animate_optimization(
        position_history=optimizer.positions_history,
        best_pos_history=optimizer.best_positions_history,
        save_path='rastrigin_optimization.gif'
    )
    
    # Show convergence plot
    visualizer.plot_convergence(cost_history)
    
    # Show search space with final positions
    visualizer.plot_search_space(positions=optimizer.positions, best_pos=best_pos)
```

## Documentation

Porcupy comes with comprehensive documentation to help you get started and make the most of the library:

- [**User Guide**](docs/user_guide.md): A step-by-step guide to using Porcupy, including installation, basic usage, advanced features, and examples.
- [**API Reference**](docs/api_reference.md): Detailed documentation of all classes, methods, and functions in the library.
- [**Examples**](examples/): A collection of example scripts demonstrating various features of the library.

The documentation covers:

- Core optimization algorithms and their parameters
- Population management strategies
- Visualization tools and techniques
- Benchmark functions and their characteristics
- Advanced usage patterns and customization options

## Algorithm

The Crested Porcupine Optimizer (CPO) algorithm is inspired by the defensive behaviors of crested porcupines, which use four distinct mechanisms to protect themselves from predators:

1. **Sight Defense**: An exploration mechanism that simulates how porcupines use visual cues to detect threats from a distance. This mechanism helps the algorithm explore new regions of the search space by moving search agents toward random positions.

2. **Sound Defense**: Another exploration mechanism that mimics how porcupines use auditory signals to warn others of danger. This mechanism enhances exploration by moving search agents toward positions that combine information from multiple sources.

3. **Odor Defense**: An exploitation mechanism inspired by how porcupines use olfactory signals to communicate. This mechanism focuses on refining solutions by moving search agents toward the current best position with controlled randomness.

4. **Physical Attack**: The most aggressive exploitation mechanism, representing the porcupine's quill defense. This mechanism intensifies local search around promising solutions by moving search agents directly toward the best position with minimal randomness.

What makes CPO unique is its cyclic population reduction strategy, which periodically reduces the population size to focus computational resources on the most promising solutions. This strategy helps balance exploration and exploitation throughout the optimization process, leading to faster convergence and better solutions for complex problems.

The algorithm dynamically adjusts the influence of each defense mechanism based on the current iteration, gradually shifting from exploration-focused strategies (sight and sound) to exploitation-focused strategies (odor and physical attack) as the optimization progresses.

## Citing

If you use Porcupy in your research, please cite the original paper:

```
@article{article,
author = {Abdel-Basset, Mohamed and Mohamed, Reda and Abouhawwash, Mohamed},
year = {2023},
month = {12},
pages = {111257},
title = {Crested Porcupine Optimizer: A new nature-inspired metaheuristic},
volume = {284},
journal = {Knowledge-Based Systems},
doi = {10.1016/j.knosys.2023.111257}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Development and Testing

### Setting Up the Development Environment

To set up the development environment for contributing to Porcupy:

```bash
# Clone the repository
git clone https://github.com/SammanSarkar/Porcupy.git
cd Porcupy

# Install in development mode with all extras
pip install -e .[all]
```

### Core Components

1. **Optimization Algorithms**
   - `cpo.py`: Main implementation of the Crested Porcupine Optimizer
   - `gpu_cpo.py`: GPU-accelerated version using CuPy
   - `base.py`: Base optimizer class with common functionality

2. **Algorithm Components**
   - `porcupines.py`: Core implementation of porcupine behaviors and population management
   - Defense mechanisms (sight, sound, odor, physical attack)
   - Population management and selection strategies

3. **Benchmark Functions**
   - Built-in test functions for optimization
   - Both unimodal and multimodal functions
   - Easy integration with custom objective functions

4. **Utilities**
   - Visualization tools for optimization progress
   - Parallel processing support
   - Input validation and helper functions

5. **Documentation**
   - User guides and tutorials
   - API reference
   - Example scripts

6. **Tests**
   - Unit tests for all components
   - Integration tests
   - Performance benchmarks


### Running Tests

Porcupy has a comprehensive test suite with over 80% code coverage. To run the tests:

```bash
# Run all tests
python -m pytest tests/

# Run tests for a specific module
python -m pytest tests/test_porcupines.py

# Run tests with verbose output
python -m pytest tests/ -v

# Generate test coverage report
python -m pytest tests/ --cov=porcupy

# Generate detailed HTML coverage report
python -m pytest tests/ --cov=porcupy --cov-report=html
```

> **Note**: Using `python -m pytest` is recommended over just `pytest` as it ensures the current directory is in the Python path, which helps with imports.

### Continuous Integration

The codebase is continuously tested to ensure high quality and reliability. All pull requests must pass the test suite before being merged.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
