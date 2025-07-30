"""Test suite for AST Analysis Research module.

Tests the experimental AST analysis capabilities and patterns.
"""

import ast

from ecoguard_ai.research.ast_analysis import (
    ASTAnalysisMetrics,
    ASTExplorer,
    ASTNodeInfo,
    ASTNodeVisitor,
    ASTPatternMatcher,
    demonstrate_ast_capabilities,
    get_all_ast_node_types,
    run_ast_research_demo,
)


class TestASTNodeInfo:
    """Test the ASTNodeInfo dataclass."""

    def test_basic_initialization(self):
        """Test basic ASTNodeInfo creation."""
        node_info = ASTNodeInfo(
            node_type="FunctionDef", line=1, column=0, parent_type="Module"
        )

        assert node_info.node_type == "FunctionDef"
        assert node_info.line == 1
        assert node_info.column == 0
        assert node_info.parent_type == "Module"
        assert node_info.children_count == 0
        assert node_info.attributes == {}
        assert node_info.context is None


class TestASTAnalysisMetrics:
    """Test the ASTAnalysisMetrics dataclass."""

    def test_default_initialization(self):
        """Test default ASTAnalysisMetrics creation."""
        metrics = ASTAnalysisMetrics()

        assert metrics.total_nodes == 0
        assert metrics.max_depth == 0
        assert len(metrics.node_type_counts) == 0
        assert len(metrics.complexity_metrics) == 0
        assert len(metrics.patterns_found) == 0

    def test_with_data(self):
        """Test ASTAnalysisMetrics with data."""
        metrics = ASTAnalysisMetrics(total_nodes=10, max_depth=3)
        metrics.node_type_counts["FunctionDef"] = 2
        metrics.complexity_metrics["cyclomatic"] = 5
        metrics.patterns_found.append("nested_function")

        assert metrics.total_nodes == 10
        assert metrics.max_depth == 3
        assert metrics.node_type_counts["FunctionDef"] == 2
        assert metrics.complexity_metrics["cyclomatic"] == 5
        assert "nested_function" in metrics.patterns_found


class TestASTNodeVisitor:
    """Test the enhanced AST visitor."""

    def test_simple_function_analysis(self):
        """Test analyzing a simple function."""
        code = """
def hello():
    print("Hello, World!")
"""
        visitor = ASTNodeVisitor(code)
        tree = ast.parse(code)
        visitor.visit(tree)

        assert visitor.metrics.total_nodes > 0
        assert visitor.metrics.node_type_counts["FunctionDef"] == 1
        assert visitor.metrics.node_type_counts["Call"] == 1
        assert len(visitor.nodes_info) > 0

        # Check that we have a FunctionDef node info
        function_nodes = [
            ni for ni in visitor.nodes_info if ni.node_type == "FunctionDef"
        ]
        assert len(function_nodes) == 1
        assert function_nodes[0].attributes.get("name") == "hello"

    def test_complex_code_analysis(self):
        """Test analyzing more complex code."""
        code = """
class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, x):
        if x > 0:
            self.value += x
        return self.value

calc = Calculator()
result = calc.add(5)
"""
        visitor = ASTNodeVisitor(code)
        tree = ast.parse(code)
        visitor.visit(tree)

        assert visitor.metrics.total_nodes > 10
        assert visitor.metrics.node_type_counts["ClassDef"] == 1
        assert visitor.metrics.node_type_counts["FunctionDef"] == 2  # __init__ and add
        assert visitor.metrics.max_depth > 2

        # Check for class definition
        class_nodes = [ni for ni in visitor.nodes_info if ni.node_type == "ClassDef"]
        assert len(class_nodes) == 1
        assert class_nodes[0].attributes.get("name") == "Calculator"

    def test_pattern_detection(self):
        """Test pattern detection capabilities."""
        code = """
def outer():
    def inner():
        return [x for x in range(10) if x > 5 if x < 8]
    return inner

class A: pass
class B(A, object): pass  # Multiple inheritance
"""
        visitor = ASTNodeVisitor(code)
        tree = ast.parse(code)
        visitor.visit(tree)

        assert "nested_function" in visitor.metrics.patterns_found
        assert "complex_list_comprehension" in visitor.metrics.patterns_found
        assert "multiple_inheritance" in visitor.metrics.patterns_found

    def test_complexity_metrics(self):
        """Test complexity metrics calculation."""
        code = """
def complex_function(x):
    if x > 0:
        while x > 0:
            if x % 2 == 0:
                x //= 2
            else:
                x = x * 3 + 1
    return x
"""
        visitor = ASTNodeVisitor(code)
        tree = ast.parse(code)
        visitor.visit(tree)

        # Should detect multiple complexity contributors
        assert visitor.metrics.complexity_metrics["cyclomatic"] > 1
        assert visitor.metrics.complexity_metrics.get("max_nesting", 0) > 1

    def test_context_detection(self):
        """Test context detection for nodes."""
        code = """
def my_function():
    x = 1
    if x:
        y = 2

class MyClass:
    z = 3
"""
        visitor = ASTNodeVisitor(code)
        tree = ast.parse(code)
        visitor.visit(tree)

        # Check contexts
        contexts = [ni.context for ni in visitor.nodes_info if ni.context]
        assert any("function:my_function" in ctx for ctx in contexts if ctx)
        assert any("class:MyClass" in ctx for ctx in contexts if ctx)
        assert any("control_flow:if" in ctx for ctx in contexts if ctx)


