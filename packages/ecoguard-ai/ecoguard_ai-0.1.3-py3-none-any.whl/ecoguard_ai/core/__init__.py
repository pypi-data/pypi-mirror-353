"""Core module initialization."""

from ecoguard_ai.core.analyzer import AnalysisConfig, EcoGuardAnalyzer
from ecoguard_ai.core.issue import Category, Fix, Impact, Issue, Severity
from ecoguard_ai.core.result import AnalysisResult, ProjectAnalysisResult

__all__ = [
    "EcoGuardAnalyzer",
    "AnalysisConfig",
    "Issue",
    "Severity",
    "Category",
    "Impact",
    "Fix",
    "AnalysisResult",
    "ProjectAnalysisResult",
]
