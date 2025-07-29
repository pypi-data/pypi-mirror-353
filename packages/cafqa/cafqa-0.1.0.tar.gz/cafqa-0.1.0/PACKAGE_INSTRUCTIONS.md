# CAFQA Package Build and Publish Instructions

## Overview

The CAFQA repository has been restructured as a proper Python package that can be built and published using `uv`.

## Package Structure

```
cafqa/
├── cafqa/                    # Main package directory
│   ├── __init__.py          # Package initialization and public API
│   ├── vqe_helpers.py       # Core VQE functionality
│   ├── circuit_manipulation.py  # Circuit transformation utilities
│   ├── vqe_experiment.py    # High-level experiment functions
│   └── main.py              # CLI entry point (currently unused)
├── examples/                # Example notebooks and data
├── pyproject.toml          # Package configuration
├── README.md               # Project documentation
└── dist/                   # Built packages (after building)
```

## Building the Package

To build the package distributions (wheel and source):

```bash
uv build
```

This creates:
- `dist/cafqa-0.1.0-py3-none-any.whl` (wheel distribution)
- `dist/cafqa-0.1.0.tar.gz` (source distribution)

## Testing the Package

Test that the package can be imported and used:

```bash
# Test basic import
uv run --with ./dist/cafqa-0.1.0-py3-none-any.whl --no-project -- python -c "import cafqa; print('Import successful!')"

# Test basic functionality
uv run --with ./dist/cafqa-0.1.0-py3-none-any.whl --no-project -- python -c "
import cafqa
coeffs, paulis, hf_state = cafqa.ising_model(3, 1.0, 0.5)
print('Ising model created:', len(paulis), 'terms')
"
```

## Package Dependencies

### Core Dependencies
- qiskit==1.2.1
- qiskit-aer>=0.17.1
- qiskit-nature>=0.7.2
- stim>=1.15.0
- numpy, scipy (via qiskit)
- pyscf>=2.9.0
- scikit-quant>=0.8.2

### Optional Dependencies
- hypermapper (for CAFQA optimization, install with `pip install cafqa[cafqa]`)

## Publishing the Package

### To PyPI (public)

1. Get a PyPI account and API token
2. Set the token:
   ```bash
   export UV_PUBLISH_TOKEN="your-pypi-token"
   ```
3. Publish:
   ```bash
   uv publish
   ```

### To Test PyPI (recommended first)

1. Get a Test PyPI account and token
2. Publish to test:
   ```bash
   uv publish --publish-url https://test.pypi.org/legacy/ --token your-test-token
   ```

### To a Private Index

```bash
uv publish --publish-url https://your-private-index.com/simple/ --username your-user --password your-pass
```

## Usage Examples

After installation (`pip install cafqa`), you can use:

```python
import cafqa

# Create an Ising model Hamiltonian
coeffs, paulis, initial_state = cafqa.ising_model(n_qubits=4, Jx=1.0, h=0.5)

# Create a molecule Hamiltonian
coeffs, paulis, hf_state = cafqa.molecule("H 0 0 0; H 0 0 0.74")

# Run VQE optimization
energy, params = cafqa.run_vqe(
    n_qubits=4,
    coeffs=coeffs,
    paulis=paulis,
    param_guess=[],
    budget=100,
    shots=1000,
    mode="no_noisy_sim",
    backend=None,
    save_dir="./results",
    loss_file="losses.csv",
    params_file="params.csv",
    vqe_kwargs={"ansatz_reps": 1, "HF_bitstring": hf_state}
)

# Run CAFQA optimization (requires hypermapper)
energy_cafqa, params_cafqa = cafqa.run_cafqa(
    n_qubits=4,
    coeffs=coeffs,
    paulis=paulis,
    param_guess=[],
    budget=100,
    save_dir="./results",
    loss_file="cafqa_losses.csv", 
    params_file="cafqa_params.csv",
    vqe_kwargs={"ansatz_reps": 1, "HF_bitstring": hf_state}
)
```

## Notes

- The package includes conditional imports for hypermapper to avoid dependency issues
- All functions from the original modules are available through the main `cafqa` namespace
- The CLI entry point has been removed to avoid import issues with optional dependencies
- Examples and test files are excluded from the built distributions 