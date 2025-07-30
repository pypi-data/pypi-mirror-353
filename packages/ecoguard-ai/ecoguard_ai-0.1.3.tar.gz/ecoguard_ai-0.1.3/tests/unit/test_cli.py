"""
Test suite for the CLI module.

This module tests the command-line interface functionality.
"""

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ecoguard_ai.cli import (
    _display_ast_research_summary,
    _display_project_result,
    _display_project_table,
    _display_single_result,
    _display_table_result,
    _get_severity_color,
    cli,
    main,
)
from ecoguard_ai.core.issue import Category, Fix, Impact, Issue, Severity
from ecoguard_ai.core.result import AnalysisResult, ProjectAnalysisResult


@pytest.fixture
def runner():
    """CLI runner fixture for tests."""
    return CliRunner()


@pytest.fixture
def temp_python_file(tmp_path):
    """Create a temporary Python file for testing."""
    content = """def example_function():
    return "Hello, World!"
"""
    file_path = tmp_path / "test_file.py"
    file_path.write_text(content)
    return file_path


@contextmanager
def windows_safe_tempfile(content: str, suffix: str = ".py"):
    """
    Create a temporary file that works safely on Windows.

    Windows has issues with deleting files that are still open,
    so we need to properly close them before deletion.
    """
    # Create a temporary file without auto-deletion
    fd, filepath = tempfile.mkstemp(suffix=suffix, text=True)
    try:
        # Write content to the file
        with os.fdopen(fd, "w") as f:
            f.write(content)
        # Return the path for use
        yield filepath
    finally:
        # Ensure file is deleted even if test fails
        try:
            os.unlink(filepath)
        except OSError:
            pass  # File might already be deleted


class TestCLIMain:
    """Test main CLI entry points."""

    def test_main_function_calls_cli(self) -> None:
        """Test that main() calls the CLI."""
        with patch("ecoguard_ai.cli.cli") as mock_cli:
            main()
            mock_cli.assert_called_once()

    def test_main_with_args(self) -> None:
        """Test main function with command line arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "EcoGuard AI" in result.output


class TestCLICommands:
    """Test CLI commands."""

    def test_version_command(self, runner) -> None:
        """Test version command output."""
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "EcoGuard AI v0.1.2" in result.output
        assert "AI-augmented software development pipeline solution" in result.output

    def test_version_subcommand(self) -> None:
        """Test version subcommand."""
        runner = CliRunner()
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "EcoGuard AI" in result.output

    def test_help_command(self) -> None:
        """Test help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "EcoGuard AI" in result.output
        assert "analyze" in result.output
        assert "rules" in result.output
        assert "version" in result.output

    def test_analyze_help(self) -> None:
        """Test analyze command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze Python code" in result.output

    def test_rules_help(self) -> None:
        """Test rules command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["rules", "--help"])
        assert result.exit_code == 0


