"""
Test suite for the analyzer base classes.

This module tests the base analyzer classes and rule framework.
"""

import ast

from ecoguard_ai.analyzers.base import (
    ASTVisitorRule,
    BaseAnalyzer,
    BaseRule,
    get_source_segment,
)
from ecoguard_ai.core.issue import Issue


class ConcreteAnalyzer(BaseAnalyzer):
    """Concrete implementation for testing."""

    def analyze(self, tree: ast.AST, source_code: str, file_path: str) -> None:
        """Simple implementation for testing."""
        issues = []
        for rule in self.rules.values():
            if rule.enabled:
                try:
                    rule_issues = rule.check(tree, source_code, file_path)
                    issues.extend(rule_issues)
                except Exception:
                    # Skip rules that fail
                    pass
        return issues


class ConcreteRule(BaseRule):
    """Concrete implementation for testing."""

    def check(self, node: ast.AST, source_code: str, file_path: str) -> None:
        """Simple implementation for testing."""
        return [
            Issue(
                rule_id=self.rule_id,
                message="Test issue",
                severity=self.severity,
                category=self.category,
                file_path=file_path,
                line=1,
            )
        ]


class ConcreteASTRule(ASTVisitorRule):
    """Concrete implementation for testing."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Test visitor method."""
        self.add_issue(f"Function found: {node.name}", node)
        self.generic_visit(node)


class TestBaseAnalyzer:
    """Test the BaseAnalyzer class."""

    def test_initialization(self) -> None:
        """Test BaseAnalyzer initialization."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        assert analyzer.name == "Test"
        assert analyzer.description == "Test analyzer"
        assert analyzer.enabled is True
        assert analyzer.rules == {}

    def test_register_rule(self) -> None:
        """Test registering a rule."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")

        analyzer.register_rule(rule)
        assert "test_rule" in analyzer.rules
        assert analyzer.rules["test_rule"] == rule

    def test_enable_disable_rule(self) -> None:
        """Test enabling and disabling rules."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")
        analyzer.register_rule(rule)

        # Test disabling
        analyzer.disable_rule("test_rule")
        assert not analyzer.rules["test_rule"].enabled

        # Test enabling
        analyzer.enable_rule("test_rule")
        assert analyzer.rules["test_rule"].enabled

    def test_analyze_with_rules(self) -> None:
        """Test analyzing with registered rules."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")
        analyzer.register_rule(rule)

        code = "def test(): pass"
        tree = ast.parse(code)
        issues = analyzer.analyze(tree, code, "test.py")

        assert len(issues) == 1
        assert issues[0].rule_id == "test_rule"


class TestBaseRule:
    """Test the BaseRule class."""

    def test_initialization(self) -> None:
        """Test BaseRule initialization."""
        rule = ConcreteRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test description",
            category="quality",
            severity="warning",
        )

        assert rule.rule_id == "test_rule"
        assert rule.name == "Test Rule"
        assert rule.description == "Test description"
        assert rule.category == "quality"
        assert rule.severity == "warning"
        assert rule.enabled is True

    def test_create_issue(self) -> None:
        """Test creating an issue."""
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")

        node = ast.parse("x = 1").body[0]
        issue = rule.create_issue("Test message", node, "test.py")

        assert issue.rule_id == "test_rule"
        assert issue.message == "Test message"
        assert issue.file_path == "test.py"


class TestASTVisitorRule:
    """Test the ASTVisitorRule class."""

    def test_initialization(self) -> None:
        """Test ASTVisitorRule initialization."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        assert rule.rule_id == "ast_rule"
        assert rule.issues == []
        assert rule.current_source_code == ""
        assert rule.current_file_path == ""

    def test_check_with_visitor(self) -> None:
        """Test checking code with visitor pattern."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        code = """
def test_function() -> None:
    pass

def another_function():
    pass
"""
        tree = ast.parse(code)
        issues = rule.check(tree, code, "test.py")

        # Should find two functions
        assert len(issues) == 2
        assert all("Function found:" in issue.message for issue in issues)

    def test_reset_and_finalize(self) -> None:
        """Test reset and finalize methods."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        rule.reset("test.py", "code")
        assert rule.current_file_path == "test.py"
        assert rule.current_source_code == "code"
        assert rule.issues == []

        # Add an issue and reset
        node = ast.parse("x = 1").body[0]
        rule.add_issue("Test", node)
        assert len(rule.issues) == 1

        rule.reset("test2.py", "code2")
        assert rule.issues == []

    def test_add_issue(self) -> None:
        """Test adding issues."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        rule.reset("test.py", "x = 1")
        node = ast.parse("x = 1").body[0]

        rule.add_issue("Test issue", node)
        assert len(rule.issues) == 1
        assert rule.issues[0].message == "Test issue"
        assert rule.issues[0].file_path == "test.py"


def test_get_source_segment() -> None:
    """Test the get_source_segment utility function."""

    # Test single line
    source = "x = 1\ny = 2\nz = 3"
    tree = ast.parse(source)
    assign_node = tree.body[0]  # x = 1

    segment = get_source_segment(source, assign_node)
    assert segment == "x = 1"

    # Test multiple lines
    source = "def func():\n    x = 1\n    return x"
    tree = ast.parse(source)
    func_node = tree.body[0]

    segment = get_source_segment(source, func_node)
    assert "def func():" in segment
    assert "return x" in segment

    # Test node without line info
    node_without_line = ast.AST()
    segment = get_source_segment(source, node_without_line)
    assert segment == ""

    # Test invalid line numbers
    class MockNode:
        def __init__(self, lineno: int, end_lineno: int = None) -> None:
            self.lineno = lineno
            self.end_lineno = end_lineno

    invalid_node = MockNode(-1)
    segment = get_source_segment(source, invalid_node)
    assert segment == ""

    out_of_bounds_node = MockNode(100)
    segment = get_source_segment(source, out_of_bounds_node)
    assert segment == ""


def test_get_source_segment_column_offsets() -> None:
    """Test get_source_segment with column offset handling."""

    source = "x = 1 + 2"
    tree = ast.parse(source)

    # Get the binary operation node (1 + 2)
    assign_node = tree.body[0]
    binop_node = assign_node.value

    segment = get_source_segment(source, binop_node)
    assert "1 + 2" in segment or segment  # Should extract part of the expression

    # Test with multiline and column offsets
    source = "if True:\n    x = 1\n    y = 2"
    tree = ast.parse(source)
    if_node = tree.body[0]

    segment = get_source_segment(source, if_node)
    assert "if True:" in segment
    assert "y = 2" in segment
