"""
AI code analyzer for EcoGuard AI.

This module implements AI-specific code analysis rules including:
- Redundant imports in AI-generated code
- Verbose code patterns
- Duplicate function detection
- AI-generated boilerplate identification
"""

import ast
from typing import List

from ecoguard_ai.analyzers.base import ASTVisitorRule, BaseAnalyzer
from ecoguard_ai.core.issue import Fix, Impact, Issue


class VerboseCodeRule(ASTVisitorRule):
    """Detect overly verbose code patterns common in AI-generated code."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="verbose_ai_code",
            name="Verbose AI-Generated Code",
            description="Code pattern appears verbose and could be simplified",
            category="ai_code",
            severity="info",
        )

    def visit_If(self, node: ast.If) -> None:
        """Check for nested if statements that could be simplified."""
        if self._is_redundant_nested_if(node):
            issue = self.create_issue(
                message="Redundant nested if statements can be combined with 'and'",
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description="Combine conditions with 'and' operator",
                    replacement_code="# if condition1 and condition2:",
                ),
                impact=Impact(maintainability=0.5, performance=-0.05),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _is_redundant_nested_if(self, node: ast.If) -> bool:
        """Check if this is a simple nested if that could be combined."""
        if (
            len(node.body) == 1
            and isinstance(node.body[0], ast.If)
            and not node.body[0].orelse
        ):  # No else clause
            return True
        return False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check for overly explicit return patterns."""
        if self._has_verbose_return_pattern(node):
            issue = self.create_issue(
                message="Function has verbose return pattern that could be simplified",
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description=(
                        "Simplify return logic by returning expressions directly"
                    ),
                    replacement_code=(
                        "# return expression instead of if/else with True/False"
                    ),
                ),
                impact=Impact(maintainability=0.4, performance=-0.03),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _has_verbose_return_pattern(self, node: ast.FunctionDef) -> bool:
        """Check for if condition: return True else: return False patterns."""
        # Look for the pattern: if condition: return True else: return False
        for stmt in node.body:
            if (
                isinstance(stmt, ast.If)
                and len(stmt.body) == 1
                and len(stmt.orelse) == 1
                and isinstance(stmt.body[0], ast.Return)
                and isinstance(stmt.orelse[0], ast.Return)
            ):

                # Check if returning boolean literals
                body_return = stmt.body[0]
                else_return = stmt.orelse[0]

                if (
                    isinstance(body_return.value, ast.Constant)
                    and isinstance(else_return.value, ast.Constant)
                    and isinstance(body_return.value.value, bool)
                    and isinstance(else_return.value.value, bool)
                ):
                    return True
        return False


class RedundantVariableRule(ASTVisitorRule):
    """Detect redundant variable assignments common in AI code."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="redundant_variable",
            name="Redundant Variable Assignment",
            description="Variable assignment is redundant",
            category="ai_code",
            severity="info",
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check for variables assigned once and immediately returned."""
        self._check_immediate_return_pattern(node)
        self.generic_visit(node)

    def _check_immediate_return_pattern(self, node: ast.FunctionDef) -> None:
        """Check for: var = expr; return var pattern."""
        if len(node.body) >= 2:
            for i in range(len(node.body) - 1):
                stmt1 = node.body[i]
                stmt2 = node.body[i + 1]

                if (
                    isinstance(stmt1, ast.Assign)
                    and isinstance(stmt2, ast.Return)
                    and len(stmt1.targets) == 1
                    and isinstance(stmt1.targets[0], ast.Name)
                    and isinstance(stmt2.value, ast.Name)
                    and stmt1.targets[0].id == stmt2.value.id
                ):

                    issue = self.create_issue(
                        message=(
                            f"Variable '{stmt1.targets[0].id}' is assigned "
                            "and immediately returned"
                        ),
                        node=stmt1,
                        file_path=self.current_file_path,
                        suggested_fix=Fix(
                            description=(
                                "Return the expression directly without "
                                "intermediate variable"
                            ),
                            replacement_code="# return expression",
                        ),
                        impact=Impact(maintainability=0.2, performance=-0.02),
                    )
                    self.issues.append(issue)


