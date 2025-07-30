"""
Issue representation for EcoGuard AI analysis results.

This module defines the core Issue class and related enums used throughout
the analysis pipeline to represent findings and their metadata.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class Severity(Enum):
    """Severity levels for issues found during analysis."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def __lt__(self, other: Any) -> bool:
        """Enable comparison between severity levels."""
        if not isinstance(other, Severity):
            return NotImplemented

        order = [
            Severity.DEBUG,
            Severity.INFO,
            Severity.WARNING,
            Severity.ERROR,
            Severity.CRITICAL,
        ]

        return order.index(self) < order.index(other)


class Category(Enum):
    """Categories of analysis that can generate issues."""

    QUALITY = "quality"
    SECURITY = "security"
    GREEN = "green"
    AI_CODE = "ai_code"
    SYNTAX = "syntax"
    SYSTEM = "system"


@dataclass
class Impact:
    """Represents the potential impact of an issue."""

    # Performance impact (0.0 to 1.0)
    performance: float = 0.0

    # Security risk level (0.0 to 1.0)
    security_risk: float = 0.0

    # Carbon footprint impact (estimated grams CO2/hour)
    carbon_impact: float = 0.0

    # Maintainability impact (0.0 to 1.0)
    maintainability: float = 0.0

    # Financial cost impact (estimated cost increase)
    cost_impact: float = 0.0


@dataclass
class Fix:
    """Represents an automated or suggested fix for an issue."""

    # Description of the fix
    description: str

    # Code replacement (for automated fixes)
    replacement_code: Optional[str] = None

    # Whether this fix can be applied automatically
    can_auto_fix: bool = False

    # Confidence level in the fix (0.0 to 1.0)
    confidence: float = 0.0

    # Additional instructions for manual fixes
    instructions: Optional[str] = None


@dataclass
class Issue:
    """
    Represents a single issue found during analysis.

    This is the core data structure used throughout EcoGuard AI to represent
    findings from various analyzers.
    """

    # Core identification
    rule_id: str
    category: Union[str, Category]  # Will be converted to Category enum
    severity: Union[str, Severity]  # Will be converted to Severity enum
    message: str

    # Location information
    file_path: str
    line: int
    column: int = 1
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    # Additional context
    description: Optional[str] = None
    code_snippet: Optional[str] = None
    suggested_fix: Optional[Fix] = None
    impact: Optional[Impact] = None

    # Metadata
    rule_name: Optional[str] = None
    rule_description: Optional[str] = None
    references: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    # AI-specific metadata
    ai_generated: bool = False
    ai_confidence: Optional[float] = None

    # Timestamps
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if self.references is None:
            self.references = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

        # Convert string enums to proper enums
        if isinstance(self.severity, str):
            try:
                self.severity = Severity(self.severity.lower())
            except ValueError:
                # Handle unknown severity values
                self.severity = Severity.INFO
        if isinstance(self.category, str):
            try:
                self.category = Category(self.category.lower())
            except ValueError:
                # Handle unknown category values
                self.category = Category.SYSTEM

    @property
    def severity_score(self) -> int:
        """Get numeric severity score for sorting/filtering."""
        severity_scores = {
            Severity.DEBUG: 1,
            Severity.INFO: 2,
            Severity.WARNING: 3,
            Severity.ERROR: 4,
            Severity.CRITICAL: 5,
        }
        # Ensure severity is a Severity enum
        if isinstance(self.severity, Severity):
            return severity_scores.get(self.severity, 0)
        else:
            # Convert string to enum first
            try:
                severity_enum = Severity(self.severity.lower())
                return severity_scores.get(severity_enum, 0)
            except (ValueError, AttributeError):
                return 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary representation."""
        return {
            "rule_id": self.rule_id,
            "category": (
                self.category.value
                if isinstance(self.category, Category)
                else self.category
            ),
            "severity": (
                self.severity.value
                if isinstance(self.severity, Severity)
                else self.severity
            ),
            "message": self.message,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "description": self.description,
            "code_snippet": self.code_snippet,
            "suggested_fix": (
                self.suggested_fix.__dict__ if self.suggested_fix else None
            ),
            "impact": self.impact.__dict__ if self.impact else None,
            "rule_name": self.rule_name,
            "rule_description": self.rule_description,
            "references": self.references,
            "tags": self.tags,
            "ai_generated": self.ai_generated,
            "ai_confidence": self.ai_confidence,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
        """Create issue from dictionary representation."""
        # Handle nested objects
        suggested_fix = None
        if data.get("suggested_fix"):
            suggested_fix = Fix(**data["suggested_fix"])

        impact = None
        if data.get("impact"):
            impact = Impact(**data["impact"])

        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])

        return cls(
            rule_id=data["rule_id"],
            category=data["category"],
            severity=data["severity"],
            message=data["message"],
            file_path=data["file_path"],
            line=data["line"],
            column=data.get("column", 1),
            end_line=data.get("end_line"),
            end_column=data.get("end_column"),
            description=data.get("description"),
            code_snippet=data.get("code_snippet"),
            suggested_fix=suggested_fix,
            impact=impact,
            rule_name=data.get("rule_name"),
            rule_description=data.get("rule_description"),
            references=data.get("references", []),
            tags=data.get("tags", []),
            ai_generated=data.get("ai_generated", False),
            ai_confidence=data.get("ai_confidence"),
            created_at=created_at,
        )

    def __str__(self) -> str:
        """String representation of the issue."""
        severity_str = (
            self.severity.value
            if isinstance(self.severity, Severity)
            else str(self.severity)
        )
        return (
            f"{self.file_path}:{self.line}:{self.column}: {severity_str}: "
            f"{self.message} [{self.rule_id}]"
        )
