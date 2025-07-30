use std::path::Path;

use pyo3::{exceptions::PyIOError, prelude::*};

#[pyclass(eq)]
#[derive(Clone, Debug, PartialEq)]
enum DetectionStrategy {
    #[pyo3(name = "FILENAME")]
    Filename,
    #[pyo3(name = "EXTENSION")]
    Extension,
    #[pyo3(name = "SHEBANG")]
    Shebang,
    #[pyo3(name = "HEURISTICS")]
    Heuristics,
    #[pyo3(name = "CLASSIFIER")]
    Classifier,
}

#[pymethods]
impl DetectionStrategy {
    fn __repr__(&self) -> String {
        match self {
            DetectionStrategy::Filename => "DetectionStrategy.FILENAME",
            DetectionStrategy::Extension => "DetectionStrategy.EXTENSION",
            DetectionStrategy::Shebang => "DetectionStrategy.SHEBANG",
            DetectionStrategy::Heuristics => "DetectionStrategy.HEURISTICS",
            DetectionStrategy::Classifier => "DetectionStrategy.CLASSIFIER",
        }
        .to_string()
    }
}

impl From<hyperpolyglot::Detection> for DetectionStrategy {
    fn from(detection: hyperpolyglot::Detection) -> Self {
        match detection {
            hyperpolyglot::Detection::Filename(_) => DetectionStrategy::Filename,
            hyperpolyglot::Detection::Extension(_) => DetectionStrategy::Extension,
            hyperpolyglot::Detection::Shebang(_) => DetectionStrategy::Shebang,
            hyperpolyglot::Detection::Heuristics(_) => DetectionStrategy::Heuristics,
            hyperpolyglot::Detection::Classifier(_) => DetectionStrategy::Classifier,
        }
    }
}

#[pyclass]
#[derive(Clone, Debug)]
struct LanguageDetection {
    #[pyo3(get)]
    language: String,
    #[pyo3(get)]
    strategy: DetectionStrategy,
}

#[pymethods]
impl LanguageDetection {
    fn __repr__(&self) -> String {
        format!(
            "LanguageDetection(language='{}', strategy={})",
            self.language,
            self.strategy.__repr__()
        )
    }
}

#[pyclass(eq)]
#[derive(Clone, Debug, PartialEq)]
enum FileCategory {
    #[pyo3(name = "APPLICATION")]
    Application,
    #[pyo3(name = "ARCHIVE")]
    Archive,
    #[pyo3(name = "AUDIO")]
    Audio,
    #[pyo3(name = "BOOK")]
    Book,
    #[pyo3(name = "DOCUMENT")]
    Document,
    #[pyo3(name = "FONT")]
    Font,
    #[pyo3(name = "IMAGE")]
    Image,
    #[pyo3(name = "VIDEO")]
    Video,
    #[pyo3(name = "TEXT")]
    Text,
    #[pyo3(name = "CUSTOM")]
    Custom,
}

#[pymethods]
impl FileCategory {
    fn __repr__(&self) -> String {
        match self {
            FileCategory::Application => "FileCategory.APPLICATION",
            FileCategory::Archive => "FileCategory.ARCHIVE",
            FileCategory::Audio => "FileCategory.AUDIO",
            FileCategory::Book => "FileCategory.BOOK",
            FileCategory::Document => "FileCategory.DOCUMENT",
            FileCategory::Font => "FileCategory.FONT",
            FileCategory::Image => "FileCategory.IMAGE",
            FileCategory::Video => "FileCategory.VIDEO",
            FileCategory::Text => "FileCategory.TEXT",
            FileCategory::Custom => "FileCategory.CUSTOM",
        }
        .to_string()
    }
}

impl From<infer::MatcherType> for FileCategory {
    fn from(matcher_type: infer::MatcherType) -> Self {
        match matcher_type {
            infer::MatcherType::App => FileCategory::Application,
            infer::MatcherType::Archive => FileCategory::Archive,
            infer::MatcherType::Audio => FileCategory::Audio,
            infer::MatcherType::Book => FileCategory::Book,
            infer::MatcherType::Doc => FileCategory::Document,
            infer::MatcherType::Font => FileCategory::Font,
            infer::MatcherType::Image => FileCategory::Image,
            infer::MatcherType::Video => FileCategory::Video,
            infer::MatcherType::Text => FileCategory::Text,
            infer::MatcherType::Custom => FileCategory::Custom,
        }
    }
}

#[pyclass]
#[derive(Clone, Debug)]
struct FileType {
    #[pyo3(get)]
    mime_type: String,
    #[pyo3(get)]
    extension: Option<String>,
    #[pyo3(get)]
    category: FileCategory,
}

#[pymethods]
impl FileType {
    fn __repr__(&self) -> String {
        match &self.extension {
            Some(ext) => format!(
                "FileType(mime_type='{}', extension='{}', category={})",
                self.mime_type,
                ext,
                self.category.__repr__()
            ),
            None => format!(
                "FileType(mime_type='{}', category={})",
                self.mime_type,
                self.category.__repr__()
            ),
        }
    }
}