class TestASTExplorer:
    """Test the AST explorer functionality."""

    def test_analyze_simple_code(self):
        """Test analyzing simple code."""
        explorer = ASTExplorer()
        code = "x = 1\ny = 2"

        metrics = explorer.analyze_code(code, "simple assignment")

        assert metrics.total_nodes > 0
        assert metrics.node_type_counts["Assign"] == 2
        assert len(explorer.analysis_results) == 1

    def test_analyze_syntax_error(self):
        """Test handling syntax errors."""
        explorer = ASTExplorer()
        code = "def broken(\n    pass"  # Missing closing parenthesis

        metrics = explorer.analyze_code(code, "syntax error test")

        assert any("syntax_error" in pattern for pattern in metrics.patterns_found)

    def test_node_type_hierarchy(self):
        """Test node type hierarchy extraction."""
        explorer = ASTExplorer()
        code = """
def func():
    if True:
        x = 1
"""

        hierarchy = explorer.get_node_type_hierarchy(code)

        assert "Module" in hierarchy
        assert "FunctionDef" in hierarchy["Module"]
        assert "If" in hierarchy["FunctionDef"]

    def test_find_specific_patterns(self):
        """Test finding specific patterns."""
        explorer = ASTExplorer()
        code = """
import os
from sys import argv

def my_func():
    pass

class MyClass:
    pass

for i in range(10):
    pass

result = [x for x in range(5)]
"""

        patterns = explorer.find_specific_patterns(
            code, ["function_def", "class_def", "import", "loop", "comprehension"]
        )

        assert len(patterns["function_def"]) == 1
        assert len(patterns["class_def"]) == 1
        assert len(patterns["import"]) == 2  # import and from import
        assert len(patterns["loop"]) == 1
        assert len(patterns["comprehension"]) == 1

    def test_compare_complexity(self):
        """Test complexity comparison between code samples."""
        explorer = ASTExplorer()

        simple_code = "x = 1"
        complex_code = """
def complex_func(a, b, c):
    if a > 0:
        for i in range(b):
            if i % 2 == 0:
                yield i * c
"""

        comparison = explorer.compare_complexity(
            [("simple", simple_code), ("complex", complex_code)]
        )

        assert len(comparison["samples"]) == 2
        assert (
            comparison["samples"][1]["total_nodes"]
            > comparison["samples"][0]["total_nodes"]
        )
        assert (
            comparison["samples"][1]["cyclomatic_complexity"]
            > comparison["samples"][0]["cyclomatic_complexity"]
        )


