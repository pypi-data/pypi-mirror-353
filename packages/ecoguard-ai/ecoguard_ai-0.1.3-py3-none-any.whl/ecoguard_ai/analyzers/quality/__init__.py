"""
Quality analyzer for EcoGuard AI.

This module implements code quality analysis rules including:
- Unused variables and imports
- Function complexity metrics
- Naming conventions
- Code structure improvements
"""

import ast
from typing import Dict, List, Set

from ecoguard_ai.analyzers.base import ASTVisitorRule, BaseAnalyzer
from ecoguard_ai.core.issue import Fix, Impact, Issue


class UnusedVariableRule(ASTVisitorRule):
    """Detect unused variables in function scopes."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="unused_variable",
            name="Unused Variable",
            description="Variable is defined but never used",
            category="quality",
            severity="warning",
        )
        self.scopes: List[Dict[str, ast.AST]] = []
        self.used_names: List[Set[str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Enter new scope
        self.scopes.append({})
        self.used_names.append(set())

        # Add parameters to current scope
        for arg in node.args.args:
            self.scopes[-1][arg.arg] = arg

        # Visit function body
        for child in ast.iter_child_nodes(node):
            self.visit(child)

        # Check for unused variables in this scope
        for var_name, var_node in self.scopes[-1].items():
            if var_name not in self.used_names[-1] and not var_name.startswith("_"):
                issue = self.create_issue(
                    message=f"Variable '{var_name}' is defined but never used",
                    node=var_node,
                    file_path=self.current_file_path,
                    suggested_fix=Fix(
                        description=(
                            f"Remove unused variable '{var_name}' or prefix with "
                            "underscore if intentional"
                        ),
                        replacement_code=f"# Remove line or rename to _{var_name}",
                    ),
                    impact=Impact(maintainability=-0.5, performance=-0.1),
                )
                self.issues.append(issue)

        # Exit scope
        self.scopes.pop()
        self.used_names.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        # Record variable assignments
        if self.scopes:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.scopes[-1][target.id] = target
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        # Record variable usage
        if isinstance(node.ctx, ast.Load) and self.used_names:
            self.used_names[-1].add(node.id)
        self.generic_visit(node)


class UnusedImportRule(ASTVisitorRule):
    """Detect unused imports at module level."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="unused_import",
            name="Unused Import",
            description="Import statement is not used in the module",
            category="quality",
            severity="info",
        )
        self.imported_names: Dict[str, ast.AST] = {}
        self.used_names: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names[name] = node
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names[name] = node
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # Handle module.attribute usage
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)

    def finalize(self) -> None:
        """Check for unused imports after visiting entire module."""
        for name, import_node in self.imported_names.items():
            if name not in self.used_names:
                issue = self.create_issue(
                    message=f"Import '{name}' is not used",
                    node=import_node,
                    file_path=self.current_file_path,
                    suggested_fix=Fix(
                        description=f"Remove unused import '{name}'",
                        replacement_code="# Remove import line",
                    ),
                    impact=Impact(performance=-0.1, maintainability=-0.2),
                )
                self.issues.append(issue)


class FunctionComplexityRule(ASTVisitorRule):
    """Detect functions with high cyclomatic complexity."""

    def __init__(self, max_complexity: int = 10):
        super().__init__(
            rule_id="function_complexity",
            name="High Function Complexity",
            description="Function has high cyclomatic complexity",
            category="quality",
            severity="warning",
        )
        self.max_complexity = max_complexity

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        complexity = self._calculate_complexity(node)

        if complexity > self.max_complexity:
            issue = self.create_issue(
                message=(
                    f"Function '{node.name}' has complexity {complexity} "
                    f"(max: {self.max_complexity})"
                ),
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description=(
                        "Consider breaking this function into smaller functions"
                    ),
                    replacement_code="# Refactor into smaller, more focused functions",
                ),
                impact=Impact(maintainability=-0.8, performance=-0.3),
            )
            self.issues.append(issue)

        self.generic_visit(node)

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points that increase complexity
            if isinstance(
                child,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.ListComp,
                    ast.DictComp,
                    ast.SetComp,
                ),
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # And/Or operations
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ExceptHandler,)):
                complexity += 1

        return complexity


class LongParameterListRule(ASTVisitorRule):
    """Detect functions with too many parameters."""

    def __init__(self, max_params: int = 5):
        super().__init__(
            rule_id="too_many_params",
            name="Too Many Parameters",
            description="Function has too many parameters",
            category="quality",
            severity="info",
        )
        self.max_params = max_params

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        param_count = len(node.args.args)

        if param_count > self.max_params:
            issue = self.create_issue(
                message=(
                    f"Function '{node.name}' has {param_count} parameters "
                    f"(max: {self.max_params})"
                ),
                node=node,
                file_path=self.current_file_path,
                suggested_fix=Fix(
                    description=(
                        "Consider using a data class or dictionary to group "
                        "related parameters"
                    ),
                    replacement_code="# Group related parameters into a data structure",
                ),
                impact=Impact(maintainability=-0.5),
            )
            self.issues.append(issue)

        self.generic_visit(node)


class QualityAnalyzer(BaseAnalyzer):
    """
    Quality analyzer for Python code.

    This analyzer implements rules for:
    - Unused variables and imports
    - Function complexity metrics
    - Parameter count limits
    - Code structure improvements
    """

    def __init__(self) -> None:
        super().__init__(
            name="Quality Analyzer",
            description="Analyzes code quality and maintainability",
        )

        # Register quality rules
        self.register_rule(UnusedVariableRule())
        self.register_rule(UnusedImportRule())
        self.register_rule(FunctionComplexityRule())
        self.register_rule(LongParameterListRule())

    def analyze(self, tree: ast.AST, source_code: str, file_path: str) -> List[Issue]:
        """
        Analyze quality issues.

        Args:
            tree: The parsed AST
            source_code: Original source code
            file_path: Path to the file being analyzed

        Returns:
            List of quality-related issues
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