#[pyclass]
#[derive(Clone, Debug)]
struct FileInfo {
    #[pyo3(get)]
    file_type: Option<FileType>,
    #[pyo3(get)]
    language: Option<String>,
    #[pyo3(get)]
    language_detection: Option<LanguageDetection>,
}

#[pymethods]
impl FileInfo {
    fn __repr__(&self) -> String {
        let file_type_str = match &self.file_type {
            Some(ft) => ft.__repr__(),
            None => "None".to_string(),
        };
        let lang_detection_str = match &self.language_detection {
            Some(ld) => ld.__repr__(),
            None => "None".to_string(),
        };
        format!(
            "FileInfo(file_type={}, language={:?}, language_detection={})",
            file_type_str, self.language, lang_detection_str
        )
    }
}

#[pyfunction]
#[pyo3(text_signature = "(path, /)")]
/// Detect the programming language of a file.
///
/// Args:
///     path: Path to the file to analyze
///
/// Returns:
///     The detected language name, or None if no language was detected
///
/// Raises:
///     OSError: If there's an error reading the file
fn detect_language(path: &str) -> PyResult<Option<String>> {
    let path = Path::new(&path);

    match hyperpolyglot::detect(path) {
        Ok(Some(detection)) => Ok(Some(detection.language().to_string())),
        Ok(None) => Ok(None),
        Err(e) => Err(PyIOError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(text_signature = "(path, /)")]
/// Detect the programming language of a file with detailed strategy information.
///
/// Args:
///     path: Path to the file to analyze
///
/// Returns:
///     A LanguageDetection object with language name and detection strategy,
///     or None if no language was detected
///
/// Raises:
///     OSError: If there's an error reading the file
fn detect_language_with_strategy(path: &str) -> PyResult<Option<LanguageDetection>> {
    let path = Path::new(&path);

    match hyperpolyglot::detect(path) {
        Ok(Some(detection)) => Ok(Some(LanguageDetection {
            language: detection.language().to_string(),
            strategy: detection.into(),
        })),
        Ok(None) => Ok(None),
        Err(e) => Err(PyIOError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(text_signature = "(path, /)")]
/// Detect the file type by reading the file's content and checking magic bytes.
///
/// Args:
///     path: Path to the file to analyze
///
/// Returns:
///     A FileType object with MIME type, extension, and category,
///     or None if the file type couldn't be determined
///
/// Raises:
///     OSError: If there's an error reading the file
fn detect_file_type(path: &str) -> PyResult<Option<FileType>> {
    match infer::get_from_path(path) {
        Ok(Some(file_type)) => Ok(Some(FileType {
            mime_type: file_type.mime_type().to_string(),
            extension: Some(file_type.extension().to_string()),
            category: file_type.matcher_type().into(),
        })),
        Ok(None) => Ok(None),
        Err(e) => Err(PyIOError::new_err(e.to_string())),
    }
}

#[pyfunction]
#[pyo3(text_signature = "(path, /)")]
/// Detect both file type and programming language for a given file.
///
/// This combines the functionality of detect_language_with_strategy and detect_file_type
/// to provide comprehensive file information in a single call.
///
/// Args:
///     path: Path to the file to analyze
///
/// Returns:
///     A FileInfo object containing:
///     - file_type: Optional FileType with MIME type and category
///     - language: Optional detected programming language name
///     - language_detection: Optional detailed language detection info
///
/// Raises:
///     OSError: If there's an error reading the file for file type detection
///
/// Note:
///     Language detection failures are silently ignored and return None
fn detect_file_info(path: &str) -> PyResult<FileInfo> {
    let file_type = match infer::get_from_path(path) {
        Ok(Some(ft)) => Some(FileType {
            mime_type: ft.mime_type().to_string(),
            extension: Some(ft.extension().to_string()),
            category: ft.matcher_type().into(),
        }),
        Ok(None) => None,
        Err(e) => return Err(PyIOError::new_err(e.to_string())),
    };

    let (language, language_detection) = match hyperpolyglot::detect(Path::new(path)) {
        Ok(Some(detection)) => (
            Some(detection.language().to_string()),
            Some(LanguageDetection {
                language: detection.language().to_string(),
                strategy: detection.into(),
            }),
        ),
        Ok(None) => (None, None),
        Err(_) => (None, None), // Language detection failure is not critical
    };

    Ok(FileInfo {
        file_type,
        language,
        language_detection,
    })
}

/// Fast file type and programming language detection for Python.
///
/// This module provides functions to detect programming languages and file types
/// using the Rust libraries hyperpolyglot and infer.
#[pymodule]
fn breeze_langdetect(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<DetectionStrategy>()?;
    m.add_class::<LanguageDetection>()?;
    m.add_class::<FileCategory>()?;
    m.add_class::<FileType>()?;
    m.add_class::<FileInfo>()?;
    m.add_function(wrap_pyfunction!(detect_language, m)?)?;
    m.add_function(wrap_pyfunction!(detect_language_with_strategy, m)?)?;
    m.add_function(wrap_pyfunction!(detect_file_type, m)?)?;
    m.add_function(wrap_pyfunction!(detect_file_info, m)?)?;
    Ok(())
}
