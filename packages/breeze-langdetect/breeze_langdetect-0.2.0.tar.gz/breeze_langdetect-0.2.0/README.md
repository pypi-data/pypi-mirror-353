# breeze-langdetect

A Python extension for detecting programming languages and file types, combining the power of `hyperpolyglot` for language detection and `infer` for file type identification.

## Installation

```bash
pip install breeze-langdetect
```

## Features

- **Language Detection**: Fast and accurate programming language detection using hyperpolyglot
- **File Type Detection**: MIME type and file category detection using the infer crate
- **Detection Strategy Information**: Know whether language was detected from filename, extension, shebang, heuristics, or classifier
- **Combined Analysis**: Get both language and file type information in a single call
- **Pure Rust Performance**: Fast detection with Python bindings via PyO3
- **Comprehensive Type Support**: Detects hundreds of programming languages and file types

## Usage

### Basic Language Detection

```python
import breeze_langdetect

# Detect language from a file path
language = breeze_langdetect.detect_language("example.py")
print(language)  # "Python"

# Returns None if language cannot be detected
language = breeze_langdetect.detect_language("unknown.xyz")
print(language)  # None
```

### Language Detection with Strategy

```python
# Get detailed detection information
detection = breeze_langdetect.detect_language_with_strategy("script.py")
if detection:
    print(f"Language: {detection.language}")
    print(f"Strategy: {detection.strategy}")
    # Output:
    # Language: Python
    # Strategy: DetectionStrategy.EXTENSION
```

### File Type Detection

```python
# Detect file type from content
file_type = breeze_langdetect.detect_file_type("image.png")
if file_type:
    print(f"MIME Type: {file_type.mime_type}")      # "image/png"
    print(f"Extension: {file_type.extension}")       # "png"
    print(f"Category: {file_type.category}")         # FileCategory.IMAGE
```

### Combined File Information

```python
# Get both language and file type information
info = breeze_langdetect.detect_file_info("main.rs")
print(f"Language: {info.language}")                  # "Rust"
print(f"File Type: {info.file_type}")                # FileType details if detected
print(f"Detection: {info.language_detection}")       # Full detection details
```

## Types and Enums

### DetectionStrategy

Indicates how the language was detected:

- `FILENAME`: Detected from the filename (e.g., "Makefile")
- `EXTENSION`: Detected from file extension (e.g., ".py" → Python)
- `SHEBANG`: Detected from shebang line (e.g., "#!/usr/bin/env python")
- `HEURISTICS`: Detected using content heuristics
- `CLASSIFIER`: Detected using the statistical classifier

### FileCategory

Categorizes the type of file:

- `APPLICATION`: Application files (e.g., executables, JSON)
- `ARCHIVE`: Archive files (e.g., zip, tar)
- `AUDIO`: Audio files (e.g., mp3, wav)
- `BOOK`: E-book files (e.g., epub, mobi)
- `DOCUMENT`: Document files (e.g., pdf, docx)
- `FONT`: Font files (e.g., ttf, otf)
- `IMAGE`: Image files (e.g., jpg, png, gif)
- `VIDEO`: Video files (e.g., mp4, avi)
- `TEXT`: Plain text files
- `CUSTOM`: Custom file types

## Building from Source

This project uses [maturin](https://github.com/PyO3/maturin) for building Python extensions in Rust.

```bash
# Install development dependencies
pip install maturin[patchelf]

# Build and install locally
maturin develop

# Build wheel for distribution
maturin build --release
```

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
maturin develop
pytest

# Format code
cargo fmt
ruff format .

# Run linters
cargo clippy
ruff check .
```

## Testing

The project includes comprehensive tests for all detection features:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest test_breeze_langdetect.py::TestDetectLanguage::test_python_file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
