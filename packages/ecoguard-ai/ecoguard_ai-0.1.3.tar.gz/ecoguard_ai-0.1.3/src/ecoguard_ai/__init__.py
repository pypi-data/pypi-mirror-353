"""
EcoGuard AI: AI-augmented software development pipeline solution

A unified intelligence layer for analyzing code quality, security,
and environmental sustainability in both human-written and AI-generated code.
"""

__version__ = "0.1.2"
__author__ = "EcoGuard AI Team"
__email__ = "team@ecoguard-ai.org"
__license__ = "MIT"

from ecoguard_ai.core.analyzer import EcoGuardAnalyzer
from ecoguard_ai.core.issue import Issue, Severity
from ecoguard_ai.core.result import AnalysisResult

__all__ = [
    "EcoGuardAnalyzer",
    "Issue",
    "Severity",
    "AnalysisResult",
]
