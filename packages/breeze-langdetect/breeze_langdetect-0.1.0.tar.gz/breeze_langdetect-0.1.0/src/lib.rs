use std::path::Path;

use pyo3::{exceptions::PyIOError, prelude::*};

#[pyfunction]
fn detect_language(path: &str) -> PyResult<Option<String>> {
    let path = Path::new(&path);

    match hyperpolyglot::detect(path) {
        Ok(Some(detection)) => Ok(Some(detection.language().to_string())),
        Ok(None) => Ok(None),
        Err(e) => Err(PyIOError::new_err(e.to_string())),
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn breeze_langdetect(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(detect_language, m)?)?;
    Ok(())
}
