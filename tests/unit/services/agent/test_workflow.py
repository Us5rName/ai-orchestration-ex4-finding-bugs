"""Tests for WorkflowBuilder — assembles LangGraph debugging workflow.

Tests that the WorkflowBuilder correctly registers all 7 nodes and
configures the control flow edges including the retry loop.
"""

from unittest.mock import patch

from ex04.services.agent.workflow import WorkflowBuilder


class TestWorkflowBuilderBuild:
    """Tests for WorkflowBuilder.build method."""

    def test_build_returns_compiled_graph(self) -> None:
        """Test that build() returns the compiled graph."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            result = builder.build()
            assert result is mock_sg.return_value.compile()

    def test_build_adds_all_nodes(self) -> None:
        """Test that build() adds all 7 nodes."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            add_nodes_calls = mock_sg.return_value.add_node.call_count
            # 7 nodes: knowledge, analysis, suspect, inspect, rootcause, fix, verify
            assert add_nodes_calls == 7

    def test_build_adds_all_edges(self) -> None:
        """Test that build() adds all control flow edges."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            add_edge_calls = mock_sg.return_value.add_edge.call_count
            # 6 linear edges + 1 retry edge + START/END edges
            assert add_edge_calls >= 6

    def test_build_compiles_graph(self) -> None:
        """Test that build() compiles the graph."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            mock_sg.return_value.compile.assert_called_once()


class TestWorkflowBuilderNodes:
    """Tests for WorkflowBuilder.add_nodes method."""

    def test_adds_knowledge_node(self) -> None:
        """Test that the knowledge node is registered."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            # Check that add_node was called with 'knowledge'
            node_names = [call[0][0] for call in mock_sg.return_value.add_node.call_args_list]
            assert "knowledge" in node_names

    def test_adds_analysis_node(self) -> None:
        """Test that the analysis node is registered."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            node_names = [call[0][0] for call in mock_sg.return_value.add_node.call_args_list]
            assert "analysis" in node_names

    def test_adds_suspect_node(self) -> None:
        """Test that the suspect node is registered."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            node_names = [call[0][0] for call in mock_sg.return_value.add_node.call_args_list]
            assert "suspect" in node_names

    def test_adds_inspect_node(self) -> None:
        """Test that the inspect node is registered."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            node_names = [call[0][0] for call in mock_sg.return_value.add_node.call_args_list]
            assert "inspect" in node_names

    def test_adds_rootcause_node(self) -> None:
        """Test that the rootcause node is registered."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            node_names = [call[0][0] for call in mock_sg.return_value.add_node.call_args_list]
            assert "rootcause" in node_names

    def test_adds_fix_node(self) -> None:
        """Test that the fix node is registered."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            node_names = [call[0][0] for call in mock_sg.return_value.add_node.call_args_list]
            assert "fix" in node_names

    def test_adds_verify_node(self) -> None:
        """Test that the verify node is registered."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            node_names = [call[0][0] for call in mock_sg.return_value.add_node.call_args_list]
            assert "verify" in node_names


class TestWorkflowBuilderEdges:
    """Tests for WorkflowBuilder.add_edges method."""

    def test_linear_flow_edges(self) -> None:
        """Test that the linear flow edges are configured."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            edge_calls = [call[0] for call in mock_sg.return_value.add_edge.call_args_list]
            # Check key edges: knowledge→analysis, analysis→suspect, etc.
            edge_pairs = [(e[0], e[1]) for e in edge_calls]
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

            # add_conditional_edges is used for the retry loop
            mock_sg.return_value.add_conditional_edges.assert_called_once()

    def test_start_and_end_edges(self) -> None:
        """Test that START edge and END routing are configured."""
        with patch("ex04.services.agent.workflow.StateGraph") as mock_sg:
            builder = WorkflowBuilder()
            builder.build()

            edge_calls = [call[0] for call in mock_sg.return_value.add_edge.call_args_list]
            edge_pairs = [(e[0], e[1]) for e in edge_calls]
            assert ("__start__", "knowledge") in edge_pairs
            # verify→END is handled via add_conditional_edges, not add_edge
            mock_sg.return_value.add_conditional_edges.assert_called_once()
            cond_call = mock_sg.return_value.add_conditional_edges.call_args
            routes = cond_call[0][2]  # third positional arg is the routes dict
            assert "pass" in routes
            assert routes["pass"] == "__end__"