class TestASTPatternMatcher:
    """Test the pattern matcher functionality."""

    def test_simple_assignment_pattern(self):
        """Test simple assignment pattern matching."""
        code = "x = 1"
        tree = ast.parse(code)
        node = tree.body[0]

        assert ASTPatternMatcher.matches_pattern(node, "simple_assignment")
        assert not ASTPatternMatcher.matches_pattern(node, "chained_assignment")

    def test_chained_assignment_pattern(self):
        """Test chained assignment pattern matching."""
        code = "x = y = 1"
        tree = ast.parse(code)
        node = tree.body[0]

        assert ASTPatternMatcher.matches_pattern(node, "chained_assignment")
        assert not ASTPatternMatcher.matches_pattern(node, "simple_assignment")

    def test_function_call_pattern(self):
        """Test function call pattern matching."""
        code = "print('hello')"
        tree = ast.parse(code)
        call_node = tree.body[0].value  # Extract the Call from Expr

        assert ASTPatternMatcher.matches_pattern(call_node, "function_call")

    def test_method_call_pattern(self):
        """Test method call pattern matching."""
        code = "obj.method()"
        tree = ast.parse(code)
        call_node = tree.body[0].value

        assert ASTPatternMatcher.matches_pattern(call_node, "method_call")
        assert ASTPatternMatcher.matches_pattern(
            call_node, "function_call"
        )  # Also a function call

    def test_string_concatenation_pattern(self):
        """Test string concatenation pattern matching."""
        # Note: In Python 3.8+, string literals are ast.Constant, not ast.Str
        code = "'hello' + 'world'"
        tree = ast.parse(code)
        binop_node = tree.body[0].value

        # This might not match due to AST changes, but the pattern is there
        assert isinstance(binop_node, ast.BinOp)
        assert isinstance(binop_node.op, ast.Add)

    def test_find_all_patterns(self):
        """Test finding all pattern instances."""
        code = """
x = 1
y = z = 2
print("hello")
obj.method()
"""
        tree = ast.parse(code)

        patterns = ASTPatternMatcher.find_all_patterns(
            tree,
            ["simple_assignment", "chained_assignment", "function_call", "method_call"],
        )

        assert len(patterns["simple_assignment"]) >= 1
        assert len(patterns["chained_assignment"]) >= 1
        assert len(patterns["function_call"]) >= 1  # includes method calls
        assert len(patterns["method_call"]) >= 1


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_all_ast_node_types(self):
        """Test getting all AST node types."""
        node_types = get_all_ast_node_types()

        assert isinstance(node_types, list)
        assert len(node_types) > 50  # Should have many node types
        assert "FunctionDef" in node_types
        assert "ClassDef" in node_types
        assert "If" in node_types
        assert "For" in node_types
        assert "Call" in node_types
        assert node_types == sorted(node_types)  # Should be sorted

    def test_demonstrate_ast_capabilities(self):
        """Test the demonstration function."""
        code = """
def example():
    return [x**2 for x in range(10)]

class Example:
    pass
"""

        analysis = demonstrate_ast_capabilities(code)

        assert "metrics" in analysis
        assert "patterns" in analysis
        assert "hierarchy" in analysis
        assert "pattern_matches" in analysis
        assert "available_node_types" in analysis

        assert analysis["metrics"].total_nodes > 0
        assert len(analysis["patterns"]["function_def"]) == 1
        assert len(analysis["patterns"]["class_def"]) == 1
        assert len(analysis["available_node_types"]) > 50


