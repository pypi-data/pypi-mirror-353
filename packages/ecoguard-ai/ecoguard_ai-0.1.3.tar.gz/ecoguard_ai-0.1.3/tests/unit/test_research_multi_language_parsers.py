"""Test suite for multi-language parser research module."""

import pytest

from ecoguard_ai.research.multi_language_parsers import (
    ANTLRResearch,
    LanguageSupport,
    MultiLanguageAnalysisStrategy,
    MultiLanguageStrategy,
    ParserCapability,
    ParserType,
    TreeSitterResearch,
    demonstrate_multi_language_research,
)


class TestParserType:
    """Test ParserType enum."""

    def test_parser_type_values(self):
        """Test that ParserType enum has expected values."""
        assert ParserType.PYTHON_AST.value == "python_ast"
        assert ParserType.TREE_SITTER.value == "tree_sitter"
        assert ParserType.ANTLR.value == "antlr"

    def test_parser_type_count(self):
        """Test that we have the expected number of parser types."""
        assert len(ParserType) == 3


class TestLanguageSupport:
    """Test LanguageSupport enum."""

    def test_language_support_values(self):
        """Test that LanguageSupport enum has expected values."""
        assert LanguageSupport.PYTHON.value == "python"
        assert LanguageSupport.JAVASCRIPT.value == "javascript"
        assert LanguageSupport.TYPESCRIPT.value == "typescript"
        assert LanguageSupport.JAVA.value == "java"
        assert LanguageSupport.CPP.value == "cpp"
        assert LanguageSupport.RUST.value == "rust"
        assert LanguageSupport.GO.value == "go"
        assert LanguageSupport.CSHARP.value == "csharp"

    def test_language_support_count(self):
        """Test that we have the expected number of supported languages."""
        assert len(LanguageSupport) == 8


class TestParserCapability:
    """Test ParserCapability dataclass."""

    def test_parser_capability_creation(self):
        """Test creating a ParserCapability instance."""
        capability = ParserCapability(
            parser_type=ParserType.TREE_SITTER,
            language=LanguageSupport.PYTHON,
            incremental_parsing=True,
            error_recovery=True,
            syntax_highlighting=True,
            ast_traversal=True,
            query_language=True,
        )

        assert capability.parser_type == ParserType.TREE_SITTER
        assert capability.language == LanguageSupport.PYTHON
        assert capability.incremental_parsing is True
        assert capability.error_recovery is True
        assert capability.syntax_highlighting is True
        assert capability.ast_traversal is True
        assert capability.query_language is True

    def test_parser_capability_defaults(self):
        """Test ParserCapability default values."""
        capability = ParserCapability(
            parser_type=ParserType.PYTHON_AST,
            language=LanguageSupport.PYTHON,
        )

        assert capability.incremental_parsing is False
        assert capability.error_recovery is False
        assert capability.syntax_highlighting is False
        assert capability.ast_traversal is False
        assert capability.query_language is False
        assert capability.community_support == "unknown"
        assert capability.performance_rating == "unknown"
        assert capability.integration_difficulty == "unknown"
        assert capability.notes == []

    def test_parser_capability_with_notes(self):
        """Test ParserCapability with custom notes."""
        notes = ["Test note 1", "Test note 2"]
        capability = ParserCapability(
            parser_type=ParserType.ANTLR,
            language=LanguageSupport.JAVA,
            notes=notes,
        )

        assert capability.notes == notes


