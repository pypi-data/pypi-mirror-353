# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python extension module written in Rust that provides language detection and file type identification capabilities using the `hyperpolyglot` and `infer` libraries. The project uses `maturin` to build and package the Rust code as a Python module.

## Build and Development Commands

### Building the Project
```bash
# Install development dependencies
uv sync --extra dev

# Build the Python extension module
maturin develop

# Build in release mode
maturin develop --release

# Build a wheel for distribution
maturin build --release
```

### Testing
```bash
# Run Python tests (after building with maturin develop)
python -m pytest

# Run with verbose output
python -m pytest -v

# Run Rust tests
cargo test
```

### Linting and Formatting
```bash
# Rust formatting
cargo fmt

# Rust linting
cargo clippy

# Python formatting
ruff format .

# Python linting
ruff check .

# Check for compilation errors
cargo check
```

## Architecture

The project bridges Rust and Python using PyO3, providing comprehensive file analysis capabilities:

### Core Components

1. **Language Detection** (via hyperpolyglot):
   - `detect_language(path: str) -> Optional[str]`: Basic language detection
   - `detect_language_with_strategy(path: str) -> Optional[LanguageDetection]`: Detection with strategy info
   - Returns detection strategy (Filename, Extension, Shebang, Heuristics, Classifier)

2. **File Type Detection** (via infer):
   - `detect_file_type(path: str) -> Optional[FileType]`: MIME type and category detection
   - Identifies files by content/magic bytes
   - Categorizes files (Image, Video, Audio, Document, etc.)

3. **Combined Analysis**:
   - `detect_file_info(path: str) -> FileInfo`: Complete file information
   - Combines both language and file type detection
   - Includes detailed detection strategy information

### Type System

The module exposes several Python types:

- **DetectionStrategy**: Enum indicating how language was detected
- **LanguageDetection**: Struct with language name and detection strategy
- **FileCategory**: Enum for file type categories (IMAGE, AUDIO, VIDEO, etc.)
- **FileType**: Struct with MIME type, extension, and category
- **FileInfo**: Combined information with both language and file type details

### Error Handling

- Functions return `None` when detection is not possible
- IO errors are propagated as Python exceptions
- Language detection failures in `detect_file_info` are non-critical

## Key Dependencies

- **hyperpolyglot**: Rust library for detecting programming languages from file paths
- **infer**: Rust library for file type detection based on magic bytes
- **pyo3**: Rust-Python interoperability framework
- **maturin**: Build tool for creating Python extensions from Rust code

## Testing Strategy

The project includes comprehensive Python tests covering:
- Language detection for various file types
- File type detection including binary formats
- Combined detection scenarios
- Edge cases (nonexistent files, unknown formats)
- Enum comparison and type system validation