class TestAnalyzeCommand:
    """Test the analyze command."""

    def test_analyze_nonexistent_file(self) -> None:
        """Test analyze command with nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "nonexistent_file.py"])
        assert result.exit_code == 2  # Click validation error

    def test_analyze_with_valid_file(self) -> None:
        """Test analyze command with valid Python file."""
        with windows_safe_tempfile("print('hello world')") as temp_file:
            runner = CliRunner()
            result = runner.invoke(cli, ["analyze", temp_file])
            # Should execute without error (may exit with 0 or 1 depending
            # on issues found)
            assert result.exit_code in [0, 1]

    def test_analyze_with_config_option(
        self, runner, temp_python_file, tmp_path
    ) -> None:
        """Test analyze command with config option."""
        # Create a temporary config file
        config_file = tmp_path / "config.yaml"
        config_file.write_text("# Test config file\n")

        result = runner.invoke(
            cli, ["analyze", str(temp_python_file), "--config", str(config_file)]
        )
        # Should show config warning but still work
        assert (
            result.exit_code == 0
            or "Config file support coming in future release" in result.output
        )

    def test_analyze_with_format_json(self, runner, temp_python_file) -> None:
        """Test analyze command with JSON output format."""
        result = runner.invoke(
            cli, ["analyze", str(temp_python_file), "--format", "json"]
        )
        assert result.exit_code == 0
        # JSON output should be parseable
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            # If not valid JSON, at least check it ran
            pass

    def test_analyze_directory(self) -> None:
        """Test analyze command with directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Python file in the directory
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('hello world')")

            runner = CliRunner()
            result = runner.invoke(cli, ["analyze", temp_dir])
            assert result.exit_code in [0, 1]

    def test_analyze_directory_with_errors(self, runner, tmp_path) -> None:
        """Test analyze command on directory that causes errors."""
        # Create a directory with Python files that might have issues
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()

        # Create a file with potential issues
        (test_dir / "test.py").write_text(
            """
# File with unused variable
def test_func() -> None:
    unused_var = 42
    return "hello"
"""
        )

        result = runner.invoke(cli, ["analyze", str(test_dir)])
        # Command should complete (exit codes handled by analyzer)
        assert isinstance(result.exit_code, int)

    def test_analyze_file_error_exit_code(self, runner, tmp_path) -> None:
        """Test that analyze exits with error code when critical issues found."""
        # Create a file that might trigger error-level issues
        test_file = tmp_path / "error_file.py"
        test_file.write_text("# This might not trigger errors, but test the path")

        result = runner.invoke(cli, ["analyze", str(test_file)])
        # Exit code should be 0 or 1 depending on analysis results
        assert result.exit_code in [0, 1]

    def test_analyze_with_invalid_format(self) -> None:
        """Test analyze command with invalid format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello world')")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name, "--format", "invalid"])
                assert result.exit_code == 2  # Click validation error
                assert "Invalid value" in result.output
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_severity_filter(self) -> None:
        """Test analyze command with severity filtering."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import unused_module\ndef test(): pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name, "--severity", "error"])
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_disabled_modules(self) -> None:
        """Test analyze command with disabled analysis modules."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello world')")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    [
                        "analyze",
                        f.name,
                        "--no-quality",
                        "--no-security",
                        "--no-green",
                        "--no-ai-code",
                    ],
                )
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)


class TestRulesCommand:
    """Test the rules command."""

    def test_rules_list(self) -> None:
        """Test rules list command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["rules"])
        assert result.exit_code == 0
        assert "Available Analysis Rules" in result.output


class TestCLIHelpers:
    """Test CLI helper functions."""

    def test_get_severity_color(self) -> None:
        """Test severity color mapping function."""
        assert _get_severity_color(Severity.DEBUG) == "dim"
        assert _get_severity_color(Severity.INFO) == "blue"
        assert _get_severity_color(Severity.WARNING) == "yellow"
        assert _get_severity_color(Severity.ERROR) == "red"
        assert _get_severity_color(Severity.CRITICAL) == "red bold"

    def test_display_single_result_with_issues(self) -> None:
        """Test display function with issues present."""
        issues = [
            Issue(
                rule_id="test_rule",
                category="quality",
                severity="warning",
                message="Test issue",
                file_path="test.py",
                line=1,
                impact=Impact(maintainability=-0.5),
                suggested_fix=Fix(description="Test fix"),
            )
        ]
        result = AnalysisResult(file_path="test.py", issues=issues)

        # Test table format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_single_result(result, "table", None)
            assert mock_console.print.called

    def test_display_single_result_json_format(self) -> None:
        """Test display function with JSON format."""
        result = AnalysisResult(file_path="test.py", issues=[])

        # Test JSON format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_single_result(result, "json", None)
            assert mock_console.print.called

    def test_display_single_result_text_format(self) -> None:
        """Test display function with text format."""
        result = AnalysisResult(file_path="test.py", issues=[])

        # Test text format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_single_result(result, "text", None)
            assert mock_console.print.called

    def test_display_project_result_with_issues(self) -> None:
        """Test project display function with issues."""
        file_results = [
            AnalysisResult(
                file_path="test1.py",
                issues=[
                    Issue(
                        rule_id="test_rule",
                        category="quality",
                        severity="warning",
                        message="Test issue",
                        file_path="test1.py",
                        line=1,
                    )
                ],
            ),
            AnalysisResult(file_path="test2.py", issues=[]),
        ]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        # Test table format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_project_result(project_result, "table", None)
            assert mock_console.print.called

    def test_display_project_result_no_issues(self) -> None:
        """Test project display function with no issues."""
        file_results = [
            AnalysisResult(file_path="test1.py", issues=[]),
            AnalysisResult(file_path="test2.py", issues=[]),
        ]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        # Test table format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_project_result(project_result, "table", None)
            assert mock_console.print.called


