"""Tests for AgentState — validates the LangGraph state TypedDict structure."""

from ex04.services.agent.state import AgentState, Suspect, TokenMetrics


class TestAgentState:
    """Tests for AgentState TypedDict structure."""

    def test_agent_state_has_bug_report(self) -> None:
        """Test that AgentState includes bug_report field."""
        state: AgentState = {"bug_report": "Test bug"}
        assert state["bug_report"] == "Test bug"

    def test_agent_state_has_graph_context(self) -> None:
        """Test that AgentState includes graph_context field."""
        state: AgentState = {"graph_context": "Graph data here"}
        assert state["graph_context"] == "Graph data here"

    def test_agent_state_has_vault_context(self) -> None:
        """Test that AgentState includes vault_context field."""
        state: AgentState = {"vault_context": "Vault data here"}
        assert state["vault_context"] == "Vault data here"

    def test_agent_state_has_suspects(self) -> None:
        """Test that AgentState includes suspects field."""
        state: AgentState = {"suspects": []}
        assert isinstance(state["suspects"], list)

    def test_agent_state_has_inspected_code(self) -> None:
        """Test that AgentState includes inspected_code field."""
        state: AgentState = {"inspected_code": "def foo(): pass"}
        assert state["inspected_code"] == "def foo(): pass"

    def test_agent_state_has_root_cause(self) -> None:
        """Test that AgentState includes root_cause field."""
        state: AgentState = {"root_cause": "Null pointer"}
        assert state["root_cause"] == "Null pointer"

    def test_agent_state_has_proposed_fix(self) -> None:
        """Test that AgentState includes proposed_fix field."""
        state: AgentState = {"proposed_fix": "Add null check"}
        assert state["proposed_fix"] == "Add null check"

    def test_agent_state_has_fix_applied(self) -> None:
        """Test that AgentState includes fix_applied field."""
        state: AgentState = {"fix_applied": False}
        assert state["fix_applied"] is False

    def test_agent_state_has_test_results(self) -> None:
        """Test that AgentState includes test_results field."""
        state: AgentState = {"test_results": {}}
        assert isinstance(state["test_results"], dict)

    def test_agent_state_has_token_usage(self) -> None:
        """Test that AgentState includes token_usage field."""
        state: AgentState = {"token_usage": TokenMetrics()}
        assert isinstance(state["token_usage"], TokenMetrics)

    def test_agent_state_has_iterations(self) -> None:
        """Test that AgentState includes the iterations counter field."""
        state: AgentState = {"iterations": 3}
        assert state["iterations"] == 3

    def test_agent_state_all_fields(self) -> None:
        """Test that AgentState can hold all fields simultaneously."""
        state: AgentState = {
            "bug_report": "App crashes on startup",
            "graph_context": "Entity: main.py",
            "vault_context": "Index: main.py",
            "suspects": [],
            "inspected_code": "",
            "root_cause": "",
            "proposed_fix": "",
            "fix_applied": False,
            "test_results": {},
            "token_usage": TokenMetrics(),
        }
        assert len(state) == 10


class TestSuspect:
    """Tests for Suspect dataclass."""

    def test_suspect_required_fields(self) -> None:
        """Test that Suspect has required fields."""
        suspect = Suspect(
            file_path="src/main.py",
            line_start=10,
            line_end=20,
        )
        assert suspect.file_path == "src/main.py"
        assert suspect.line_start == 10
        assert suspect.line_end == 20

    def test_suspect_optional_fields_defaults(self) -> None:
        """Test that Suspect optional fields have defaults."""
        suspect = Suspect(file_path="a.py", line_start=1, line_end=5)
        assert suspect.score == 0.0
        assert suspect.reason == ""

    def test_suspect_all_fields(self) -> None:
        """Test Suspect with all fields set."""
        suspect = Suspect(
            file_path="src/main.py",
            line_start=10,
            line_end=20,
            score=0.95,
            reason="Accesses null object",
        )
        assert suspect.score == 0.95
        assert suspect.reason == "Accesses null object"
