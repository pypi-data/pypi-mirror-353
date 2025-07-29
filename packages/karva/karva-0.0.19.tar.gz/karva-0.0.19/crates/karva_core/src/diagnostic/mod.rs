use pyo3::{prelude::*, types::PyString};

use crate::diagnostic::render::DisplayDiagnostic;

pub mod render;
pub mod reporter;

#[derive(Clone)]
pub struct Diagnostic {
    diagnostic_type: DiagnosticType,
    message: String,
}

impl Diagnostic {
    pub fn from_py_err(py: &Python, error: &PyErr) -> Self {
        Self {
            diagnostic_type: DiagnosticType::Error(get_type_name(*py, error)),
            message: error.to_string(),
        }
    }

    pub fn from_py_fail(py: &Python, error: &PyErr) -> Self {
        let default_error = |error: &PyErr| Self {
            diagnostic_type: DiagnosticType::Error(get_type_name(*py, error)),
            message: get_traceback(*py, error).unwrap_or_default(),
        };

        if error.is_instance_of::<pyo3::exceptions::PyAssertionError>(*py) {
            return Self {
                diagnostic_type: DiagnosticType::Fail,
                message: get_traceback(*py, error).unwrap_or_default(),
            };
        }
        default_error(error)
    }

    #[must_use]
    pub const fn diagnostic_type(&self) -> &DiagnosticType {
        &self.diagnostic_type
    }

    #[must_use]
    pub const fn display(&self) -> DisplayDiagnostic {
        DisplayDiagnostic::new(self)
    }
}

#[derive(Clone)]
pub enum DiagnosticType {
    Fail,
    Error(String),
}

fn get_traceback(py: Python<'_>, error: &PyErr) -> Option<String> {
    if let Some(traceback) = error.traceback(py) {
        let traceback_str = traceback.format().unwrap_or_default();
        if traceback_str.is_empty() {
            return None;
        }
        Some(filter_traceback(&traceback_str))
    } else {
        None
    }
}

fn get_type_name(py: Python<'_>, error: &PyErr) -> String {
    error
        .get_type(py)
        .name()
        .unwrap_or_else(|_| PyString::new(py, "Unknown"))
        .to_string()
}

// Simplified traceback filtering that removes unnecessary traceback headers
fn filter_traceback(traceback: &str) -> String {
    let lines: Vec<&str> = traceback.lines().collect();
    let mut filtered = String::new();

    for (i, line) in lines.iter().enumerate() {
        if i == 0 && line.contains("Traceback (most recent call last):") {
            continue;
        }
        if line.starts_with("  ") {
            if let Some(stripped) = line.strip_prefix("  ") {
                filtered.push_str(stripped);
            }
        } else {
            filtered.push_str(line);
        }
        filtered.push('\n');
    }
    filtered = filtered.trim_end_matches('\n').to_string();

    filtered = filtered.trim_end_matches('^').to_string();

    filtered.trim_end().to_string()
}
