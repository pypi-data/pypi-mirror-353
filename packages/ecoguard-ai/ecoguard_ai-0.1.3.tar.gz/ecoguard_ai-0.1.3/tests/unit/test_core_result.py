"""
Test suite for the result module.

This module tests the AnalysisResult class and related functionality.
"""

import json
from datetime import datetime

from ecoguard_ai.core.issue import Category, Impact, Issue, Severity
from ecoguard_ai.core.result import AnalysisResult


class TestAnalysisResult:
    """Tests for AnalysisResult class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.sample_issues = [
            Issue(
                rule_id="unused_variable",
                message="Variable 'x' is unused",
                severity=Severity.WARNING,
                category=Category.QUALITY,
                file_path="test.py",
                line=10,
                impact=Impact(maintainability=2),
            ),
            Issue(
                rule_id="hardcoded_secret",
                message="Hardcoded API key detected",
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                file_path="test.py",
                line=5,
                impact=Impact(security_risk=5),
            ),
            Issue(
                rule_id="inefficient_loop",
                message="Use enumerate() instead of range(len())",
                severity=Severity.INFO,
                category=Category.GREEN,
                file_path="test.py",
                line=15,
                impact=Impact(performance=2, carbon_impact=3, maintainability=1),
            ),
        ]

    def test_basic_initialization(self) -> None:
        """Test basic AnalysisResult initialization."""
        result = AnalysisResult(file_path="test.py")

        assert result.file_path == "test.py"
        assert result.issues == []
        assert isinstance(result.analysis_time, datetime)
        assert result.issue_count == 0

    def test_initialization_with_issues(self) -> None:
        """Test AnalysisResult initialization with issues."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        assert result.file_path == "test.py"
        assert len(result.issues) == 3
        assert result.issue_count == 3

    def test_add_issue(self) -> None:
        """Test adding issues to result."""
        result = AnalysisResult(file_path="test.py")

        issue = Issue(
            rule_id="test_rule",
            message="Test message",
            severity=Severity.ERROR,
            category=Category.QUALITY,
            file_path="test.py",
            line=1,
        )

        # Since AnalysisResult doesn't have add_issue method,
        # we test direct issue list manipulation
        result.issues.append(issue)
        assert len(result.issues) == 1
        assert result.issue_count == 1

    def test_issue_count_property(self) -> None:
        """Test issue count property."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        assert result.issue_count == 3

    def test_get_issues_by_severity(self) -> None:
        """Test getting issues by severity."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        critical_issues = result.get_issues_by_severity(Severity.CRITICAL)
        assert len(critical_issues) == 1
        assert critical_issues[0].rule_id == "hardcoded_secret"

        warning_issues = result.get_issues_by_severity(Severity.WARNING)
        assert len(warning_issues) == 1
        assert warning_issues[0].rule_id == "unused_variable"

        info_issues = result.get_issues_by_severity(Severity.INFO)
        assert len(info_issues) == 1
        assert info_issues[0].rule_id == "inefficient_loop"

    def test_get_issues_by_category(self) -> None:
        """Test getting issues by category."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        quality_issues = result.get_issues_by_category(Category.QUALITY)
        assert len(quality_issues) == 1
        assert quality_issues[0].rule_id == "unused_variable"

        security_issues = result.get_issues_by_category(Category.SECURITY)
        assert len(security_issues) == 1
        assert security_issues[0].rule_id == "hardcoded_secret"

        green_issues = result.get_issues_by_category(Category.GREEN)
        assert len(green_issues) == 1
        assert green_issues[0].rule_id == "inefficient_loop"

    def test_get_issues_by_rule(self) -> None:
        """Test getting issues by rule ID."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        unused_var_issues = result.get_issues_by_rule("unused_variable")
        assert len(unused_var_issues) == 1
        assert unused_var_issues[0].message == "Variable 'x' is unused"

    def test_severity_count_properties(self) -> None:
        """Test severity count properties."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        assert result.critical_count == 1
        assert result.error_count == 0
        assert result.warning_count == 1
        assert result.info_count == 1

    def test_calculate_green_score(self) -> None:
        """Test green score calculation."""
        # Test with no issues
        empty_result = AnalysisResult(file_path="test.py", issues=[])
        assert empty_result.calculate_green_score() == 100.0

        # Test with no green issues
        quality_issue = Issue(
            rule_id="quality_rule",
            message="Quality issue",
            severity=Severity.WARNING,
            category=Category.QUALITY,
            file_path="test.py",
            line=1,
        )
        no_green_result = AnalysisResult(file_path="test.py", issues=[quality_issue])
        assert no_green_result.calculate_green_score() == 100.0

        # Test with green issues
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        score = result.calculate_security_score()
        assert isinstance(score, float)
        assert 0 <= score <= 100
        # Should be less than 100 due to critical security issue
        assert score < 100

    def test_green_score_with_error_level_issues(self) -> None:
        """Test green score calculation with error level green issues."""
        error_green_issue = Issue(
            rule_id="energy_inefficient",
            message="Energy inefficient operation",
            severity=Severity.ERROR,
            category=Category.GREEN,
            file_path="test.py",
            line=1,
        )

        result = AnalysisResult(file_path="test.py", issues=[error_green_issue])

        score = result.calculate_green_score()
        assert score == 85.0  # 100 - 15 penalty for ERROR level

    def test_green_score_with_info_level_issues(self) -> None:
        """Test green score calculation with info level green issues."""
        info_green_issue = Issue(
            rule_id="minor_inefficiency",
            message="Minor inefficiency detected",
            severity=Severity.INFO,
            category=Category.GREEN,
            file_path="test.py",
            line=1,
        )

        result = AnalysisResult(file_path="test.py", issues=[info_green_issue])

        score = result.calculate_green_score()
        assert score == 95.0  # 100 - 5 penalty for INFO level

    def test_security_score_with_error_level_issues(self) -> None:
        """Test security score calculation with error level security issues."""
        error_security_issue = Issue(
            rule_id="sql_injection",
            message="SQL injection vulnerability",
            severity=Severity.ERROR,
            category=Category.SECURITY,
            file_path="test.py",
            line=1,
        )

        result = AnalysisResult(file_path="test.py", issues=[error_security_issue])

        score = result.calculate_security_score()
        assert score == 80.0  # 100 - 20 penalty for ERROR level

    def test_security_score_with_warning_level_issues(self) -> None:
        """Test security score calculation with warning level security issues."""
        warning_security_issue = Issue(
            rule_id="weak_crypto",
            message="Weak cryptographic algorithm",
            severity=Severity.WARNING,
            category=Category.SECURITY,
            file_path="test.py",
            line=1,
        )

        result = AnalysisResult(file_path="test.py", issues=[warning_security_issue])

        score = result.calculate_security_score()
        assert score == 90.0  # 100 - 10 penalty for WARNING level

    def test_security_score_with_info_level_issues(self) -> None:
        """Test security score calculation with info level security issues."""
        info_security_issue = Issue(
            rule_id="security_best_practice",
            message="Consider using secure headers",
            severity=Severity.INFO,
            category=Category.SECURITY,
            file_path="test.py",
            line=1,
        )

        result = AnalysisResult(file_path="test.py", issues=[info_security_issue])

        score = result.calculate_security_score()
        assert score == 97.0  # 100 - 3 penalty for INFO level

    def test_to_dict(self) -> None:
        """Test converting result to dictionary."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        data = result.to_dict()
        assert isinstance(data, dict)
        assert "file_path" in data
        assert "analysis_time" in data
        assert "summary" in data
        assert "issues" in data

        assert data["file_path"] == "test.py"
        assert len(data["issues"]) == 3
        assert data["summary"]["total_issues"] == 3

    def test_to_dict_with_metadata(self) -> None:
        """Test to_dict method includes metadata."""
        metadata = {"test_key": "test_value", "analyzer_version": "1.0.0"}
        result = AnalysisResult(
            file_path="test.py", issues=self.sample_issues, metadata=metadata
        )

        data = result.to_dict()
        assert "metadata" in data
        assert data["metadata"] == metadata

    def test_to_json(self) -> None:
        """Test converting result to JSON."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        json_str = result.to_json()
        assert isinstance(json_str, str)

        # Should be valid JSON
        data = json.loads(json_str)
        assert "file_path" in data
        assert "summary" in data
        assert "issues" in data

    def test_to_json_with_indent(self) -> None:
        """Test converting result to formatted JSON."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        json_str = result.to_json(indent=2)
        assert isinstance(json_str, str)
        assert "\n" in json_str  # Should be formatted

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["file_path"] == "test.py"

    def test_from_dict(self) -> None:
        """Test creating result from dictionary."""
        original_result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        data = original_result.to_dict()
        restored_result = AnalysisResult.from_dict(data)

        assert restored_result.file_path == original_result.file_path
        assert len(restored_result.issues) == len(original_result.issues)
        assert restored_result.issue_count == original_result.issue_count

    def test_from_json(self) -> None:
        """Test creating result from JSON."""
        original_result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        json_str = original_result.to_json()
        restored_result = AnalysisResult.from_json(json_str)

        assert restored_result.file_path == original_result.file_path
        assert len(restored_result.issues) == len(original_result.issues)
        assert restored_result.issue_count == original_result.issue_count

    def test_empty_result(self) -> None:
        """Test result with no issues."""
        result = AnalysisResult(file_path="test.py")

        assert result.issue_count == 0
        assert result.calculate_green_score() == 100.0
        assert result.calculate_security_score() == 100.0

    def test_result_with_mixed_severities(self) -> None:
        """Test result calculations with mixed severity issues."""
        mixed_issues = [
            Issue(
                rule_id="critical_issue",
                message="Critical problem",
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                file_path="test.py",
                line=1,
            ),
            Issue(
                rule_id="error_issue",
                message="Error problem",
                severity=Severity.ERROR,
                category=Category.QUALITY,
                file_path="test.py",
                line=2,
            ),
            Issue(
                rule_id="warning_issue",
                message="Warning problem",
                severity=Severity.WARNING,
                category=Category.GREEN,
                file_path="test.py",
                line=3,
            ),
            Issue(
                rule_id="info_issue",
                message="Info problem",
                severity=Severity.INFO,
                category=Category.AI_CODE,
                file_path="test.py",
                line=4,
            ),
        ]

        result = AnalysisResult(file_path="test.py", issues=mixed_issues)

        assert result.critical_count == 1
        assert result.error_count == 1
        assert result.warning_count == 1
        assert result.info_count == 1

        # Scores should be reduced due to issues
        assert result.calculate_green_score() < 100
        assert result.calculate_security_score() < 100

    def test_result_string_representation(self) -> None:
        """Test string representation of result."""
        result = AnalysisResult(file_path="test.py", issues=self.sample_issues)

        str_repr = str(result)
        assert "AnalysisResult" in str_repr
        assert "test.py" in str_repr

    def test_helper_functions(self) -> None:
        """Test the private helper functions in result module."""
        from ecoguard_ai.core.issue import Category, Issue, Severity
        from ecoguard_ai.core.result import (
            _get_severity_enum,
            _matches_category,
            _matches_severity,
        )

        # Test _matches_severity
        issue = Issue(
            rule_id="test",
            category="quality",
            severity="warning",
            message="Test",
            file_path="test.py",
            line=1,
        )

        assert _matches_severity(issue, Severity.WARNING) is True
        assert _matches_severity(issue, Severity.ERROR) is False

        # Test with invalid severity string
        issue_invalid = Issue(
            rule_id="test",
            category="quality",
            severity="invalid_severity",
            message="Test",
            file_path="test.py",
            line=1,
        )
        assert _matches_severity(issue_invalid, Severity.WARNING) is False

        # Test _matches_category
        assert _matches_category(issue, Category.QUALITY) is True
        assert _matches_category(issue, Category.SECURITY) is False

        # Test with invalid category string
        issue_invalid_cat = Issue(
            rule_id="test",
            category="invalid_category",
            severity="warning",
            message="Test",
            file_path="test.py",
            line=1,
        )
        assert _matches_category(issue_invalid_cat, Category.QUALITY) is False

        # Test _get_severity_enum
        assert _get_severity_enum(issue) == Severity.WARNING
        assert _get_severity_enum(issue_invalid) == Severity.INFO  # Default fallback

    def test_analysis_result_filter_edge_cases(self) -> None:
        """Test edge cases in AnalysisResult filtering methods."""
        from ecoguard_ai.core.issue import Category, Issue, Severity
        from ecoguard_ai.core.result import AnalysisResult

        # Create result with mixed severity/category types
        issues = [
            Issue(
                rule_id="test1",
                category="quality",  # String
                severity=Severity.ERROR,  # Enum
                message="Test 1",
                file_path="test.py",
                line=1,
            ),
            Issue(
                rule_id="test2",
                category=Category.SECURITY,  # Enum
                severity="warning",  # String
                message="Test 2",
                file_path="test.py",
                line=2,
            ),
        ]

        result = AnalysisResult(file_path="test.py", issues=issues)

        # Test filtering with mixed types
        error_issues = result.get_issues_by_severity(Severity.ERROR)
        assert len(error_issues) == 1
        assert error_issues[0].rule_id == "test1"

        warning_issues = result.get_issues_by_severity(Severity.WARNING)
        assert len(warning_issues) == 1
        assert warning_issues[0].rule_id == "test2"

        quality_issues = result.get_issues_by_category(Category.QUALITY)
        assert len(quality_issues) == 1
        assert quality_issues[0].rule_id == "test1"

    def test_project_analysis_result_filtering(self) -> None:
        """Test ProjectAnalysisResult filtering capabilities."""
        from ecoguard_ai.core.issue import Category, Issue, Severity
        from ecoguard_ai.core.result import AnalysisResult, ProjectAnalysisResult

        # Create multiple file results
        issues1 = [
            Issue(
                rule_id="test1",
                category=Category.QUALITY,
                severity=Severity.ERROR,
                message="Error in file 1",
                file_path="file1.py",
                line=1,
            )
        ]

        issues2 = [
            Issue(
                rule_id="test2",
                category=Category.SECURITY,
                severity=Severity.WARNING,
                message="Warning in file 2",
                file_path="file2.py",
                line=1,
            )
        ]

        result1 = AnalysisResult(file_path="file1.py", issues=issues1)
        result2 = AnalysisResult(file_path="file2.py", issues=issues2)

        project_result = ProjectAnalysisResult(
            project_path="/test/project",
            file_results=[result1, result2],
        )

        # Test has_errors
        assert project_result.has_errors() is True  # Has ERROR severity

        # Test get_all_issues
        all_issues = project_result.get_all_issues()
        assert len(all_issues) == 2

        # Test filtering across all files
        error_issues = [
            issue for issue in all_issues if issue.severity == Severity.ERROR
        ]
        assert len(error_issues) == 1
