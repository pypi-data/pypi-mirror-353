"""
Analysis result representation for EcoGuard AI.

This module defines the AnalysisResult class which aggregates issues
and metadata from analysis runs.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ecoguard_ai.core.issue import Category, Issue, Severity


def _matches_severity(issue: Issue, severity: Severity) -> bool:
    """Helper function to safely compare issue severity with target severity."""
    if isinstance(issue.severity, Severity):
        return issue.severity == severity
    if isinstance(issue.severity, str):
        try:
            return Severity(issue.severity.lower()) == severity
        except ValueError:
            pass
    return False


def _matches_category(issue: Issue, category: Category) -> bool:
    """Helper function to safely compare issue category with target category."""
    if isinstance(issue.category, Category):
        return issue.category == category
    if isinstance(issue.category, str):
        try:
            return Category(issue.category.lower()) == category
        except ValueError:
            pass
    return False


def _get_severity_enum(issue: Issue) -> Severity:
    """Helper function to get Severity enum from issue."""
    if isinstance(issue.severity, Severity):
        return issue.severity
    if isinstance(issue.severity, str):
        try:
            return Severity(issue.severity.lower())
        except ValueError:
            pass
    return Severity.INFO


@dataclass
class AnalysisResult:
    """
    Represents the result of analyzing a single file or project.

    This class aggregates all issues found during analysis along with
    metadata about the analysis run.
    """

    file_path: str
    issues: List[Issue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_time: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if self.analysis_time is None:
            self.analysis_time = datetime.now(timezone.utc)

    @property
    def issue_count(self) -> int:
        """Total number of issues found."""
        return len(self.issues)

    @property
    def error_count(self) -> int:
        """Number of error-level issues."""
        return len([i for i in self.issues if _matches_severity(i, Severity.ERROR)])

    @property
    def warning_count(self) -> int:
        """Number of warning-level issues."""
        return len([i for i in self.issues if _matches_severity(i, Severity.WARNING)])

    @property
    def info_count(self) -> int:
        """Number of info-level issues."""
        return len([i for i in self.issues if _matches_severity(i, Severity.INFO)])

    @property
    def critical_count(self) -> int:
        """Number of critical-level issues."""
        return len([i for i in self.issues if _matches_severity(i, Severity.CRITICAL)])

    def get_issues_by_category(self, category: Category) -> List[Issue]:
        """Get all issues for a specific category."""
        return [i for i in self.issues if _matches_category(i, category)]

    def get_issues_by_severity(self, severity: Severity) -> List[Issue]:
        """Get all issues for a specific severity level."""
        return [i for i in self.issues if _matches_severity(i, severity)]

    def get_issues_by_rule(self, rule_id: str) -> List[Issue]:
        """Get all issues for a specific rule."""
        return [i for i in self.issues if i.rule_id == rule_id]

    def has_errors(self) -> bool:
        """Check if any error-level or critical issues were found."""
        return any(
            _get_severity_enum(i) in [Severity.ERROR, Severity.CRITICAL]
            for i in self.issues
        )

    def calculate_green_score(self) -> float:
        """
        Calculate a green software score (0-100) based on found issues.

        Returns:
            Score from 0 (worst) to 100 (best) representing green software practices
        """
        if not self.issues:
            return 100.0

        green_issues = self.get_issues_by_category(Category.GREEN)
        if not green_issues:
            return 100.0

        # Simple scoring based on severity and count
        penalty = 0
        for issue in green_issues:
            severity = _get_severity_enum(issue)
            if severity == Severity.CRITICAL:
                penalty += 20
            elif severity == Severity.ERROR:
                penalty += 15
            elif severity == Severity.WARNING:
                penalty += 10
            elif severity == Severity.INFO:
                penalty += 5

        score = max(0.0, 100.0 - penalty)
        return score

    def calculate_security_score(self) -> float:
        """
        Calculate a security score (0-100) based on found issues.

        Returns:
            Score from 0 (worst) to 100 (best) representing security posture
        """
        if not self.issues:
            return 100.0

        security_issues = self.get_issues_by_category(Category.SECURITY)
        if not security_issues:
            return 100.0

        # Security issues are weighted more heavily
        penalty = 0
        for issue in security_issues:
            severity = _get_severity_enum(issue)
            if severity == Severity.CRITICAL:
                penalty += 30
            elif severity == Severity.ERROR:
                penalty += 20
            elif severity == Severity.WARNING:
                penalty += 10
            elif severity == Severity.INFO:
                penalty += 3

        score = max(0.0, 100.0 - penalty)
        return score

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation."""
        return {
            "file_path": self.file_path,
            "analysis_time": (
                self.analysis_time.isoformat() if self.analysis_time else None
            ),
            "summary": {
                "total_issues": self.issue_count,
                "critical": self.critical_count,
                "error": self.error_count,
                "warning": self.warning_count,
                "info": self.info_count,
                "green_score": self.calculate_green_score(),
                "security_score": self.calculate_security_score(),
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Create result from dictionary representation."""
        issues = [Issue.from_dict(issue_data) for issue_data in data.get("issues", [])]

        analysis_time = None
        if data.get("analysis_time"):
            analysis_time = datetime.fromisoformat(data["analysis_time"])

        return cls(
            file_path=data["file_path"],
            issues=issues,
            metadata=data.get("metadata", {}),
            analysis_time=analysis_time,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AnalysisResult":
        """Create result from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class ProjectAnalysisResult:
    """
    Represents the aggregated results of analyzing an entire project.

    This class combines multiple file analysis results into a project-wide view.
    """

    project_path: str
    file_results: List[AnalysisResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_time: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if self.analysis_time is None:
            self.analysis_time = datetime.now(timezone.utc)

    @property
    def total_files(self) -> int:
        """Total number of files analyzed."""
        return len(self.file_results)

    @property
    def total_issues(self) -> int:
        """Total number of issues across all files."""
        return sum(result.issue_count for result in self.file_results)

    @property
    def all_issues(self) -> List[Issue]:
        """Get all issues from all files."""
        issues = []
        for result in self.file_results:
            issues.extend(result.issues)
        return issues

    def get_summary_by_category(self) -> Dict[str, int]:
        """Get issue counts by category across all files."""
        summary = {}
        for category in Category:
            count = sum(
                len(result.get_issues_by_category(category))
                for result in self.file_results
            )
            summary[category.value] = count
        return summary

    def get_summary_by_severity(self) -> Dict[str, int]:
        """Get issue counts by severity across all files."""
        summary = {}
        for severity in Severity:
            count = sum(
                len(result.get_issues_by_severity(severity))
                for result in self.file_results
            )
            summary[severity.value] = count
        return summary

    def calculate_overall_green_score(self) -> float:
        """Calculate overall green software score for the project."""
        if not self.file_results:
            return 100.0

        scores = [result.calculate_green_score() for result in self.file_results]
        return sum(scores) / len(scores)

    def calculate_overall_security_score(self) -> float:
        """Calculate overall security score for the project."""
        if not self.file_results:
            return 100.0

        scores = [result.calculate_security_score() for result in self.file_results]
        return sum(scores) / len(scores)

    def has_errors(self) -> bool:
        """Check if the project has any error-level or critical issues."""
        for result in self.file_results:
            if result.error_count > 0 or result.critical_count > 0:
                return True
        return False

    def get_all_issues(self) -> List[Issue]:
        """Get all issues from all files (same as all_issues property but as method)."""
        return self.all_issues

    def to_dict(self) -> Dict[str, Any]:
        """Convert project result to dictionary representation."""
        return {
            "project_path": self.project_path,
            "analysis_time": (
                self.analysis_time.isoformat() if self.analysis_time else None
            ),
            "summary": {
                "total_files": self.total_files,
                "total_issues": self.total_issues,
                "by_category": self.get_summary_by_category(),
                "by_severity": self.get_summary_by_severity(),
                "overall_green_score": self.calculate_overall_green_score(),
                "overall_security_score": self.calculate_overall_security_score(),
            },
            "file_results": [result.to_dict() for result in self.file_results],
            "metadata": self.metadata,
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert project result to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
