from langgraph.graph import StateGraph, END
from app.agents.state import ResearchWorkflowState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.market_data_node import market_data_node
from app.agents.nodes.financial_research_node import financial_research_node
from app.agents.nodes.rag_node import rag_node
from app.agents.nodes.quantitative_node import quantitative_node
from app.agents.nodes.verifier_node import verifier_node
from app.agents.nodes.report_node import report_node
from app.core.config import settings

def route_after_planner(state: ResearchWorkflowState) -> str:
    status = state.get("run_status")
    if status in ("needs_clarification", "failed"):
        return END
    return "market_data_retrieval"

def route_after_verifier(state: ResearchWorkflowState) -> str:
    current_step = state.get("current_step")
    if current_step == "rag_evidence_retrieval":
        return "rag_evidence_retrieval"
    return "report_generation"

def create_research_graph():
    """
    Constructs and compiles the bounded, stateful LangGraph workflow.
    """
    builder = StateGraph(ResearchWorkflowState)

    # Add workflow nodes
    builder.add_node("planner", planner_node)
    builder.add_node("market_data_retrieval", market_data_node)
    builder.add_node("financial_research", financial_research_node)
    builder.add_node("rag_evidence_retrieval", rag_node)
    builder.add_node("quantitative_analysis", quantitative_node)
    builder.add_node("verification", verifier_node)
    builder.add_node("report_generation", report_node)

    # Set entry point
    builder.set_entry_point("planner")

    # Add conditional edge from planner
    builder.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "market_data_retrieval": "market_data_retrieval",
            END: END
        }
    )

    # Add sequential edges
    builder.add_edge("market_data_retrieval", "financial_research")
    builder.add_edge("financial_research", "rag_evidence_retrieval")
    builder.add_edge("rag_evidence_retrieval", "quantitative_analysis")
    builder.add_edge("quantitative_analysis", "verification")

    # Add conditional edge from verifier
    builder.add_conditional_edges(
        "verification",
        route_after_verifier,
        {
            "rag_evidence_retrieval": "rag_evidence_retrieval",
            "report_generation": "report_generation"
        }
    )

    # Add terminal edge
    builder.add_edge("report_generation", END)

    return builder.compile()

# Global compiled graph instance
research_graph = create_research_graph()
