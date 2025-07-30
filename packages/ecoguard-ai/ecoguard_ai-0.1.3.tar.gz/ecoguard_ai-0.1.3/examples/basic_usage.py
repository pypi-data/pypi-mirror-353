"""
Example usage of EcoGuard AI analysis capabilities.

This example demonstrates how to use the EcoGuard AI library programmatically
to analyze Python code for quality, security, and sustainability issues.
"""

from pathlib import Path

from ecoguard_ai.core.analyzer import AnalysisConfig, EcoGuardAnalyzer


def main() -> None:
    """Demonstrate EcoGuard AI analysis."""
    print("🌱 EcoGuard AI - Example Usage")
    print("=" * 50)

    # Create a sample Python file to analyze
    sample_code = '''
"""Sample Python code with various issues."""

import os
import sys
import unused_module  # This import is never used

def inefficient_function():
    """This function has several inefficiencies."""

    # Inefficient string concatenation
    result = ""
    for i in range(100):
        result = result + str(i) + ", "

    # Unused variable
    unused_var = "This variable is never used"

    return result

class Calculator:
    def __init__(self):
        self.value = 0

    def add(self, number):
        """Add a number to the current value."""
        self.value += number
        return self.value

    def multiply(self, number):
        """Multiply the current value by a number."""
        self.value *= number
        return self.value

# Example of potentially AI-generated verbose code
def verbose_function(data):
    """This function could be more concise."""
    if data is not None:
        if len(data) > 0:
            if isinstance(data, list):
                result = []
                for item in data:
                    if item is not None:
                        result.append(str(item))
                return result
            else:
                return None
        else:
            return None
    else:
        return None

# Main execution
if __name__ == "__main__":
    calc = Calculator()
    calc.add(5)
    calc.multiply(3)
    print(f"Result: {calc.value}")
'''

    # Write sample code to a temporary file
    sample_file = Path("example_code.py")
    sample_file.write_text(sample_code)

    try:
        # Create analyzer with default configuration
        print("Creating EcoGuard AI analyzer...")
        analyzer = EcoGuardAnalyzer()

        print(f"Analyzing file: {sample_file}")
        result = analyzer.analyze_file(sample_file)

        # Display results
        print(f"\n📊 Analysis Results for {result.file_path}")
        print("-" * 60)

        if not result.issues:
            print(
                "✅ No issues found! "
                "(This is expected since rules aren't implemented yet)"
            )
        else:
            print(f"Found {result.issue_count} issues:")

            for issue in result.issues:
                severity_str = (
                    issue.severity.value
                    if hasattr(issue.severity, "value")
                    else str(issue.severity)
                )
                category_str = (
                    issue.category.value
                    if hasattr(issue.category, "value")
                    else str(issue.category)
                )
                print(
                    f"  Line {issue.line}: " f"{severity_str.upper()} - {issue.message}"
                )
                print(f"    Rule: {issue.rule_id} (Category: {category_str})")
                if issue.suggested_fix:
                    print(f"    Fix: {issue.suggested_fix.description}")
                print()

        # Display metadata
        print("📈 File Metadata:")
        print(f"  File size: {result.metadata.get('file_size', 'unknown')} bytes")
        print(f"  Line count: {result.metadata.get('line_count', 'unknown')}")
        print(f"  Green score: {result.calculate_green_score():.1f}/100")
        print(f"  Security score: {result.calculate_security_score():.1f}/100")

        # Demonstrate different output formats
        print("\n💾 JSON Output (first 200 characters):")
        json_output = result.to_json()
        print(json_output[:200] + "..." if len(json_output) > 200 else json_output)

        # Example of analyzing with custom configuration
        print("\n🔧 Custom Configuration Example:")
        custom_config = AnalysisConfig(
            enable_security=False,  # Disable security analysis
            min_severity="warning",  # Only show warnings and above
            output_format="json",
        )

        # Create a custom analyzer (unused variable for demo purposes)
        custom_analyzer = EcoGuardAnalyzer(custom_config)  # noqa: F841
        custom_result = analyzer.analyze_file(sample_file)

        print(f"Custom analysis found {custom_result.issue_count} issues")
        print("(Note: Results are the same since rules aren't implemented yet)")

    finally:
        # Clean up temporary file
        if sample_file.exists():
            sample_file.unlink()

    print("\n🚀 Next Steps:")
    print("1. Rules will be implemented in Stage 1 (Quality & Green Software)")
    print("2. Security rules will be added in Stage 2")
    print("3. Advanced features coming in later stages")
    print("\nFor more information, see the 50-stage development roadmap in README.md")


if __name__ == "__main__":
    main()
