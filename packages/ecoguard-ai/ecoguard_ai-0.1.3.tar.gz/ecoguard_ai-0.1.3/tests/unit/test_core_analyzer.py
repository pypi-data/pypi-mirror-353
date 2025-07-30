"""Tests for the core analyzer functionality."""

import pytest

from ecoguard_ai.core.analyzer import AnalysisConfig, EcoGuardAnalyzer
from ecoguard_ai.core.result import AnalysisResult


class TestAnalysisConfig:
    """Tests for AnalysisConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = AnalysisConfig()

        assert config.include_patterns == ["*.py"]
        assert "__pycache__/*" in config.exclude_patterns
        assert config.enable_quality is True
        assert config.enable_security is True
        assert config.enable_green is True
        assert config.enable_ai_code is True
        assert config.output_format == "json"
        assert config.min_severity == "info"

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = AnalysisConfig(
            include_patterns=["*.py", "*.pyi"],
            enable_security=False,
            output_format="text",
            min_severity="warning",
        )

        assert config.include_patterns == ["*.py", "*.pyi"]
        assert config.enable_security is False
        assert config.output_format == "text"
        assert config.min_severity == "warning"


class TestEcoGuardAnalyzer:
    """Tests for EcoGuardAnalyzer."""

    def test_analyzer_initialization(self) -> None:
        """Test analyzer initialization with default config."""
        analyzer = EcoGuardAnalyzer()

        assert analyzer.config is not None
        assert isinstance(analyzer.config, AnalysisConfig)
        # Note: _analyzers list will be empty since placeholder analyzers
        # return no issues
        assert isinstance(analyzer._analyzers, list)

    def test_analyzer_with_custom_config(self) -> None:
        """Test analyzer initialization with custom config."""
        config = AnalysisConfig(enable_security=False)
        analyzer = EcoGuardAnalyzer(config)

        assert analyzer.config.enable_security is False

    def test_analyze_file_nonexistent(self, analyzer) -> None:
        """Test analyzing a non-existent file."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_file("nonexistent.py")

    def test_analyze_file_non_python(self, analyzer, temp_dir) -> None:
        """Test analyzing a non-Python file."""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("Hello, world!")

        with pytest.raises(ValueError, match="Only Python files are supported"):
            analyzer.analyze_file(txt_file)

    def test_analyze_valid_file(self, analyzer, sample_python_file) -> None:
        """Test analyzing a valid Python file."""
        result = analyzer.analyze_file(sample_python_file)

        assert isinstance(result, AnalysisResult)
        assert result.file_path == str(sample_python_file)
        assert isinstance(result.issues, list)
        assert isinstance(result.metadata, dict)
        assert "file_path" in result.metadata
        assert "file_size" in result.metadata
        assert "line_count" in result.metadata

    def test_analyze_file_with_syntax_error(self, analyzer, temp_dir) -> None:
        """Test analyzing a file with syntax errors."""
        bad_file = temp_dir / "bad.py"
        bad_file.write_text(
            "def broken_function(\n    pass"
        )  # Missing closing parenthesis

        result = analyzer.analyze_file(bad_file)

        assert isinstance(result, AnalysisResult)
        assert len(result.issues) == 1
        assert result.issues[0].rule_id == "syntax_error"
        assert result.issues[0].severity.value == "error"

    def test_analyze_directory_nonexistent(self, analyzer) -> None:
        """Test analyzing a non-existent directory."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_directory("nonexistent_dir")

    def test_analyze_directory_empty(self, analyzer, temp_dir) -> None:
        """Test analyzing an empty directory."""
        results = analyzer.analyze_directory(temp_dir)

        assert isinstance(results, list)
        assert len(results) == 0

    def test_analyze_directory_with_files(self, analyzer, temp_dir) -> None:
        """Test analyzing a directory with Python files."""
        # Create multiple Python files
        file1 = temp_dir / "file1.py"
        file1.write_text("print('Hello from file1')")

        file2 = temp_dir / "file2.py"
        file2.write_text("print('Hello from file2')")

        # Create a subdirectory with a Python file
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        file3 = subdir / "file3.py"
        file3.write_text("print('Hello from file3')")

        # Create a non-Python file (should be ignored)
        txt_file = temp_dir / "ignore.txt"
        txt_file.write_text("This should be ignored")

        results = analyzer.analyze_directory(temp_dir)

        assert isinstance(results, list)
        assert len(results) == 3  # Only Python files

        file_paths = [r.file_path for r in results]
        assert str(file1) in file_paths
        assert str(file2) in file_paths
        assert str(file3) in file_paths
        assert str(txt_file) not in file_paths

    def test_minimal_analyzer_no_issues(
        self, minimal_analyzer, sample_python_file
    ) -> None:
        """Test that analyzer with all modules disabled finds no issues."""
        result = minimal_analyzer.analyze_file(sample_python_file)

        assert isinstance(result, AnalysisResult)
        assert len(result.issues) == 0  # No analyzers enabled, so no issues