class TestMultiLanguageAnalysisStrategy:
    """Test MultiLanguageAnalysisStrategy dataclass."""

    def test_strategy_creation(self):
        """Test creating a MultiLanguageAnalysisStrategy instance."""
        strategy = MultiLanguageAnalysisStrategy(
            primary_parser=ParserType.TREE_SITTER,
            fallback_parsers=[ParserType.PYTHON_AST],
            supported_languages={LanguageSupport.PYTHON, LanguageSupport.JAVASCRIPT},
            analysis_patterns=["pattern1", "pattern2"],
            integration_requirements=["req1", "req2"],
        )

        assert strategy.primary_parser == ParserType.TREE_SITTER
        assert strategy.fallback_parsers == [ParserType.PYTHON_AST]
        assert len(strategy.supported_languages) == 2
        assert LanguageSupport.PYTHON in strategy.supported_languages
        assert LanguageSupport.JAVASCRIPT in strategy.supported_languages
        assert strategy.analysis_patterns == ["pattern1", "pattern2"]
        assert strategy.integration_requirements == ["req1", "req2"]

    def test_strategy_defaults(self):
        """Test MultiLanguageAnalysisStrategy default values."""
        strategy = MultiLanguageAnalysisStrategy(primary_parser=ParserType.TREE_SITTER)

        assert strategy.fallback_parsers == []
        assert strategy.supported_languages == set()
        assert strategy.analysis_patterns == []
        assert strategy.integration_requirements == []


class TestTreeSitterResearch:
    """Test TreeSitterResearch class."""

    def test_get_capabilities_returns_dict(self):
        """Test that get_capabilities returns a dictionary."""
        capabilities = TreeSitterResearch.get_capabilities()
        assert isinstance(capabilities, dict)
        assert len(capabilities) > 0

    def test_get_capabilities_contains_expected_languages(self):
        """Test that capabilities contain expected languages."""
        capabilities = TreeSitterResearch.get_capabilities()

        expected_languages = [
            LanguageSupport.PYTHON,
            LanguageSupport.JAVASCRIPT,
            LanguageSupport.TYPESCRIPT,
            LanguageSupport.RUST,
            LanguageSupport.GO,
        ]

        for language in expected_languages:
            assert language in capabilities

    def test_get_capabilities_parser_capability_structure(self):
        """Test that capabilities contain proper ParserCapability objects."""
        capabilities = TreeSitterResearch.get_capabilities()

        for language, capability in capabilities.items():
            assert isinstance(capability, ParserCapability)
            assert capability.parser_type == ParserType.TREE_SITTER
            assert capability.language == language
            assert isinstance(capability.notes, list)

    def test_python_capability_details(self):
        """Test specific details of Python capability."""
        capabilities = TreeSitterResearch.get_capabilities()
        python_cap = capabilities[LanguageSupport.PYTHON]

        assert python_cap.incremental_parsing is True
        assert python_cap.error_recovery is True
        assert python_cap.syntax_highlighting is True
        assert python_cap.ast_traversal is True
        assert python_cap.query_language is True
        assert python_cap.community_support == "excellent"
        assert python_cap.performance_rating == "high"
        assert python_cap.integration_difficulty == "medium"
        assert len(python_cap.notes) > 0

    def test_get_advantages_returns_list(self):
        """Test that get_advantages returns a list of strings."""
        advantages = TreeSitterResearch.get_advantages()
        assert isinstance(advantages, list)
        assert len(advantages) > 0
        assert all(isinstance(advantage, str) for advantage in advantages)

    def test_get_advantages_contains_key_features(self):
        """Test that advantages contain key Tree-sitter features."""
        advantages = TreeSitterResearch.get_advantages()
        advantage_text = " ".join(advantages).lower()

        assert "incremental" in advantage_text
        assert "error recovery" in advantage_text
        assert "query language" in advantage_text
        assert "performance" in advantage_text

    def test_get_disadvantages_returns_list(self):
        """Test that get_disadvantages returns a list of strings."""
        disadvantages = TreeSitterResearch.get_disadvantages()
        assert isinstance(disadvantages, list)
        assert len(disadvantages) > 0
        assert all(isinstance(disadvantage, str) for disadvantage in disadvantages)

    def test_get_disadvantages_contains_challenges(self):
        """Test that disadvantages contain known challenges."""
        disadvantages = TreeSitterResearch.get_disadvantages()
        disadvantage_text = " ".join(disadvantages).lower()

        assert "complex" in disadvantage_text
        assert "learning" in disadvantage_text or "grammar" in disadvantage_text


