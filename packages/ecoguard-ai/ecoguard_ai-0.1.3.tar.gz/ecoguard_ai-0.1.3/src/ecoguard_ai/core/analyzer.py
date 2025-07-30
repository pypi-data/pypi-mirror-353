"""
Core analysis engine for EcoGuard AI.

This module provides the foundational AST-based analysis capabilities
that power all EcoGuard AI analyzers.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ecoguard_ai.analyzers.base import BaseAnalyzer
from ecoguard_ai.core.issue import Issue
from ecoguard_ai.core.result import AnalysisResult


@dataclass
class AnalysisConfig:
    """Configuration for analysis runs."""

    # File patterns to include/exclude
    include_patterns: List[str] = field(default_factory=lambda: ["*.py"])
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "__pycache__/*",
            "*.pyc",
            ".venv/*",
            "venv/*",
            ".git/*",
        ]
    )

    # Analysis modules to enable
    enable_quality: bool = True
    enable_security: bool = True
    enable_green: bool = True
    enable_ai_code: bool = True

    # AST Research capabilities (Phase 1 Stage 3 Integration)
    enable_ast_research: bool = False
    ast_research_depth: str = "basic"  # basic, detailed, comprehensive
    enable_pattern_analysis: bool = False
    enable_complexity_metrics: bool = False

    # Output configuration
    output_format: str = "json"  # json, text, xml
    output_file: Optional[str] = None

    # Severity thresholds
    min_severity: str = "info"  # debug, info, warning, error, critical

    # Performance settings
    max_workers: int = 4
    timeout_seconds: int = 300


class EcoGuardAnalyzer:
    """
    Main analyzer class that orchestrates all analysis modules.

    This class serves as the central coordinator for AST-based static analysis,
    managing the execution of various analyzer modules and aggregating results.
    """

    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self._analyzers: List[BaseAnalyzer] = []

        # Initialize AST research capabilities if enabled
        self.ast_explorer = None
        if self.config.enable_ast_research:
            try:
                from ecoguard_ai.research.ast_analysis import ASTExplorer

                self.ast_explorer = ASTExplorer()
            except ImportError:
                # AST research module not available, continue without it
                pass

        self._initialize_analyzers()

    def _initialize_analyzers(self) -> None:
        """Initialize and register all available analyzers."""
        # This will be expanded as we implement specific analyzers
        if self.config.enable_quality:
            from ecoguard_ai.analyzers.quality import QualityAnalyzer

            self._analyzers.append(QualityAnalyzer())

        if self.config.enable_security:
            from ecoguard_ai.analyzers.security import SecurityAnalyzer

            self._analyzers.append(SecurityAnalyzer())

        if self.config.enable_green:
            from ecoguard_ai.analyzers.green import GreenAnalyzer

            self._analyzers.append(GreenAnalyzer())

        if self.config.enable_ai_code:
            from ecoguard_ai.analyzers.ai_code import AICodeAnalyzer

            self._analyzers.append(AICodeAnalyzer())

    def analyze_file(self, file_path: Union[str, Path]) -> AnalysisResult:
        """
        Analyze a single Python file.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            AnalysisResult containing all issues found
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.suffix == ".py":
            raise ValueError(f"Only Python files are supported: {file_path}")

        try:
            # Read and parse the file
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code, filename=str(file_path))

            # Enhanced AST analysis if research is enabled
            ast_research_data = {}
            if self.ast_explorer and self.config.enable_ast_research:
                try:
                    # Perform comprehensive AST analysis
                    ast_metrics = self.ast_explorer.analyze_code(
                        source_code, f"Analysis of {file_path.name}"
                    )

                    # Collect pattern analysis if enabled
                    if self.config.enable_pattern_analysis:
                        patterns = self.ast_explorer.find_specific_patterns(
                            source_code,
                            [
                                "function_def",
                                "class_def",
                                "import",
                                "loop",
                                "comprehension",
                            ],
                        )
                        ast_research_data["patterns"] = patterns

                    # Add complexity metrics to research data
                    if self.config.enable_complexity_metrics:
                        ast_research_data["complexity_metrics"] = (
                            ast_metrics.complexity_metrics
                        )
                        ast_research_data["max_depth"] = ast_metrics.max_depth
                        ast_research_data["node_type_counts"] = dict(
                            ast_metrics.node_type_counts
                        )

                except Exception as e:
                    # Continue analysis even if AST research fails
                    ast_research_data["error"] = f"AST research failed: {str(e)}"

            # Run all analyzers
            all_issues: List[Issue] = []
            metadata: Dict[str, Any] = {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "line_count": len(source_code.splitlines()),
            }

            # Add AST research data to metadata if available
            if ast_research_data:
                metadata["ast_research"] = ast_research_data

            for analyzer in self._analyzers:
                issues = analyzer.analyze(tree, source_code, str(file_path))
                all_issues.extend(issues)

            return AnalysisResult(
                file_path=str(file_path), issues=all_issues, metadata=metadata
            )

        except SyntaxError as e:
            # Handle Python syntax errors
            syntax_issue = Issue(
                rule_id="syntax_error",
                category="syntax",
                severity="error",
                message=f"Syntax error: {e.msg}",
                line=e.lineno or 1,
                column=e.offset or 1,
                file_path=str(file_path),
            )
            return AnalysisResult(
                file_path=str(file_path),
                issues=[syntax_issue],
                metadata={"error": "syntax_error"},
            )

        except Exception as e:
            # Handle other unexpected errors
            error_issue = Issue(
                rule_id="analysis_error",
                category="system",
                severity="error",
                message=f"Analysis failed: {str(e)}",
                line=1,
                column=1,
                file_path=str(file_path),
            )
            return AnalysisResult(
                file_path=str(file_path),
                issues=[error_issue],
                metadata={"error": "analysis_error"},
            )

    def analyze_directory(self, directory: Union[str, Path]) -> List[AnalysisResult]:
        """
        Analyze all Python files in a directory.

        Args:
            directory: Path to the directory to analyze

        Returns:
            List of AnalysisResult objects for each file
        """
        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Find all Python files
        python_files: List[Path] = []
        for pattern in self.config.include_patterns:
            python_files.extend(directory.rglob(pattern))

        # Filter out excluded patterns
        filtered_files = []
        for file_path in python_files:
            relative_path = file_path.relative_to(directory)
            exclude = False

            for exclude_pattern in self.config.exclude_patterns:
                if relative_path.match(exclude_pattern):
                    exclude = True
                    break

            if not exclude:
                filtered_files.append(file_path)

        # Analyze each file
        results = []
        for file_path in filtered_files:
            try:
                result = self.analyze_file(file_path)
                results.append(result)
            except Exception as e:
                # Log error but continue with other files
                error_result = AnalysisResult(
                    file_path=str(file_path),
                    issues=[
                        Issue(
                            rule_id="file_error",
                            category="system",
                            severity="error",
                            message=f"Failed to analyze file: {str(e)}",
                            line=1,
                            column=1,
                            file_path=str(file_path),
                        )
                    ],
                    metadata={"error": "file_error"},
                )
                results.append(error_result)

        return results
