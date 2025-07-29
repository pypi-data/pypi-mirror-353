use std::io::Write;

use colored::{Color, Colorize};
use karva_project::project::Project;
use pyo3::prelude::*;

use crate::{
    diagnostic::{
        Diagnostic, DiagnosticType,
        reporter::{DummyReporter, Reporter},
    },
    discovery::{Discoverer, discoverer::DiscoveredTests},
};

pub trait TestRunner {
    fn test(&self) -> RunDiagnostics;
    fn test_with_reporter(&self, reporter: &mut dyn Reporter) -> RunDiagnostics;
}

pub struct StandardTestRunner<'proj> {
    project: &'proj Project,
}

impl<'proj> StandardTestRunner<'proj> {
    #[must_use]
    pub const fn new(project: &'proj Project) -> Self {
        Self { project }
    }

    #[must_use]
    fn test_impl(&self, reporter: &mut dyn Reporter) -> RunDiagnostics {
        let discovered_tests: DiscoveredTests<'proj> = Discoverer::new(self.project).discover();
        let total_tests = discovered_tests.count;

        reporter.set_files(total_tests);

        let test_results: Vec<Diagnostic> = Python::with_gil(|py| {
            let add_cwd_to_sys_path_result = self.add_cwd_to_sys_path(py);

            if add_cwd_to_sys_path_result.is_err() {
                tracing::error!("Failed to add {cwd} to sys.path", cwd = self.project.cwd());
                return Vec::new();
            }

            discovered_tests
                .tests
                .into_iter()
                .filter_map(|(module, test_cases)| {
                    PyModule::import(py, module.name()).map_or_else(
                        |err| {
                            tracing::error!("Failed to import module {}", module.name());
                            tracing::debug!("{:?}", err);
                            None
                        },
                        |py_module| {
                            Some(
                                test_cases
                                    .into_iter()
                                    .filter_map(|test_case| {
                                        let test_name = test_case.to_string();
                                        let result = test_case.run_test(&py, &py_module);
                                        reporter.report_test(&test_name);
                                        result
                                    })
                                    .collect::<Vec<_>>(),
                            )
                        },
                    )
                })
                .flatten()
                .collect()
        });

        RunDiagnostics::new(test_results, total_tests)
    }

    fn add_cwd_to_sys_path(&self, py: Python) -> PyResult<()> {
        let sys_path = py.import("sys")?;
        let path = sys_path.getattr("path")?;
        path.call_method1("append", (self.project.cwd().as_str(),))?;
        Ok(())
    }
}

impl TestRunner for StandardTestRunner<'_> {
    fn test(&self) -> RunDiagnostics {
        self.test_impl(&mut DummyReporter)
    }

    fn test_with_reporter(&self, reporter: &mut dyn Reporter) -> RunDiagnostics {
        self.test_impl(reporter)
    }
}

impl TestRunner for Project {
    fn test(&self) -> RunDiagnostics {
        let test_runner = StandardTestRunner::new(self);
        test_runner.test()
    }

    fn test_with_reporter(&self, reporter: &mut dyn Reporter) -> RunDiagnostics {
        let test_runner = StandardTestRunner::new(self);
        test_runner.test_with_reporter(reporter)
    }
}

#[derive(Clone)]
pub struct RunDiagnostics {
    diagnostics: Vec<Diagnostic>,
    total_tests: usize,
}

impl RunDiagnostics {
    #[must_use]
    pub const fn new(test_results: Vec<Diagnostic>, total_tests: usize) -> Self {
        Self {
            diagnostics: test_results,
            total_tests,
        }
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.diagnostics.is_empty()
    }

    #[must_use]
    pub fn test_results(&self) -> &[Diagnostic] {
        &self.diagnostics
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.diagnostics.len()
    }

    #[must_use]
    pub fn stats(&self) -> DiagnosticStats {
        let mut stats = DiagnosticStats::new(self.total_tests);
        for diagnostic in &self.diagnostics {
            stats.passed -= 1;
            match diagnostic.diagnostic_type() {
                DiagnosticType::Fail => stats.failed += 1,
                DiagnosticType::Error(_) => stats.error += 1,
            }
        }
        stats
    }

    fn log_test_count(writer: &mut dyn Write, label: &str, count: usize, color: Color) {
        if count > 0 {
            let _ = writeln!(
                writer,
                "{} {}",
                label.color(color),
                count.to_string().color(color)
            );
        }
    }