class TestANTLRResearch:
    """Test ANTLRResearch class."""

    def test_get_capabilities_returns_dict(self):
        """Test that get_capabilities returns a dictionary."""
        capabilities = ANTLRResearch.get_capabilities()
        assert isinstance(capabilities, dict)
        assert len(capabilities) > 0

    def test_get_capabilities_contains_expected_languages(self):
        """Test that capabilities contain expected languages."""
        capabilities = ANTLRResearch.get_capabilities()

        expected_languages = [
            LanguageSupport.PYTHON,
            LanguageSupport.JAVA,
            LanguageSupport.JAVASCRIPT,
        ]

        for language in expected_languages:
            assert language in capabilities

    def test_get_capabilities_parser_capability_structure(self):
        """Test that capabilities contain proper ParserCapability objects."""
        capabilities = ANTLRResearch.get_capabilities()

        for language, capability in capabilities.items():
            assert isinstance(capability, ParserCapability)
            assert capability.parser_type == ParserType.ANTLR
            assert capability.language == language
            assert isinstance(capability.notes, list)

    def test_antlr_characteristics(self):
        """Test ANTLR characteristic patterns."""
        capabilities = ANTLRResearch.get_capabilities()

        for capability in capabilities.values():
            # ANTLR typically doesn't support incremental parsing
            assert capability.incremental_parsing is False
            # ANTLR typically supports error recovery
            assert capability.error_recovery is True
            # ANTLR doesn't focus on syntax highlighting
            assert capability.syntax_highlighting is False
            # ANTLR supports AST traversal
            assert capability.ast_traversal is True
            # ANTLR doesn't have Tree-sitter style query language
            assert capability.query_language is False

    def test_get_advantages_returns_list(self):
        """Test that get_advantages returns a list of strings."""
        advantages = ANTLRResearch.get_advantages()
        assert isinstance(advantages, list)
        assert len(advantages) > 0
        assert all(isinstance(advantage, str) for advantage in advantages)

    def test_get_advantages_contains_key_features(self):
        """Test that advantages contain key ANTLR features."""
        advantages = ANTLRResearch.get_advantages()
        advantage_text = " ".join(advantages).lower()

        assert "grammar" in advantage_text
        assert "visitor" in advantage_text or "listener" in advantage_text
        assert "error recovery" in advantage_text

    def test_get_disadvantages_returns_list(self):
        """Test that get_disadvantages returns a list of strings."""
        disadvantages = ANTLRResearch.get_disadvantages()
        assert isinstance(disadvantages, list)
        assert len(disadvantages) > 0
        assert all(isinstance(disadvantage, str) for disadvantage in disadvantages)

    def test_get_disadvantages_contains_challenges(self):
        """Test that disadvantages contain known challenges."""
        disadvantages = ANTLRResearch.get_disadvantages()
        disadvantage_text = " ".join(disadvantages).lower()

        assert "performance" in disadvantage_text or "complex" in disadvantage_text
        assert "incremental" in disadvantage_text


