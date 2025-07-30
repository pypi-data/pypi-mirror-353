"""AST Analysis Research and Prototyping for EcoGuard AI.

This module explores advanced Python AST capabilities and serves as a
proof-of-concept for sophisticated AST analysis patterns. It documents
AST traversal strategies and node identification techniques.

Goals:
- Deep dive into Python AST module capabilities
- Create proof-of-concept AST parser for basic Python constructs
- Document AST traversal patterns and node identification strategies
- Prototype advanced analysis techniques

This work supports Phase 1 Stage 3 of the EcoGuard AI development roadmap.
"""

import ast
import inspect
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ASTNodeInfo:
    """Information about an AST node for analysis."""

    node_type: str
    line: int
    column: int
    parent_type: Optional[str] = None
    children_count: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    context: Optional[str] = None


@dataclass
class ASTAnalysisMetrics:
    """Metrics collected during AST analysis."""

    total_nodes: int = 0
    node_type_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    max_depth: int = 0
    complexity_metrics: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    patterns_found: List[str] = field(default_factory=list)


class ASTNodeVisitor(ast.NodeVisitor):
    """Enhanced AST visitor for research and analysis purposes."""

    def __init__(self, source_code: str = ""):
        """Initialize the AST visitor with source code."""
        self.source_code = source_code
        self.nodes_info: List[ASTNodeInfo] = []
        self.metrics = ASTAnalysisMetrics()
        self.current_depth = 0
        self.parent_stack: List[ast.AST] = []

    def visit(self, node: ast.AST) -> None:
        """Visit a node and collect detailed information."""
        self.current_depth += 1
        self.metrics.max_depth = max(self.metrics.max_depth, self.current_depth)
        self.metrics.total_nodes += 1

        node_type = type(node).__name__
        self.metrics.node_type_counts[node_type] += 1

        # Collect node information
        node_info = ASTNodeInfo(
            node_type=node_type,
            line=getattr(node, "lineno", 0),
            column=getattr(node, "col_offset", 0),
            parent_type=(
                type(self.parent_stack[-1]).__name__ if self.parent_stack else None
            ),
            children_count=len(list(ast.iter_child_nodes(node))),
            attributes=self._extract_node_attributes(node),
            context=self._get_node_context(node),
        )
        self.nodes_info.append(node_info)

        # Track patterns
        self._detect_patterns(node)

        # Update complexity metrics
        self._update_complexity_metrics(node)

        # Visit children
        self.parent_stack.append(node)
        self.generic_visit(node)
        self.parent_stack.pop()
        self.current_depth -= 1

    def _extract_node_attributes(self, node: ast.AST) -> Dict[str, Any]:
        """Extract relevant attributes from an AST node."""
        attributes = {}

        # Common attributes based on node type
        if hasattr(node, "name"):
            attributes["name"] = node.name
        if hasattr(node, "id"):
            attributes["id"] = node.id
        if hasattr(node, "attr"):
            attributes["attr"] = node.attr
        if hasattr(node, "op"):
            attributes["op"] = type(node.op).__name__ if node.op else None
        if hasattr(node, "targets") and isinstance(node.targets, list):
            attributes["targets_count"] = len(node.targets)
        if hasattr(node, "args") and hasattr(node.args, "args"):
            attributes["param_count"] = len(node.args.args)
        if hasattr(node, "body") and isinstance(node.body, list):
            attributes["body_length"] = len(node.body)
        if hasattr(node, "orelse") and isinstance(node.orelse, list):
            attributes["has_else"] = len(node.orelse) > 0

        return attributes

    def _get_node_context(self, node: ast.AST) -> Optional[str]:
        """Get contextual information about where this node appears."""
        if not self.parent_stack:
            return "module_level"

        parent = self.parent_stack[-1]
        parent_type = type(parent).__name__

        if parent_type == "FunctionDef":
            return f"function:{getattr(parent, 'name', 'unknown')}"
        elif parent_type == "ClassDef":
            return f"class:{getattr(parent, 'name', 'unknown')}"
        elif parent_type in ("If", "While", "For"):
            return f"control_flow:{parent_type.lower()}"
        elif parent_type == "Try":
            return "exception_handling"
        else:
            return parent_type.lower()

    def _detect_patterns(self, node: ast.AST) -> None:
        """Detect interesting AST patterns."""
        node_type = type(node).__name__

        # Pattern: Nested function definitions
        if node_type == "FunctionDef" and any(
            isinstance(p, ast.FunctionDef) for p in self.parent_stack
        ):
            self.metrics.patterns_found.append("nested_function")

        # Pattern: List comprehensions with multiple conditions
        if node_type == "ListComp" and hasattr(node, "generators"):
            total_ifs = sum(len(gen.ifs) for gen in node.generators)
            if total_ifs > 1:
                self.metrics.patterns_found.append("complex_list_comprehension")

        # Pattern: Multiple inheritance
        if node_type == "ClassDef" and len(getattr(node, "bases", [])) > 1:
            self.metrics.patterns_found.append("multiple_inheritance")

        # Pattern: Chained comparisons
        if node_type == "Compare" and len(getattr(node, "ops", [])) > 1:
            self.metrics.patterns_found.append("chained_comparison")

        # Pattern: Exception handling with multiple except clauses
        if node_type == "Try" and len(getattr(node, "handlers", [])) > 2:
            self.metrics.patterns_found.append("complex_exception_handling")

    def _update_complexity_metrics(self, node: ast.AST) -> None:
        """Update complexity-related metrics."""
        node_type = type(node).__name__

        # Cyclomatic complexity contributors
        if node_type in ("If", "While", "For", "ExceptHandler"):
            self.metrics.complexity_metrics["cyclomatic"] += 1
        elif node_type == "BoolOp":
            # And/Or operations add to complexity
            self.metrics.complexity_metrics["cyclomatic"] += len(node.values) - 1

        # Nesting depth complexity
        if node_type in ("If", "While", "For", "Try", "With"):
            current_nesting = sum(
                1
                for p in self.parent_stack
                if type(p).__name__ in ("If", "While", "For", "Try", "With")
            )
            self.metrics.complexity_metrics["max_nesting"] = max(
                self.metrics.complexity_metrics.get("max_nesting", 0), current_nesting
            )


