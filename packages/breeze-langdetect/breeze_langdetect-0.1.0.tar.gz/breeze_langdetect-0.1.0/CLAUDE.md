# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python extension module written in Rust that provides language detection capabilities using the `hyperpolyglot` library. The project uses `maturin` to build and package the Rust code as a Python module.

## Build and Development Commands

### Building the Project
```bash
# Build the Python extension module
maturin develop

# Build in release mode
maturin develop --release

# Build a wheel for distribution
maturin build
```

### Testing
```bash
# Run Rust tests
cargo test

# Run Python tests (after building with maturin develop)
python -m pytest
```

### Linting and Formatting
```bash
# Rust formatting
cargo fmt

# Rust linting
cargo clippy

# Check for compilation errors
cargo check
```

## Architecture

The project bridges Rust and Python using PyO3:

- **Rust Core (`src/lib.rs`)**: Exposes a `detect_language` function that takes a file path and returns the detected programming language using the `hyperpolyglot` crate.
- **Python Interface**: The Rust function is exposed as a Python module named `breeze_langdetect` with a single function `detect_language(path: str) -> Optional[str]`.

The function returns `None` if no language is detected, or a string with the language name if detection succeeds. IO errors are propagated as Python exceptions.

## Key Dependencies

- **hyperpolyglot**: Rust library for detecting programming languages from file paths
- **pyo3**: Rust-Python interoperability framework
- **maturin**: Build tool for creating Python extensions from Rust code