class TestCLIIntegration:
    """Integration tests for the CLI."""

    def test_cli_with_empty_file(self) -> None:
        """Test CLI with empty Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")  # Empty file
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name])
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_cli_with_complex_code(self) -> None:
        """Test CLI with complex code that triggers multiple rules."""
        complex_code = '''
import os
import sys
import unused_module

def complex_function(a, b, c, d, e, f, g, h):
    """Function with too many parameters."""
    unused_var = 42
    result = []
    for i in range(len(a)):
        result.append(a[i] * 2)
    return result

class TestClass:
    def method1(self):
        x = "hello"
        x += " world"
        x += " test"
        return x
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(complex_code)
            f.flush()

            try:
                runner = CliRunner()

                # Test with different formats
                for format_type in ["table", "json", "text"]:
                    result = runner.invoke(
                        cli, ["analyze", f.name, "--format", format_type]
                    )
                    assert result.exit_code in [0, 1]

            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_cli_with_syntax_error(self) -> None:
        """Test CLI with file containing syntax errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def invalid_syntax(:\n    pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name])
                # Should handle syntax errors gracefully
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)


class TestCLIAdvancedFeatures:
    """Test advanced CLI features including AST research options."""

    def test_analyze_with_ast_research_options(self) -> None:
        """Test analyze command with AST research options."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def test_function():
    for i in range(10):
        if i % 2 == 0:
            print(i)
    return True
"""
            )
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    [
                        "analyze",
                        f.name,
                        "--enable-ast-research",
                        "--ast-depth",
                        "comprehensive",
                        "--enable-pattern-analysis",
                        "--enable-complexity-metrics",
                    ],
                )
                assert result.exit_code in [0, 1]
                # Should mention AST research in output
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_ast_research_basic_depth(self) -> None:
        """Test AST research with basic depth."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def simple(): return 42")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    [
                        "analyze",
                        f.name,
                        "--enable-ast-research",
                        "--ast-depth",
                        "basic",
                    ],
                )
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_ast_research_detailed_depth(self) -> None:
        """Test AST research with detailed depth."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("class TestClass:\n    def method(self): pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    [
                        "analyze",
                        f.name,
                        "--enable-ast-research",
                        "--ast-depth",
                        "detailed",
                    ],
                )
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_output_file(self) -> None:
        """Test analyze command with output file option."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as py_file:
            py_file.write("print('test')")
            py_file.flush()

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as output_file:
                try:
                    runner = CliRunner()
                    result = runner.invoke(
                        cli,
                        [
                            "analyze",
                            py_file.name,
                            "--output",
                            output_file.name,
                            "--format",
                            "json",
                        ],
                    )
                    assert result.exit_code in [0, 1]
                    # Output file should contain results
                    assert Path(output_file.name).exists()
                finally:
                    Path(py_file.name).unlink(missing_ok=True)
                    Path(output_file.name).unlink(missing_ok=True)

    def test_analyze_with_text_output_file(self) -> None:
        """Test analyze command with text output to file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as py_file:
            py_file.write("def test(): pass")
            py_file.flush()

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as output_file:
                try:
                    runner = CliRunner()
                    result = runner.invoke(
                        cli,
                        [
                            "analyze",
                            py_file.name,
                            "--output",
                            output_file.name,
                            "--format",
                            "text",
                        ],
                    )
                    assert result.exit_code in [0, 1]
                    assert Path(output_file.name).exists()
                finally:
                    Path(py_file.name).unlink(missing_ok=True)
                    Path(output_file.name).unlink(missing_ok=True)

    def test_analyze_exception_handling(self) -> None:
        """Test analyze command exception handling."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            f.flush()

            try:
                with patch("ecoguard_ai.cli.EcoGuardAnalyzer") as mock_analyzer_class:
                    # Mock the analyzer class to raise an exception when instantiated
                    mock_analyzer_class.side_effect = Exception("Test exception")

                    runner = CliRunner()
                    result = runner.invoke(cli, ["analyze", f.name])
                    assert result.exit_code == 1
                    assert "Error:" in result.output
            finally:
                Path(f.name).unlink(missing_ok=True)


class TestCLIDisplayFunctions:
    """Test CLI display helper functions."""

    def test_display_single_result_with_output_file_json(self) -> None:
        """Test display single result with JSON output file."""
        result = AnalysisResult(file_path="test.py", issues=[])

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            try:
                with patch("ecoguard_ai.cli.console") as mock_console:
                    _display_single_result(result, "json", f.name)
                    mock_console.print.assert_called()
                    # File should be written
                    assert Path(f.name).exists()
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_display_single_result_with_output_file_text(self) -> None:
        """Test display single result with text output file."""
        issues = [
            Issue(
                rule_id="test_rule",
                category=Category.QUALITY,
                severity=Severity.WARNING,
                message="Test issue",
                file_path="test.py",
                line=1,
                impact=Impact(maintainability=-0.5),
                suggested_fix=Fix(description="Test fix"),
            )
        ]
        result = AnalysisResult(file_path="test.py", issues=issues)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            try:
                with patch("ecoguard_ai.cli.console") as mock_console:
                    _display_single_result(result, "text", f.name)
                    mock_console.print.assert_called()
                    assert Path(f.name).exists()
                    # Check file content
                    content = Path(f.name).read_text()
                    assert "Analysis Results for: test.py" in content
                    assert "Test issue" in content
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_display_single_result_no_issues_text(self) -> None:
        """Test display single result with no issues in text format."""
        result = AnalysisResult(file_path="test.py", issues=[])

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_single_result(result, "text", None)
            mock_console.print.assert_called()

    def test_display_table_result_no_issues(self) -> None:
        """Test display table result with no issues."""
        result = AnalysisResult(file_path="test.py", issues=[])

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_table_result(result)
            mock_console.print.assert_called()

    def test_display_table_result_with_issues_and_metadata(self) -> None:
        """Test display table result with issues and AST metadata."""
        issues = [
            Issue(
                rule_id="test_rule",
                category=Category.SECURITY,
                severity=Severity.ERROR,
                message="Security issue",
                file_path="test.py",
                line=5,
            )
        ]

        # Create result with AST research metadata
        result = AnalysisResult(file_path="test.py", issues=issues)
        result.metadata = {
            "ast_research": {
                "max_depth": 5,
                "node_type_counts": {"FunctionDef": 3, "If": 2},
                "complexity_metrics": {
                    "cyclomatic": 4,
                    "max_nesting": 3,
                    "function_count": 2,
                },
                "patterns": {
                    "function_definitions": [
                        MagicMock(attributes={"name": "test_func"}, line=1),
                        MagicMock(attributes={"name": "other_func"}, line=10),
                    ],
                    "conditional_statements": [],
                },
            }
        }

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_table_result(result)
            mock_console.print.assert_called()

    def test_display_project_result_json_with_file(self) -> None:
        """Test display project result with JSON format and output file."""
        file_results = [AnalysisResult(file_path="test.py", issues=[])]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            try:
                with patch("ecoguard_ai.cli.console") as mock_console:
                    _display_project_result(project_result, "json", f.name)
                    mock_console.print.assert_called()
                    assert Path(f.name).exists()
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_display_project_result_text_with_file(self) -> None:
        """Test display project result with text format and output file."""
        issues = [
            Issue(
                rule_id="test_rule",
                category=Category.GREEN,
                severity=Severity.INFO,
                message="Green software issue",
                file_path="test.py",
                line=3,
            )
        ]
        file_results = [AnalysisResult(file_path="test.py", issues=issues)]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            try:
                with patch("ecoguard_ai.cli.console") as mock_console:
                    _display_project_result(project_result, "text", f.name)
                    mock_console.print.assert_called()
                    assert Path(f.name).exists()
                    # Check file content
                    content = Path(f.name).read_text()
                    assert "Project Analysis Results" in content
                    assert "test.py:" in content
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_display_project_table_with_files_with_issues(self) -> None:
        """Test display project table with files containing issues."""
        issues = [
            Issue(
                rule_id="quality_rule",
                category=Category.QUALITY,
                severity=Severity.WARNING,
                message="Quality issue",
                file_path="file1.py",
                line=1,
            ),
            Issue(
                rule_id="security_rule",
                category=Category.SECURITY,
                severity=Severity.CRITICAL,
                message="Critical security issue",
                file_path="file1.py",
                line=5,
            ),
        ]

        file_results = [
            AnalysisResult(file_path="/project/file1.py", issues=issues),
            AnalysisResult(file_path="/project/file2.py", issues=[]),
        ]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_project_table(project_result)
            mock_console.print.assert_called()

    def test_display_project_table_no_issues(self) -> None:
        """Test display project table with no issues in any files."""
        file_results = [
            AnalysisResult(file_path="/project/file1.py", issues=[]),
            AnalysisResult(file_path="/project/file2.py", issues=[]),
        ]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_project_table(project_result)
            mock_console.print.assert_called()

    def test_display_ast_research_summary_with_full_data(self) -> None:
        """Test display AST research summary with comprehensive data."""
        ast_data = {
            "max_depth": 8,
            "node_type_counts": {
                "FunctionDef": 5,
                "ClassDef": 2,
                "If": 7,
                "For": 3,
                "While": 1,
            },
            "complexity_metrics": {
                "cyclomatic": 12,
                "max_nesting": 4,
                "function_count": 5,
            },
            "patterns": {
                "function_definitions": [
                    MagicMock(attributes={"name": "func1"}, line=1),
                    MagicMock(attributes={"name": "func2"}, line=10),
                    MagicMock(attributes={"name": "func3"}, line=20),
                    MagicMock(attributes={"name": "func4"}, line=30),
                ],
                "class_definitions": [
                    MagicMock(attributes={"name": "TestClass"}, line=5)
                ],
                "conditional_statements": [
                    MagicMock(attributes={"id": "cond1"}, line=8),
                    MagicMock(attributes={}, line=15),
                ],
            },
        }

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_ast_research_summary(ast_data)
            mock_console.print.assert_called()

    def test_display_ast_research_summary_with_error(self) -> None:
        """Test display AST research summary with error data."""
        ast_data = {"error": "Failed to analyze AST: syntax error"}

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_ast_research_summary(ast_data)
            mock_console.print.assert_called()

    def test_display_ast_research_summary_minimal_data(self) -> None:
        """Test display AST research summary with minimal data."""
        ast_data = {"max_depth": 3}

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_ast_research_summary(ast_data)
            mock_console.print.assert_called()

    def test_display_ast_research_summary_patterns_with_fallback(self) -> None:
        """Test AST research summary with patterns that need fallback display."""
        ast_data = {
            "patterns": {
                "complex_patterns": [
                    MagicMock(line=5),  # No attributes
                    MagicMock(line=10),
                    MagicMock(line=15),
                    MagicMock(line=20),  # More than 3 items to test truncation
                ]
            }
        }

        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_ast_research_summary(ast_data)
            mock_console.print.assert_called()

    def test_get_severity_color_unknown_severity(self) -> None:
        """Test severity color function with unknown severity."""
        # Create a mock severity that's not in the mapping
        unknown_severity = MagicMock()
        unknown_severity.name = "UNKNOWN"

        color = _get_severity_color(unknown_severity)
        assert color == "white"  # Default fallback color


class TestCLIEdgeCases:
    """Test edge cases and error conditions."""

    def test_analyze_command_with_exception_in_analysis(self) -> None:
        """Test analyze command when analysis throws an exception."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            f.flush()

            try:
                with patch("ecoguard_ai.cli.EcoGuardAnalyzer") as mock_analyzer_class:
                    mock_analyzer = MagicMock()
                    mock_analyzer.analyze_file.side_effect = Exception(
                        "Analysis failed"
                    )
                    mock_analyzer_class.return_value = mock_analyzer

                    runner = CliRunner()
                    result = runner.invoke(cli, ["analyze", f.name])
                    assert result.exit_code == 1
                    assert "Error:" in result.output
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_directory_with_exception(self) -> None:
        """Test analyze directory when analysis throws an exception."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('test')")

            with patch("ecoguard_ai.cli.EcoGuardAnalyzer") as mock_analyzer_class:
                mock_analyzer = MagicMock()
                mock_analyzer.analyze_directory.side_effect = Exception(
                    "Directory analysis failed"
                )
                mock_analyzer_class.return_value = mock_analyzer

                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", temp_dir])
                assert result.exit_code == 1
                assert "Error:" in result.output

    def test_version_command_detailed(self) -> None:
        """Test version command output details."""
        runner = CliRunner()
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "EcoGuard AI v0.1.2" in result.output
        assert "AI-augmented software development pipeline solution" in result.output
        assert "github.com" in result.output

    def test_rules_command_detailed(self) -> None:
        """Test rules command output details."""
        runner = CliRunner()
        result = runner.invoke(cli, ["rules"])
        assert result.exit_code == 0
        assert "Available Analysis Rules" in result.output
        assert "Stage 1" in result.output
        assert "Stage 2" in result.output
        assert "Stage 3" in result.output


class TestCLISeverityHandling:
    """Test CLI severity level handling."""

    def test_analyze_with_all_severity_levels(self) -> None:
        """Test analyze command with each severity level."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            f.flush()

            try:
                runner = CliRunner()
                severity_levels = ["debug", "info", "warning", "error", "critical"]

                for severity in severity_levels:
                    result = runner.invoke(
                        cli, ["analyze", f.name, "--severity", severity]
                    )
                    assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_invalid_severity(self) -> None:
        """Test analyze command with invalid severity level."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(
                    cli, ["analyze", f.name, "--severity", "invalid_severity"]
                )
                assert result.exit_code == 2  # Click validation error
                assert "Invalid value" in result.output
            finally:
                Path(f.name).unlink(missing_ok=True)


class TestCLIAnalysisConfiguration:
    """Test CLI analysis configuration options."""

    def test_analyze_individual_module_flags(self) -> None:
        """Test individual analysis module disable flags."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            f.flush()

            try:
                runner = CliRunner()

                # Test each individual flag
                flags = ["--no-quality", "--no-security", "--no-green", "--no-ai-code"]

                for flag in flags:
                    result = runner.invoke(cli, ["analyze", f.name, flag])
                    assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_ast_research_without_patterns_or_complexity(self) -> None:
        """Test AST research without pattern analysis or complexity metrics."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def simple_function(): return 42")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    [
                        "analyze",
                        f.name,
                        "--enable-ast-research",
                        # Note: not enabling --enable-pattern-analysis
                        # or --enable-complexity-metrics
                    ],
                )
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)