class TestMultiLanguageStrategy:
    """Test MultiLanguageStrategy class."""

    def test_get_recommended_approach_returns_strategy(self):
        """Test that get_recommended_approach returns a strategy."""
        strategy = MultiLanguageStrategy.get_recommended_approach()
        assert isinstance(strategy, MultiLanguageAnalysisStrategy)

    def test_recommended_approach_details(self):
        """Test details of the recommended approach."""
        strategy = MultiLanguageStrategy.get_recommended_approach()

        assert strategy.primary_parser == ParserType.TREE_SITTER
        assert ParserType.PYTHON_AST in strategy.fallback_parsers
        assert ParserType.ANTLR in strategy.fallback_parsers
        assert len(strategy.supported_languages) > 0
        assert LanguageSupport.PYTHON in strategy.supported_languages
        assert len(strategy.analysis_patterns) > 0
        assert len(strategy.integration_requirements) > 0

    def test_recommended_analysis_patterns(self):
        """Test that recommended analysis patterns are comprehensive."""
        strategy = MultiLanguageStrategy.get_recommended_approach()

        expected_patterns = [
            "function_complexity_analysis",
            "unused_variable_detection",
            "code_duplication_detection",
            "security_pattern_matching",
            "performance_anti_patterns",
            "green_software_patterns",
        ]

        for pattern in expected_patterns:
            assert pattern in strategy.analysis_patterns

    def test_get_implementation_phases_returns_list(self):
        """Test that get_implementation_phases returns a list."""
        phases = MultiLanguageStrategy.get_implementation_phases()
        assert isinstance(phases, list)
        assert len(phases) > 0

    def test_implementation_phases_structure(self):
        """Test structure of implementation phases."""
        phases = MultiLanguageStrategy.get_implementation_phases()

        for phase in phases:
            assert isinstance(phase, dict)
            assert "phase" in phase
            assert "description" in phase
            assert "deliverables" in phase
            assert "timeline" in phase
            assert isinstance(phase["phase"], str)
            assert isinstance(phase["description"], str)
            assert isinstance(phase["deliverables"], str)
            assert isinstance(phase["timeline"], str)

    def test_implementation_phases_progression(self):
        """Test that implementation phases follow logical progression."""
        phases = MultiLanguageStrategy.get_implementation_phases()

        # Should have multiple phases
        assert len(phases) >= 3

        # First phase should be foundational
        first_phase = phases[0]
        assert (
            "foundation" in first_phase["description"].lower()
            or "python" in first_phase["description"].lower()
        )

    def test_get_integration_challenges_returns_list(self):
        """Test that get_integration_challenges returns a list."""
        challenges = MultiLanguageStrategy.get_integration_challenges()
        assert isinstance(challenges, list)
        assert len(challenges) > 0

    def test_integration_challenges_structure(self):
        """Test structure of integration challenges."""
        challenges = MultiLanguageStrategy.get_integration_challenges()

        for challenge in challenges:
            assert isinstance(challenge, dict)
            assert "challenge" in challenge
            assert "description" in challenge
            assert "solution" in challenge
            assert isinstance(challenge["challenge"], str)
            assert isinstance(challenge["description"], str)
            assert isinstance(challenge["solution"], str)

    def test_integration_challenges_cover_key_areas(self):
        """Test that integration challenges cover key concern areas."""
        challenges = MultiLanguageStrategy.get_integration_challenges()
        challenge_text = " ".join(
            [c["challenge"] + " " + c["description"] for c in challenges]
        ).lower()

        assert "performance" in challenge_text
        assert "error" in challenge_text
        assert "grammar" in challenge_text or "version" in challenge_text


