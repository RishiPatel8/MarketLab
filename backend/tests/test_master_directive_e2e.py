import pytest
from app.agents.nodes.planner import parse_investment_intent
from app.analytics.fundamental_engine import FundamentalEngine
from app.analytics.technical_engine import TechnicalEngine
from app.analytics.strategy_engine import StrategyRegistry
from app.analytics.decision_engine import DecisionIntelligenceEngine
from app.services.market_data_service import MarketDataService
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import VirtualPortfolioCreate, VirtualOrderCreate, ScenarioSimulationRequest

def test_canonical_master_directive_workflow(db_session):
    """
    Tests the complete master directive workflow end-to-end:
    "I want to invest ₹50,000 in Reliance Industries for six months. Analyze the stock,
    run multiple strategies, simulate different scenarios, and tell me whether the current price is suitable for entering."
    """
    prompt = (
        "I want to invest ₹50,000 in Reliance Industries for six months. "
        "Analyze the stock, run multiple strategies, simulate different scenarios, "
        "and tell me whether the current price is suitable for entering."
    )

    # 1. Natural Language Intent Parsing
    intent = parse_investment_intent(prompt)
    assert intent["amount"] == 50000.0
    assert intent["days"] == 180
    assert intent["category"] == "medium_term"

    # 2. Market Data Retrieval & Freshness Validation
    md_service = MarketDataService(db_session)
    bars, val_report = md_service.get_and_validate_bars(symbol="RELIANCE", exchange="NSE")
    assert len(bars) >= 50
    assert val_report.is_valid is True
    bench_bars, _ = md_service.get_and_validate_bars(symbol="^NSEI", exchange="NSE")

    # 3. Fundamental Analysis Engine
    fundamentals = md_service.get_company_fundamentals(symbol="RELIANCE", exchange="NSE")
    fundamentals["current_price"] = bars[-1].close
    fund_analysis = FundamentalEngine.analyze_fundamentals(
        raw_data=fundamentals,
        symbol="RELIANCE",
        company_name="Reliance Industries Limited"
    )
    assert fund_analysis.dcf_valuation.fair_value_per_share > 0
    assert len(fund_analysis.dcf_valuation.sensitivity_matrix) > 0
    assert fund_analysis.dupont.roe is not None

    # 4. Technical Analysis Engine
    tech_suite = TechnicalEngine.calculate_full_technical_suite(bars)
    assert tech_suite["latest_close"] == round(bars[-1].close, 2)
    assert tech_suite["indicators"]["sma_20"] > 0
    assert tech_suite["indicators"]["rsi_14"] > 0
    assert tech_suite["indicators"]["atr_14"] > 0
    assert tech_suite["pivot_levels"]["pivot"] > 0

    # 5. Multi-Strategy Consensus Engine (10 models)
    consensus = StrategyRegistry.run_multi_strategy_consensus(
        bars=bars,
        initial_capital=intent["amount"],
        benchmark_bars=bench_bars
    )
    assert consensus.total_strategies == 10
    assert consensus.consensus_rating in ("BUY", "HOLD", "SELL", "INSUFFICIENT_EVIDENCE")
    assert len(consensus.signals) == 10

    # 6. Decision Intelligence Engine Evaluation
    decision = DecisionIntelligenceEngine.evaluate_investment_decision(
        current_price=bars[-1].close,
        data_coverage_score=0.95,
        technical_data=tech_suite,
        fundamental_data=fund_analysis,
        consensus_result=consensus,
        horizon_days=intent["days"],
        horizon_category=intent["category"],
        investment_amount_inr=intent["amount"],
        risk_tolerance="moderate"
    )

    assert decision.decision_rating in ("BUY", "HOLD", "SELL", "INSUFFICIENT_EVIDENCE")
    assert decision.entry_range_min <= decision.entry_range_max
    assert decision.stop_loss_price > 0
    assert len(decision.scenarios) == 3  # BULL, BASE, BEAR
    assert decision.investment_amount_inr == 50000.0
    assert "SEBI" in decision.sebi_non_advisory_notice

    # 7. Virtual Investment Experiment & What-If Simulation
    portfolio_svc = PortfolioService(db_session)
    portfolio = portfolio_svc.create_portfolio(VirtualPortfolioCreate(
        name="Reliance 6M Research Experiment",
        initial_capital=50000.0
    ))
    assert portfolio.cash_balance == 50000.0

    # Execute simulated BUY order
    current_price = bars[-1].close
    qty = max(1, int(25000 / current_price))
    order_req = VirtualOrderCreate(
        symbol="RELIANCE",
        side="BUY",
        quantity=qty,
        order_type="MARKET",
        exchange="NSE"
    )
    order = portfolio_svc.execute_order(portfolio.id, order_req)
    assert order.status == "FILLED"
    refreshed_port = portfolio_svc.get_portfolio(portfolio.id)
    assert refreshed_port.cash_balance < 50000.0

    # Execute What-If Scenario Simulations (-10% market correction & +15% bull run)
    sim_bear = portfolio_svc.run_scenario_simulation(portfolio.id, ScenarioSimulationRequest(
        scenario_type="market_correction",
        shock_pct=-10.0
    ))
    assert sim_bear.simulated_portfolio_value < refreshed_port.total_portfolio_value

    sim_bull = portfolio_svc.run_scenario_simulation(portfolio.id, ScenarioSimulationRequest(
        scenario_type="bull_rally",
        shock_pct=15.0
    ))
    assert sim_bull.simulated_portfolio_value > refreshed_port.total_portfolio_value