    pub fn display(&self, writer: &mut dyn Write) {
        let stats = self.stats();

        if stats.total() > 0 {
            let _ = writeln!(writer, "{}", "─────────────".bold());
            for (label, num, color) in [
                ("Passed tests:", stats.passed(), Color::Green),
                ("Failed tests:", stats.failed(), Color::Red),
                ("Error tests:", stats.error(), Color::Yellow),
            ] {
                Self::log_test_count(writer, label, num, color);
            }
        }
    }

    pub fn iter(&self) -> impl Iterator<Item = &Diagnostic> {
        self.diagnostics.iter()
    }
}

#[derive(Debug)]
pub struct DiagnosticStats {
    total: usize,
    passed: usize,
    failed: usize,
    error: usize,
}

impl DiagnosticStats {
    const fn new(total: usize) -> Self {
        Self {
            total,
            passed: total,
            failed: 0,
            error: 0,
        }
    }
    #[must_use]
    pub const fn total(&self) -> usize {
        self.total
    }

    #[must_use]
    pub const fn passed(&self) -> usize {
        self.passed
    }

    #[must_use]
    pub const fn failed(&self) -> usize {
        self.failed
    }

    #[must_use]
    pub const fn error(&self) -> usize {
        self.error
    }
}

#[cfg(test)]
mod tests {

    use karva_project::path::SystemPathBuf;
    use tempfile::TempDir;

    use super::*;

    struct TestEnv {
        temp_dir: TempDir,
    }

    impl TestEnv {
        fn new() -> Self {
            Self {
                temp_dir: TempDir::new().unwrap(),
            }
        }

        fn create_test_file(&self, filename: &str, content: &str) -> String {
            let path = self.temp_dir.path().join(filename);
            std::fs::write(&path, content).unwrap();
            path.display().to_string()
        }

        fn create_python_test_path(&self, filename: &str) -> String {
            let path = self.temp_dir.path().join(filename);
            path.display().to_string()
        }
    }

    #[test]
    fn test_runner_with_passing_test() {
        let env = TestEnv::new();
        env.create_test_file(
            "test_pass.py",
            r"
def test_simple_pass():
    assert True
",
        );

        let project = Project::new(
            SystemPathBuf::from(env.temp_dir.path()),
            vec![env.create_python_test_path("test_pass.py")],
        );
        let runner = StandardTestRunner::new(&project);

        let result = runner.test();

        assert_eq!(result.stats().total(), 1);
        assert_eq!(result.stats().passed(), 1);
        assert_eq!(result.stats().failed(), 0);
        assert_eq!(result.stats().error(), 0);
    }

    #[test]
    fn test_runner_with_failing_test() {
        let env = TestEnv::new();
        env.create_test_file(
            "test_fail.py",
            r#"
def test_simple_fail():
    assert False, "This test should fail"
"#,
        );

        let project = Project::new(
            SystemPathBuf::from(env.temp_dir.path()),
            vec![env.create_python_test_path("test_fail.py")],
        );
        let runner = StandardTestRunner::new(&project);

        let result = runner.test();

        assert_eq!(result.stats().total(), 1);
        assert_eq!(result.stats().passed(), 0);
        assert_eq!(result.stats().failed(), 1);
        assert_eq!(result.stats().error(), 0);
    }

    #[test]
    fn test_runner_with_error_test() {
        let env = TestEnv::new();
        env.create_test_file(
            "test_error.py",
            r#"
def test_simple_error():
    raise ValueError("This is an error")
"#,
        );

        let project = Project::new(
            SystemPathBuf::from(env.temp_dir.path()),
            vec![env.create_python_test_path("test_error.py")],
        );
        let runner = StandardTestRunner::new(&project);

        let result = runner.test();

        assert_eq!(result.stats().total(), 1);
        assert_eq!(result.stats().passed(), 0);
        assert_eq!(result.stats().failed(), 0);
        assert_eq!(result.stats().error(), 1);
    }

    #[test]
    fn test_runner_with_multiple_tests() {
        let env = TestEnv::new();
        env.create_test_file(
            "test_mixed.py",
            r#"def test_pass():
    assert True

def test_fail():
    assert False, "This test should fail"

def test_error():
    raise ValueError("This is an error")
"#,
        );

        let project = Project::new(
            SystemPathBuf::from(env.temp_dir.path()),
            vec![env.create_python_test_path("test_mixed.py")],
        );
        let runner = StandardTestRunner::new(&project);

        let result = runner.test();

        assert_eq!(result.stats().total(), 3);
        assert_eq!(result.stats().passed(), 1);
        assert_eq!(result.stats().failed(), 1);
        assert_eq!(result.stats().error(), 1);
    }
}