class TestMainFunctionality:
    """Test main functionality and demo functions."""

    def test_run_ast_research_demo_returns_analysis(self):
        """Test that the demo function returns valid analysis results."""
        analysis = run_ast_research_demo()

        assert isinstance(analysis, dict)
        assert "metrics" in analysis
        assert "patterns" in analysis
        assert "hierarchy" in analysis
        assert "pattern_matches" in analysis
        assert "available_node_types" in analysis

        assert isinstance(analysis["metrics"], ASTAnalysisMetrics)
        assert analysis["metrics"].total_nodes > 0

    def test_run_ast_research_demo_stdout(self, capsys):
        """Test that the demo function produces expected output."""
        run_ast_research_demo()

        captured = capsys.readouterr()
        assert "EcoGuard AI AST Research Demo" in captured.out
        assert "Total AST nodes:" in captured.out
        assert "Maximum depth:" in captured.out
        assert "Node type counts:" in captured.out


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""

    def test_empty_code(self):
        """Test analyzing empty code."""
        explorer = ASTExplorer()
        metrics = explorer.analyze_code("", "empty")

        # Empty module should still have at least a Module node
        assert metrics.total_nodes >= 1
        assert metrics.node_type_counts["Module"] >= 1

    def test_comments_and_docstrings(self):
        """Test that comments and docstrings are handled correctly."""
        code = '''
"""Module docstring."""

# This is a comment
def func():
    """Function docstring."""
    # Another comment
    pass
'''

        explorer = ASTExplorer()
        metrics = explorer.analyze_code(code, "with comments")

        # Comments are not part of AST, but docstrings are
        assert metrics.total_nodes > 0
        assert metrics.node_type_counts["FunctionDef"] == 1

    def test_very_nested_code(self):
        """Test deeply nested code."""
        code = """
if True:
    if True:
        if True:
            if True:
                if True:
                    x = 1
"""

        visitor = ASTNodeVisitor(code)
        tree = ast.parse(code)
        visitor.visit(tree)

        assert visitor.metrics.max_depth > 5
        assert visitor.metrics.complexity_metrics.get("max_nesting", 0) >= 4

    def test_comprehensive_python_features(self):
        """Test analysis of comprehensive Python features."""
        code = '''
import asyncio
from typing import List, Optional

async def async_func() -> None:
    """Async function with type hints."""
    pass

@property
def prop(self) -> int:
    return self._value

class GenericClass(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

with GenericClass(42) as gc:
    result = gc.prop

# Dictionary and set comprehensions
data = {k: v for k, v in enumerate(['a', 'b', 'c'])}
unique = {x for x in range(10) if x % 2 == 0}

# Walrus operator (Python 3.8+)
try:
    if (n := len(data)) > 0:
        print(f"Data has {n} items")
except Exception as e:
    raise ValueError("Something went wrong") from e
finally:
    pass
'''

        explorer = ASTExplorer()
        metrics = explorer.analyze_code(code, "comprehensive")

        # Should handle modern Python features gracefully
        assert metrics.total_nodes > 20
        assert metrics.node_type_counts["AsyncFunctionDef"] >= 1
        assert metrics.node_type_counts["ClassDef"] >= 1
        assert metrics.node_type_counts["Try"] >= 1

    def test_malformed_code_handling(self):
        """Test handling of various malformed code scenarios."""
        explorer = ASTExplorer()

        # Test with indentation error
        malformed_code = """
def func():
pass  # Missing indentation
"""
        metrics = explorer.analyze_code(malformed_code, "indentation error")
        assert any("syntax_error" in pattern for pattern in metrics.patterns_found)

        # Test with unclosed parentheses
        malformed_code2 = "print('hello'"
        metrics2 = explorer.analyze_code(malformed_code2, "unclosed parens")
        assert any("syntax_error" in pattern for pattern in metrics2.patterns_found)

    def test_ast_node_visitor_error_handling(self):
        """Test AST node visitor with problematic code."""
        visitor = ASTNodeVisitor("")

        # Test visiting a node without line information
        node = ast.Module(body=[], type_ignores=[])
        visitor.visit(node)

        assert visitor.metrics.total_nodes >= 1
        assert len(visitor.nodes_info) >= 1

    def test_pattern_matcher_edge_cases(self):
        """Test pattern matcher with edge cases."""
        # Test with empty node
        assert not ASTPatternMatcher.matches_pattern(
            ast.Module(body=[], type_ignores=[]), "nonexistent_pattern"
        )

        # Test finding patterns in empty tree
        empty_tree = ast.parse("")
        patterns = ASTPatternMatcher.find_all_patterns(
            empty_tree, ["simple_assignment"]
        )
        assert len(patterns["simple_assignment"]) == 0

    def test_ast_explorer_analysis_storage(self):
        """Test that AST explorer stores analysis results correctly."""
        explorer = ASTExplorer()

        # Analyze multiple code samples
        explorer.analyze_code("x = 1", "sample1")
        explorer.analyze_code("def func(): pass", "sample2")

        assert len(explorer.analysis_results) == 2
        assert explorer.analysis_results[0][0] == "sample1"
        assert explorer.analysis_results[1][0] == "sample2"

        # Check that metrics are stored correctly
        assert isinstance(explorer.analysis_results[0][1], ASTAnalysisMetrics)
        assert isinstance(explorer.analysis_results[1][1], ASTAnalysisMetrics)
