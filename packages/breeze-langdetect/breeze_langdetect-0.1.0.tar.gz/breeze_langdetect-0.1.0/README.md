# breeze-langdetect

A Python extension for detecting programming languages from file paths, powered by Rust and hyperpolyglot.

## Installation

```bash
pip install breeze-langdetect
```

## Usage

```python
from breeze_langdetect import detect_language

# Detect language from a file path
language = detect_language("example.py")
print(language)  # "Python"

# Returns None if language cannot be detected
language = detect_language("unknown.xyz")
print(language)  # None
```

## Features

- Fast language detection using the hyperpolyglot library
- Simple Python API with a single function
- Returns `None` for unrecognized files
- Proper error handling with Python exceptions

## Building from Source

This project uses [maturin](https://github.com/PyO3/maturin) for building Python extensions in Rust.

```bash
# Install maturin
pip install maturin

# Build and install locally
maturin develop

# Build wheel for distribution
maturin build
```

## Development

```bash
# Run Rust tests
cargo test

# Format code
cargo fmt

# Run linter
cargo clippy
```
