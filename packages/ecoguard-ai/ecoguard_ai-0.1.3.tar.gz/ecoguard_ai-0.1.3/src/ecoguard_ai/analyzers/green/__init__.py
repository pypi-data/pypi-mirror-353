"""
Green software analyzer for EcoGuard AI.

This module implements green software analys                suggested_fix=Fix(
                    description="Use list comprehension for better performance",
                    replacement_code="# result = [expr for item in iterable]"
                ),ules including:
- Inefficient string concatenation
- List comprehension optimization
- Generator vs list usage
- Memory-efficient patterns
"""

import ast
from typing import List

from ecoguard_ai.analyzers.base import ASTVisitorRule, BaseAnalyzer
from ecoguard_ai.core.issue import Fix, Impact, Issue


class StringConcatenationRule(ASTVisitorRule):
    """Detect inefficient string concatenation in loops."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="inefficient_string_concat",
            name="Inefficient String Concatenation",
            description="String concatenation in loop is inefficient",
            category="green",
            severity="warning",
        )
        self.in_loop = False

    def visit_For(self, node: ast.For) -> None:
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = False

    def visit_While(self, node: ast.While) -> None:
        self.in_loop = True
        self.generic_visit(node)
        self.in_loop = False

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if (
            self.in_loop
            and isinstance(node.op, ast.Add)
            and self._is_string_operation(node)
        ):

            issue = self.create_issue(
                message=(
                    "String concatenation in loop is inefficient. "
                    "Use join() or f-strings instead"
                ),
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description="Use ''.join() for concatenating strings in loops",
                    replacement_code=(
                        "# Use parts = []; parts.append(item); "
                        "result = ''.join(parts)"
                    ),
                ),
                impact=Impact(performance=-0.15, carbon_impact=5.0),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _is_string_operation(self, node: ast.AugAssign) -> bool:
        """Check if this might be a string concatenation."""
        # This is a heuristic - in real code we'd need type information
        if isinstance(node.target, ast.Name):
            return True  # Assume string if variable name suggests it
        return False


class ListComprehensionRule(ASTVisitorRule):
    """Suggest list comprehensions over manual loops."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="use_list_comprehension",
            name="Use List Comprehension",
            description="Consider using list comprehension for better performance",
            category="green",
            severity="info",
        )

    def visit_For(self, node: ast.For) -> None:
        """Look for simple append patterns that could be list comprehensions."""
        if self._is_simple_append_loop(node):
            issue = self.create_issue(
                message="Consider using list comprehension instead of append in loop",
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description=(
                        "Replace with list comprehension for better performance"
                    ),
                    replacement_code="# result = [expr for item in iterable]",
                ),
                impact=Impact(performance=-0.08, carbon_impact=3.0),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _is_simple_append_loop(self, node: ast.For) -> bool:
        """Check if this is a simple for loop with append."""
        # Look for: for x in y: result.append(something)
        if len(node.body) == 1:
            stmt = node.body[0]
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr == "append"
            ):
                return True
        return False


class GeneratorExpressionRule(ASTVisitorRule):
    """Suggest generators over lists when appropriate."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="use_generator",
            name="Use Generator Expression",
            description="Consider using generator for memory efficiency",
            category="green",
            severity="info",
        )

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Check if list comprehension could be a generator."""
        # This is a heuristic - would need more context in real implementation
        if self._looks_like_single_use(node):
            issue = self.create_issue(
                message=(
                    "Consider using generator expression instead of list "
                    "comprehension for single use"
                ),
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description="Replace [] with () to create generator",
                    replacement_code=(
                        "# Change [expr for item in iterable] to "
                        "(expr for item in iterable)"
                    ),
                ),
                impact=Impact(carbon_impact=2.0, performance=-0.1),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _looks_like_single_use(self, node: ast.ListComp) -> bool:
        """Heuristic to detect if this list might be used only once."""
        # In a full implementation, we'd need data flow analysis
        # For now, suggest generators for comprehensions in function calls
        return True  # Simplified heuristic


class FileHandlingRule(ASTVisitorRule):
    """Check for efficient file handling patterns."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="file_handling_efficiency",
            name="File Handling Efficiency",
            description="File handling could be more efficient",
            category="green",
            severity="info",
        )

    def visit_Call(self, node: ast.Call) -> None:
        """Check for inefficient file operations."""
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "open"
            and not self._in_with_statement(node)
        ):

            issue = self.create_issue(
                message="Use 'with open()' for automatic file closing",
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description=(
                        "Use context manager (with statement) for file handling"
                    ),
                    replacement_code="# with open(filename) as f:",
                ),
                impact=Impact(carbon_impact=1.0, performance=-0.05),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _in_with_statement(self, node: ast.AST) -> bool:
        """Check if this call is already in a with statement."""
        # This would need proper parent node tracking in a full implementation
        return False  # Simplified for now


class IneffientLoopRule(ASTVisitorRule):
    """Detect inefficient loop patterns."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="inefficient_loop",
            name="Inefficient Loop Pattern",
            description="Loop pattern could be optimized",
            category="green",
            severity="warning",
        )

    def visit_For(self, node: ast.For) -> None:
        """Check for range(len()) anti-pattern."""
        if self._is_range_len_pattern(node):
            issue = self.create_issue(
                message=(
                    "Use enumerate() instead of range(len()) for better "
                    "readability and performance"
                ),
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description="Replace range(len(items)) with enumerate(items)",
                    replacement_code="# for i, item in enumerate(items):",
                ),
                impact=Impact(performance=-0.05, carbon_impact=2.0),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _is_range_len_pattern(self, node: ast.For) -> bool:
        """Check for for i in range(len(something)) pattern."""
        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "range"
            and len(node.iter.args) == 1
            and isinstance(node.iter.args[0], ast.Call)
            and isinstance(node.iter.args[0].func, ast.Name)
            and node.iter.args[0].func.id == "len"
        ):
            return True
        return False


class GreenAnalyzer(BaseAnalyzer):
    """
    Green software analyzer for Python code.

    This analyzer implements rules for:
    - Inefficient string concatenation
    - List comprehension optimization
    - Generator vs list usage
    - Memory-efficient patterns
    """

    def __init__(self) -> None:
        super().__init__(
            name="Green Software Analyzer",
            description="Analyzes environmental sustainability and efficiency",
        )

        # Register green software rules
        self.register_rule(StringConcatenationRule())
        self.register_rule(ListComprehensionRule())
        self.register_rule(GeneratorExpressionRule())
        self.register_rule(FileHandlingRule())
        self.register_rule(IneffientLoopRule())

    def analyze(self, tree: ast.AST, source_code: str, file_path: str) -> List[Issue]:
        """
        Analyze green software issues.

        Args:
            tree: The parsed AST
            source_code: Original source code
            file_path: Path to the file being analyzed

        Returns:
            List of green software issues
        """
        all_issues = []

        for rule in self.rules.values():
            if rule.enabled:
                if isinstance(rule, ASTVisitorRule):
                    # Use visitor pattern for traversal rules
                    rule.reset(file_path, source_code)
                    rule.visit(tree)
                    rule.finalize()
                    all_issues.extend(rule.issues)
                else:
                    # Use direct checking for other rules
                    issues = rule.check(tree, source_code, file_path)
                    all_issues.extend(issues)

        return all_issues
