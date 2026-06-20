"""Tests for WorkflowBuilder edges and verify routing."""

from unittest.mock import patch

from ex04.services.agent.nodes.verify import VerificationNode
from ex04.services.agent.workflow import WorkflowBuilder


class TestWorkflowBuilderEdges:
    """Tests for WorkflowBuilder.add_edges method."""

    def test_linear_flow_edges(self) -> None:
        """Test that the linear flow edges are configured."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            edge_calls = [call[0] for call in mock_sg.return_value.add_edge.call_args_list]
            edge_pairs = [(edge[0], edge[1]) for edge in edge_calls]
            assert ("knowledge", "analysis") in edge_pairs
            assert ("analysis", "suspect") in edge_pairs
            assert ("suspect", "inspect") in edge_pairs
            assert ("inspect", "rootcause") in edge_pairs
            assert ("rootcause", "fix") in edge_pairs
            assert ("fix", "verify") in edge_pairs

    def test_retry_loop_edge(self) -> None:
        """Test that verify has a conditional retry edge to suspect."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            mock_sg.return_value.add_conditional_edges.assert_called_once()

    def test_start_and_end_edges(self) -> None:
        """Test that START edge and END routing are configured."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            edge_calls = [call[0] for call in mock_sg.return_value.add_edge.call_args_list]
            edge_pairs = [(edge[0], edge[1]) for edge in edge_calls]
            assert ("__start__", "knowledge") in edge_pairs
            mock_sg.return_value.add_conditional_edges.assert_called_once()
            routes = mock_sg.return_value.add_conditional_edges.call_args[0][2]
            assert routes["pass"] == "__end__"


class TestVerifyRoute:
    """Tests for the bounded verify to suspect retry routing."""

    def test_retries_when_failed_under_limit(self) -> None:
        builder = WorkflowBuilder(max_iterations=5)
        state = {"test_results": {"failed": 2}, "iterations": 1}
        assert builder._verify_route(state) == "retry"

    def test_stops_at_max_iterations_even_when_failing(self) -> None:
        builder = WorkflowBuilder(max_iterations=3)
        state = {"test_results": {"failed": 2}, "iterations": 3}
        assert builder._verify_route(state) == "pass"

    def test_passes_when_no_failures(self) -> None:
        builder = WorkflowBuilder()
        state = {"test_results": {"failed": 0}, "iterations": 0}
        assert builder._verify_route(state) == "pass"

    def test_verify_node_increments_iterations(self) -> None:
        result = VerificationNode(command=["true"])({"iterations": 2})
        assert result["iterations"] == 3
        assert result["test_results"]["passed"] is True