class TestDemonstrateMultiLanguageResearch:
    """Test demonstrate_multi_language_research function."""

    def test_demonstrate_returns_dict(self):
        """Test that demonstrate function returns a dictionary."""
        result = demonstrate_multi_language_research()
        assert isinstance(result, dict)

    def test_demonstrate_contains_expected_keys(self):
        """Test that demonstrate result contains expected keys."""
        result = demonstrate_multi_language_research()

        expected_keys = [
            "tree_sitter",
            "antlr",
            "recommended_strategy",
            "implementation_phases",
            "integration_challenges",
            "summary",
        ]

        for key in expected_keys:
            assert key in result

    def test_tree_sitter_section_structure(self):
        """Test tree_sitter section structure."""
        result = demonstrate_multi_language_research()
        tree_sitter = result["tree_sitter"]

        assert "capabilities" in tree_sitter
        assert "advantages" in tree_sitter
        assert "disadvantages" in tree_sitter
        assert "supported_languages" in tree_sitter

        assert isinstance(tree_sitter["capabilities"], dict)
        assert isinstance(tree_sitter["advantages"], list)
        assert isinstance(tree_sitter["disadvantages"], list)
        assert isinstance(tree_sitter["supported_languages"], int)
        assert tree_sitter["supported_languages"] > 0

    def test_antlr_section_structure(self):
        """Test antlr section structure."""
        result = demonstrate_multi_language_research()
        antlr = result["antlr"]

        assert "capabilities" in antlr
        assert "advantages" in antlr
        assert "disadvantages" in antlr
        assert "supported_languages" in antlr

        assert isinstance(antlr["capabilities"], dict)
        assert isinstance(antlr["advantages"], list)
        assert isinstance(antlr["disadvantages"], list)
        assert isinstance(antlr["supported_languages"], int)
        assert antlr["supported_languages"] > 0

    def test_recommended_strategy_section(self):
        """Test recommended_strategy section."""
        result = demonstrate_multi_language_research()
        strategy = result["recommended_strategy"]

        assert isinstance(strategy, MultiLanguageAnalysisStrategy)
        assert strategy.primary_parser == ParserType.TREE_SITTER

    def test_implementation_phases_section(self):
        """Test implementation_phases section."""
        result = demonstrate_multi_language_research()
        phases = result["implementation_phases"]

        assert isinstance(phases, list)
        assert len(phases) > 0

    def test_integration_challenges_section(self):
        """Test integration_challenges section."""
        result = demonstrate_multi_language_research()
        challenges = result["integration_challenges"]

        assert isinstance(challenges, list)
        assert len(challenges) > 0

    def test_summary_section_structure(self):
        """Test summary section structure."""
        result = demonstrate_multi_language_research()
        summary = result["summary"]

        expected_keys = [
            "primary_recommendation",
            "secondary_recommendation",
            "priority_languages",
            "estimated_timeline",
        ]

        for key in expected_keys:
            assert key in summary

        assert isinstance(summary["priority_languages"], list)
        assert len(summary["priority_languages"]) > 0
        assert "tree-sitter" in summary["primary_recommendation"].lower()

    def test_summary_recommendations_consistency(self):
        """Test that summary recommendations are consistent with strategy."""
        result = demonstrate_multi_language_research()
        summary = result["summary"]
        strategy = result["recommended_strategy"]

        # Primary recommendation should align with strategy
        assert strategy.primary_parser == ParserType.TREE_SITTER
        assert "tree-sitter" in summary["primary_recommendation"].lower()

        # Priority languages should be reasonable
        priority_languages = summary["priority_languages"]
        assert "Python" in priority_languages
        assert len(priority_languages) >= 3


class TestModuleIntegration:
    """Test integration aspects of the module."""

    def test_all_enums_are_used(self):
        """Test that all enum values are used somewhere in the module."""
        # Get research results
        result = demonstrate_multi_language_research()

        # Check that major parser types are represented
        tree_sitter_caps = result["tree_sitter"]["capabilities"]
        antlr_caps = result["antlr"]["capabilities"]

        assert len(tree_sitter_caps) > 0
        assert len(antlr_caps) > 0

        # Check that multiple languages are supported
        all_languages = set(tree_sitter_caps.keys()) | set(antlr_caps.keys())
        assert len(all_languages) >= 3

    def test_capabilities_are_comprehensive(self):
        """Test that capabilities provide comprehensive information."""
        tree_sitter_caps = TreeSitterResearch.get_capabilities()
        antlr_caps = ANTLRResearch.get_capabilities()

        # Each capability should have detailed information
        for caps_dict in [tree_sitter_caps, antlr_caps]:
            for capability in caps_dict.values():
                assert capability.community_support != "unknown"
                assert capability.performance_rating != "unknown"
                assert capability.integration_difficulty != "unknown"
                assert len(capability.notes) > 0

    def test_research_provides_actionable_guidance(self):
        """Test that research provides actionable guidance."""
        result = demonstrate_multi_language_research()

        # Should have clear recommendations
        assert result["recommended_strategy"].primary_parser == ParserType.TREE_SITTER

        # Should have implementation phases
        phases = result["implementation_phases"]
        assert len(phases) >= 3

        # Should identify challenges and solutions
        challenges = result["integration_challenges"]
        assert len(challenges) >= 3

        for challenge in challenges:
            assert len(challenge["solution"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])
