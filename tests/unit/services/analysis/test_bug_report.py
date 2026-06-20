"""Tests for BugReporter — generates structured bug reports from investigations."""

from ex04.services.analysis.bug_report import BugReporter
from ex04.shared.types_results import InvestigationResult, Suspect, TokenMetrics


class TestBugReporterGenerate:
    """Tests for BugReporter.generate method."""

    def test_generate_returns_string(self) -> None:
        """Test that generate returns a string."""
        reporter = BugReporter()
        investigation = InvestigationResult(
            root_cause="Null pointer in function X",
            proposed_fix="Add null check before accessing Y",
        )
        result = reporter.generate(investigation)
        assert isinstance(result, str)

    def test_generate_includes_root_cause(self) -> None:
        """Test that generated report includes the root cause."""
        reporter = BugReporter()
        investigation = InvestigationResult(root_cause="Null pointer exception")
        result = reporter.generate(investigation)

        assert "Null pointer exception" in result

    def test_generate_includes_proposed_fix(self) -> None:
        """Test that generated report includes the proposed fix."""
        reporter = BugReporter()
        investigation = InvestigationResult(proposed_fix="Add null check")
        result = reporter.generate(investigation)

        assert "Add null check" in result

    def test_generate_includes_suspects(self) -> None:
        """Test that generated report includes suspect locations."""
        reporter = BugReporter()
        investigation = InvestigationResult(
            suspects=[
                Suspect(
                    file_path="src/main.py",
                    line_start=10,
                    line_end=15,
                    score=0.9,
                    reason="Directly accesses null object",
                )
            ]
        )
        result = reporter.generate(investigation)

        assert "src/main.py" in result
        assert "10" in result

    def test_generate_includes_fix_applied_status(self) -> None:
        """Test that generated report includes fix application status."""
        reporter = BugReporter()
        investigation = InvestigationResult(fix_applied=True)
        result = reporter.generate(investigation)

        assert "Applied" in result or "applied" in result

    def test_generate_includes_test_results(self) -> None:
        """Test that generated report includes test results summary."""
        reporter = BugReporter()
        investigation = InvestigationResult(test_results={"passed": 5, "failed": 0})
        result = reporter.generate(investigation)

        assert "5" in result or "passed" in result.lower()

    def test_generate_includes_token_usage(self) -> None:
        """Test that generated report includes token usage."""
        reporter = BugReporter()
        investigation = InvestigationResult(
            token_usage=TokenMetrics(input_tokens=100, output_tokens=50)
        )
        result = reporter.generate(investigation)

        assert "100" in result or "input" in result.lower()

    def test_generate_empty_investigation(self) -> None:
        """Test that generate handles empty investigation gracefully."""
        reporter = BugReporter()
        investigation = InvestigationResult()
        result = reporter.generate(investigation)

        assert isinstance(result, str)
        assert len(result) > 0


class TestBugReporterStructure:
    """Tests for BugReporter report structure and formatting."""

    def test_generate_has_section_headers(self) -> None:
        """Test that generated report has markdown section headers."""
        reporter = BugReporter()
        investigation = InvestigationResult(root_cause="Test root cause")
        result = reporter.generate(investigation)

        assert "# " in result
        assert "## " in result

    def test_generate_has_problem_section(self) -> None:
        """Test that generated report has a problem summary section."""
        reporter = BugReporter()
        investigation = InvestigationResult(
            root_cause="Test root cause",
            proposed_fix="Test fix",
        )
        result = reporter.generate(investigation)

        assert "Problem" in result or "Root Cause" in result

    def test_generate_has_investigation_steps(self) -> None:
        """Test that generated report has an investigation steps section."""
        reporter = BugReporter()
        investigation = InvestigationResult(
            suspects=[Suspect(file_path="a.py", line_start=1, line_end=2, score=1.0)]
        )
        result = reporter.generate(investigation)

        assert "Investigation" in result or "Suspect" in result

    def test_generate_markdown_formatting(self) -> None:
        """Test that generated report uses markdown formatting."""
        reporter = BugReporter()
        investigation = InvestigationResult(root_cause="Test")
        result = reporter.generate(investigation)

        # Should use markdown: headers, lists, bold
        assert any(marker in result for marker in ["##", "-", "**", "*"])