class DuplicateFunctionRule(ASTVisitorRule):
    """Detect similar function patterns that might be duplicates."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="duplicate_function",
            name="Potential Duplicate Function",
            description="Function appears similar to another function",
            category="ai_code",
            severity="warning",
        )
        self.functions: List[ast.FunctionDef] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Collect functions for similarity analysis."""
        self.functions.append(node)
        self.generic_visit(node)

    def finalize(self) -> None:
        """Check for similar functions after visiting all nodes."""
        for i, func1 in enumerate(self.functions):
            for func2 in self.functions[i + 1 :]:
                if self._are_functions_similar(func1, func2):
                    issue = self.create_issue(
                        message=(
                            f"Function '{func1.name}' appears similar to "
                            f"'{func2.name}'"
                        ),
                        node=func1,
                        file_path=self.current_file_path,
                        suggested_fix=Fix(
                            description=(
                                "Consider extracting common logic into a "
                                "shared function"
                            ),
                            replacement_code=(
                                "# Extract common patterns into reusable functions"
                            ),
                        ),
                        impact=Impact(maintainability=-0.8, performance=-0.05),
                    )
                    self.issues.append(issue)

    def _are_functions_similar(
        self, func1: ast.FunctionDef, func2: ast.FunctionDef
    ) -> bool:
        """Check if two functions are structurally similar."""
        # Simple heuristic: same number of statements and parameters
        if (
            len(func1.body) == len(func2.body)
            and len(func1.args.args) == len(func2.args.args)
            and len(func1.body) > 2
        ):  # Only check functions with some complexity

            # Check if they have similar structure (same statement types)
            for stmt1, stmt2 in zip(func1.body, func2.body):
                if not isinstance(stmt1, type(stmt2)):
                    return False
            return True
        return False


class OverCommentedCodeRule(ASTVisitorRule):
    """Detect over-commented code common in AI-generated code."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="over_commented",
            name="Over-Commented Code",
            description="Code has excessive or obvious comments",
            category="ai_code",
            severity="info",
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check for obvious comments in functions."""
        # This would need source code parsing to detect comments
        # For now, check for overly simple functions that probably don't need
        # much documentation
        if self._is_trivial_function(node) and self._has_docstring(node):
            issue = self.create_issue(
                message=(
                    f"Function '{node.name}' is trivial but has "
                    "detailed documentation"
                ),
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description=(
                        "Consider simplifying documentation for trivial functions"
                    ),
                    replacement_code="# Simplify or remove unnecessary documentation",
                ),
                impact=Impact(maintainability=0.1, performance=-0.01),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _is_trivial_function(self, node: ast.FunctionDef) -> bool:
        """Check if function is trivial (simple getter/setter pattern)."""
        return len(node.body) == 1 and isinstance(node.body[0], ast.Return)

    def _has_docstring(self, node: ast.FunctionDef) -> bool:
        """Check if function has a docstring."""
        return (
            len(node.body) > 0
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )


class UnnecessaryTypeChecksRule(ASTVisitorRule):
    """Detect unnecessary type checks common in defensive AI code."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="unnecessary_type_check",
            name="Unnecessary Type Check",
            description="Type check may be unnecessary",
            category="ai_code",
            severity="info",
        )

    def visit_If(self, node: ast.If) -> None:
        """Check for defensive type checking patterns."""
        if self._is_unnecessary_none_check(node):
            issue = self.create_issue(
                message="Multiple None checks could be simplified",
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description="Use early return or simplified condition",
                    replacement_code="# if not value: return",
                ),
                impact=Impact(maintainability=0.3, performance=-0.02),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _is_unnecessary_none_check(self, node: ast.If) -> bool:
        """Check for excessive None checking patterns."""
        # Look for nested None checks: if x is not None: if x != None: ...
        if (
            isinstance(node.test, ast.Compare)
            and len(node.body) == 1
            and isinstance(node.body[0], ast.If)
        ):

            # Both checking for not None
            outer_is_none_check = self._is_none_check(node.test)
            inner_is_none_check = self._is_none_check(node.body[0].test)

            return outer_is_none_check and inner_is_none_check
        return False

    def _is_none_check(self, test: ast.expr) -> bool:
        """Check if expression is a None check."""
        if isinstance(test, ast.Compare):
            return any(
                isinstance(comp, ast.Is) or isinstance(comp, (ast.Eq, ast.NotEq))
                for comp in test.ops
            )
        return False


class AICodeAnalyzer(BaseAnalyzer):
    """
    AI-specific code analyzer for Python code.

    This analyzer implements rules for:
    - Redundant imports in AI-generated code
    - Verbose code patterns
    - Duplicate function detection
    - AI-generated boilerplate identification
    """

    def __init__(self) -> None:
        super().__init__(
            name="AI Code Analyzer",
            description="Analyzes AI-generated code inefficiencies and patterns",
        )

        # Register AI-specific rules
        self.register_rule(VerboseCodeRule())
        self.register_rule(RedundantVariableRule())
        self.register_rule(DuplicateFunctionRule())
        self.register_rule(OverCommentedCodeRule())
        self.register_rule(UnnecessaryTypeChecksRule())

    def analyze(self, tree: ast.AST, source_code: str, file_path: str) -> List[Issue]:
        """
        Analyze AI-specific code issues.

        Args:
            tree: The parsed AST
            source_code: Original source code
            file_path: Path to the file being analyzed

        Returns:
            List of AI code issues
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
