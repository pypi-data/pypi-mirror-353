"""
Base analyzer interface for EcoGuard AI analysis modules.

This module defines the abstract base class that all specific analyzers
must implement to integrate with the EcoGuard AI analysis pipeline.
"""

import ast
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ecoguard_ai.core.issue import Issue


class BaseAnalyzer(ABC):
    """
    Abstract base class for all EcoGuard AI analyzers.

    Each specific analyzer (quality, security, green, ai_code) must inherit
    from this class and implement the analyze method.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
        self.rules: Dict[str, "BaseRule"] = {}

    @abstractmethod
    def analyze(self, tree: ast.AST, source_code: str, file_path: str) -> List[Issue]:
        """
        Analyze the given AST and return a list of issues.

        Args:
            tree: The parsed AST of the source code
            source_code: The original source code as a string
            file_path: Path to the file being analyzed

        Returns:
            List of Issue objects representing found problems
        """
        pass

    def register_rule(self, rule: "BaseRule") -> None:
        """Register a rule with this analyzer."""
        self.rules[rule.rule_id] = rule

    def enable_rule(self, rule_id: str) -> None:
        """Enable a specific rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True

    def disable_rule(self, rule_id: str) -> None:
        """Disable a specific rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False


class BaseRule(ABC):
    """
    Abstract base class for individual analysis rules.

    Each rule implements specific logic for detecting a particular type of issue.
    """

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: str,
        severity: str = "warning",
        tags: Optional[List[str]] = None,
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.category = category
        self.severity = severity
        self.tags = tags or []
        self.enabled = True

    @abstractmethod
    def check(self, node: ast.AST, source_code: str, file_path: str) -> List[Issue]:
        """
        Check a specific AST node for issues.

        Args:
            node: The AST node to check
            source_code: The original source code
            file_path: Path to the file being analyzed

        Returns:
            List of Issue objects if problems are found
        """
        pass

    def create_issue(
        self, message: str, node: ast.AST, file_path: str, **kwargs: Any
    ) -> Issue:
        """
        Helper method to create an Issue from a rule violation.

        Args:
            message: Description of the issue
            node: The AST node where the issue was found
            file_path: Path to the file
            **kwargs: Additional Issue parameters

        Returns:
            Issue object representing the problem
        """
        return Issue(
            rule_id=self.rule_id,
            category=self.category,
            severity=self.severity,
            message=message,
            file_path=file_path,
            line=getattr(node, "lineno", 1),
            column=getattr(node, "col_offset", 0),
            end_line=getattr(node, "end_lineno", None),
            end_column=getattr(node, "end_col_offset", None),
            rule_name=self.name,
            rule_description=self.description,
            tags=self.tags.copy(),
            **kwargs,
        )


class ASTVisitorRule(BaseRule, ast.NodeVisitor):
    """
    Base class for rules that use the visitor pattern to traverse the AST.

    This is the most common type of rule for static analysis.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.issues: List[Issue] = []
        self.current_source_code: str = ""
        self.current_file_path: str = ""

    def reset(self, file_path: str, source_code: str) -> None:
        """
        Reset rule state for analyzing a new file.

        Args:
            file_path: Path to the file being analyzed
            source_code: Source code content
        """
        self.issues = []
        self.current_file_path = file_path
        self.current_source_code = source_code

    def finalize(self) -> None:
        """
        Called after visiting all nodes. Override to perform final analysis.
        """
        pass

    def check(self, node: ast.AST, source_code: str, file_path: str) -> List[Issue]:
        """
        Run the visitor pattern on the AST to find issues.

        Args:
            node: Root AST node (typically ast.Module)
            source_code: Original source code
            file_path: Path to the file

        Returns:
            List of issues found
        """
        self.reset(file_path, source_code)
        self.visit(node)
        self.finalize()
        return self.issues.copy()

    def add_issue(self, message: str, node: ast.AST, **kwargs: Any) -> None:
        """
        Add an issue to the current list.

        Args:
            message: Issue description
            node: AST node where issue was found
            **kwargs: Additional Issue parameters
        """
        issue = self.create_issue(message, node, self.current_file_path, **kwargs)
        self.issues.append(issue)


def get_source_segment(source_code: str, node: ast.AST) -> str:
    """
    Extract the source code segment for a given AST node.

    Args:
        source_code: Complete source code
        node: AST node

    Returns:
        Source code segment as string
    """
    if not (hasattr(node, "lineno") and hasattr(node, "end_lineno")):
        return ""

    lines = source_code.splitlines()
    start_line = node.lineno - 1  # Convert to 0-based indexing
    end_line = node.end_lineno - 1 if node.end_lineno else start_line

    if start_line < 0 or start_line >= len(lines):
        return ""

    if start_line == end_line:
        # Single line
        line = lines[start_line]
        start_col: int = int(getattr(node, "col_offset", 0))
        end_col_attr = getattr(node, "end_col_offset", len(line))
        end_col: int = int(end_col_attr) if end_col_attr is not None else len(line)
        return str(line[start_col:end_col])
    else:
        # Multiple lines
        result_lines = []
        for i in range(start_line, min(end_line + 1, len(lines))):
            if i == start_line:
                # First line
                line_start_col: int = int(getattr(node, "col_offset", 0))
                result_lines.append(lines[i][line_start_col:])
            elif i == end_line:
                # Last line
                end_col_attr = getattr(node, "end_col_offset", len(lines[i]))
                line_end_col: int = (
                    int(end_col_attr) if end_col_attr is not None else len(lines[i])
                )
                result_lines.append(lines[i][:line_end_col])
            else:
                # Middle lines
                result_lines.append(lines[i])

        return "\n".join(result_lines)