class ASTExplorer:
    """Advanced AST exploration and analysis tool."""

    def __init__(self):
        """Initialize the AST explorer."""
        self.analysis_results: List[
            Tuple[str, ASTAnalysisMetrics, List[ASTNodeInfo]]
        ] = []

    def analyze_code(
        self, source_code: str, description: str = ""
    ) -> ASTAnalysisMetrics:
        """Analyze Python source code and return detailed AST metrics."""
        try:
            tree = ast.parse(source_code)
            visitor = ASTNodeVisitor(source_code)
            visitor.visit(tree)

            # Store results for comparison
            self.analysis_results.append(
                (description, visitor.metrics, visitor.nodes_info)
            )

            return visitor.metrics

        except SyntaxError as e:
            # Return empty metrics for syntax errors
            metrics = ASTAnalysisMetrics()
            metrics.patterns_found.append(f"syntax_error:{e.msg}")
            return metrics

    def get_node_type_hierarchy(self, source_code: str) -> Dict[str, List[str]]:
        """Get the hierarchy of AST node types in the code."""
        try:
            tree = ast.parse(source_code)
            hierarchy = defaultdict(list)

            def collect_hierarchy(node: ast.AST, parent_type: str = "Module") -> None:
                node_type = type(node).__name__
                hierarchy[parent_type].append(node_type)

                for child in ast.iter_child_nodes(node):
                    collect_hierarchy(child, node_type)

            collect_hierarchy(tree)
            return dict(hierarchy)

        except SyntaxError:
            return {}

    def find_specific_patterns(
        self, source_code: str, patterns: List[str]
    ) -> Dict[str, List[ASTNodeInfo]]:
        """Find specific AST patterns in the code."""
        results = {pattern: [] for pattern in patterns}

        try:
            tree = ast.parse(source_code)
            visitor = ASTNodeVisitor(source_code)
            visitor.visit(tree)

            for node_info in visitor.nodes_info:
                # Check for requested patterns
                if "function_def" in patterns and node_info.node_type == "FunctionDef":
                    results["function_def"].append(node_info)

                if "class_def" in patterns and node_info.node_type == "ClassDef":
                    results["class_def"].append(node_info)

                if "import" in patterns and node_info.node_type in (
                    "Import",
                    "ImportFrom",
                ):
                    results["import"].append(node_info)

                if "loop" in patterns and node_info.node_type in ("For", "While"):
                    results["loop"].append(node_info)

                if "comprehension" in patterns and node_info.node_type.endswith("Comp"):
                    results["comprehension"].append(node_info)

            return results

        except SyntaxError:
            return results

    def compare_complexity(self, code_samples: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Compare complexity metrics across multiple code samples."""
        comparison = {
            "samples": [],
            "complexity_comparison": {},
            "pattern_comparison": {},
        }

        for description, code in code_samples:
            metrics = self.analyze_code(code, description)
            comparison["samples"].append(
                {
                    "description": description,
                    "total_nodes": metrics.total_nodes,
                    "max_depth": metrics.max_depth,
                    "cyclomatic_complexity": metrics.complexity_metrics.get(
                        "cyclomatic", 0
                    ),
                    "max_nesting": metrics.complexity_metrics.get("max_nesting", 0),
                    "unique_patterns": len(set(metrics.patterns_found)),
                    "node_types": len(metrics.node_type_counts),
                }
            )

        return comparison


class ASTPatternMatcher:
    """Pattern matching for specific AST structures."""

    @staticmethod
    def matches_pattern(node: ast.AST, pattern: str) -> bool:
        """Check if a node matches a specific pattern."""
        if pattern == "simple_assignment":
            return (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
            )

        elif pattern == "chained_assignment":
            return isinstance(node, ast.Assign) and len(node.targets) > 1

        elif pattern == "function_call":
            return isinstance(node, ast.Call)

        elif pattern == "method_call":
            return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)

        elif pattern == "string_concatenation":
            return (
                isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Add)
                and isinstance(node.left, (ast.Str, ast.Constant))
                and isinstance(node.right, (ast.Str, ast.Constant))
            )

        elif pattern == "list_append_in_loop":
            # This would need more sophisticated parent context checking
            return False  # Placeholder for now

        return False

    @staticmethod
    def find_all_patterns(
        tree: ast.AST, patterns: List[str]
    ) -> Dict[str, List[ast.AST]]:
        """Find all instances of specified patterns in the AST."""
        results = {pattern: [] for pattern in patterns}

        for node in ast.walk(tree):
            for pattern in patterns:
                if ASTPatternMatcher.matches_pattern(node, pattern):
                    results[pattern].append(node)

        return results


def get_all_ast_node_types() -> List[str]:
    """Get all available AST node types in the current Python version."""
    node_types = []

    for name in dir(ast):
        obj = getattr(ast, name)
        if inspect.isclass(obj) and issubclass(obj, ast.AST) and obj is not ast.AST:
            node_types.append(name)

    return sorted(node_types)


def demonstrate_ast_capabilities(code_sample: str) -> Dict[str, Any]:
    """Demonstrate various AST analysis capabilities."""
    explorer = ASTExplorer()

    # Basic analysis
    metrics = explorer.analyze_code(code_sample, "demonstration")

    # Pattern finding
    patterns = explorer.find_specific_patterns(
        code_sample, ["function_def", "class_def", "import", "loop", "comprehension"]
    )

    # Node hierarchy
    hierarchy = explorer.get_node_type_hierarchy(code_sample)

    # Pattern matching
    try:
        tree = ast.parse(code_sample)
        pattern_matches = ASTPatternMatcher.find_all_patterns(
            tree,
            [
                "simple_assignment",
                "chained_assignment",
                "function_call",
                "method_call",
                "string_concatenation",
            ],
        )
    except SyntaxError:
        pattern_matches = {}

    return {
        "metrics": metrics,
        "patterns": patterns,
        "hierarchy": hierarchy,
        "pattern_matches": {k: len(v) for k, v in pattern_matches.items()},
        "available_node_types": get_all_ast_node_types(),
    }


# Example usage and testing functions
def run_ast_research_demo():
    """Run a demonstration of AST analysis capabilities."""
    # Sample code for analysis
    sample_code = '''
def factorial(n):
    """Calculate factorial using recursion."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class Calculator:
    """Simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def get_history(self):
        return [item for item in self.history if "=" in item]

# Usage example
calc = Calculator()
result = calc.add(5, 3)
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers if x % 2 == 0]
'''

    print("=== EcoGuard AI AST Research Demo ===")
    analysis = demonstrate_ast_capabilities(sample_code)

    print(f"\nTotal AST nodes: {analysis['metrics'].total_nodes}")
    print(f"Maximum depth: {analysis['metrics'].max_depth}")
    print(
        f"Cyclomatic complexity: "
        f"{analysis['metrics'].complexity_metrics.get('cyclomatic', 0)}"
    )
    print("Patterns found: {analysis['metrics'].patterns_found}")

    print("\nNode type counts:")
    for node_type, count in analysis["metrics"].node_type_counts.items():
        print(f"  {node_type}: {count}")

    print("\nPattern matches:")
    for pattern, count in analysis["pattern_matches"].items():
        if count > 0:
            print(f"  {pattern}: {count}")

    return analysis


if __name__ == "__main__":
    run_ast_research_demo()
