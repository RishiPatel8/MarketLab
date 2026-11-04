import pytest
from datetime import datetime, timezone
from app.db.models.strategy import StrategyDefinition
from app.db.models.virtual_portfolio import VirtualPortfolio, VirtualPosition, VirtualOrder
from app.db.models.scenario import ScenarioSimulation
from app.db.models.fundamental_snapshot import FundamentalSnapshot
from app.db.models.instrument import Instrument
from app.schemas.strategy import StrategyRunRequest, StrategySignal, StrategyConsensusResult
from app.schemas.portfolio import VirtualPortfolioCreate, VirtualOrderCreate
from app.schemas.fundamental import DCFValuationResult, FundamentalAnalysisResult
from app.schemas.decision import DecisionReportResponse, PriceTargetScenario
from app.schemas.research import ResearchRequest
from app.services.market_data_service import MarketDataService

def test_milestone_1_models_persistence(db_session):
    """Verify all new Milestone 1 SQLAlchemy entities persist and query cleanly."""
    # 1. Strategy Definition
    strat = StrategyDefinition(
        strategy_key="test_momentum",
        name="Test Momentum Strategy",
        category="momentum",
        default_parameters_json='{"period": 14}',
        version="1.0.0"
    )
    db_session.add(strat)

    # 2. Virtual Portfolio
    port = VirtualPortfolio(
        name="User Test Portfolio",
        initial_capital=50000.0,
        cash_balance=50000.0,
        currency="INR"
    )
    db_session.add(port)
    db_session.flush()

    # 3. Instrument lookup/dummy
    inst = db_session.query(Instrument).first()
    if not inst:
        inst = Instrument(symbol="M1TEST", company_name="M1 Test Corp", exchange="NSE")
        db_session.add(inst)
        db_session.flush()

    # 4. Virtual Position & Order
    pos = VirtualPosition(
        portfolio_id=port.id,
        instrument_id=inst.id,
        symbol=inst.symbol,
        quantity=10,
        average_entry_price=100.0,
        current_price=105.0,
        invested_amount=1000.0,
        current_value=1050.0,
        unrealized_pnl=50.0
    )
    db_session.add(pos)

    order = VirtualOrder(
        portfolio_id=port.id,
        instrument_id=inst.id,
        symbol=inst.symbol,
        side="BUY",
        quantity=10,
        executed_price=100.0,
        status="FILLED"
    )
    db_session.add(order)

    # 5. Scenario Simulation
    scenario = ScenarioSimulation(
        portfolio_id=port.id,
        scenario_name="Test Correction",
        scenario_type="market_shock",
        market_shock_pct=-15.0,
        simulated_pnl=-150.0,
        simulated_portfolio_value=50000.0 - 150.0
    )
    db_session.add(scenario)

    # 6. Fundamental Snapshot
    fund = FundamentalSnapshot(
        instrument_id=inst.id,
        fiscal_period="FY2025",
        report_date=datetime.now(timezone.utc),
        revenue=1200.0,
        net_profit=150.0,
        eps=15.0,
        roe=16.5,
        roce=18.2,
        free_cash_flow=120.0,
        dcf_fair_value=110.0
    )
    db_session.add(fund)
    db_session.commit()

    # Query verification
    retrieved_strat = db_session.query(StrategyDefinition).filter_by(strategy_key="test_momentum").first()
    assert retrieved_strat is not None
    assert retrieved_strat.name == "Test Momentum Strategy"

    retrieved_port = db_session.query(VirtualPortfolio).filter_by(id=port.id).first()
    assert retrieved_port is not None
    assert retrieved_port.initial_capital == 50000.0

    retrieved_pos = db_session.query(VirtualPosition).filter_by(portfolio_id=port.id).first()
    assert retrieved_pos is not None
    assert retrieved_pos.unrealized_pnl == 50.0

    retrieved_fund = db_session.query(FundamentalSnapshot).filter_by(instrument_id=inst.id).first()
    assert retrieved_fund is not None
    assert retrieved_fund.dcf_fair_value == 110.0

def test_milestone_1_pydantic_schemas():
    """Verify new Pydantic v2 schemas instantiate and validate properly."""
    req = ResearchRequest(
        question="Invest 50000 in Reliance for 6 months",
        symbol="RELIANCE",
        investment_amount_inr=50000.0,
        horizon_days=180,
        horizon_category="medium_term",
        risk_tolerance="moderate"
    )
    assert req.investment_amount_inr == 50000.0
    assert req.horizon_category == "medium_term"

    dcf = DCFValuationResult(
        fair_value_per_share=2950.0,
        current_market_price=2750.0,
        margin_of_safety_pct=7.27,
        projected_growth_rate=12.0,
        terminal_growth_rate=5.0,
        wacc=10.5,
        valuation_status="UNDERVALUED"
    )
    assert dcf.valuation_status == "UNDERVALUED"

    scenario = PriceTargetScenario(
        scenario="BULL",
        probability=0.30,
        target_price=3300.0,
        expected_return_pct=20.0,
        rationale="Strong refinery and retail margin expansion"
    )
    assert scenario.expected_return_pct == 20.0

def test_market_data_service_corporate_actions_and_fundamentals(db_session):
    """Verify MarketDataService methods execute safely without errors."""
    md_service = MarketDataService(db_session)
    actions = md_service.get_corporate_actions("RELIANCE", "NSE")
    assert isinstance(actions, dict)
    assert "splits" in actions
    assert "dividends" in actions

    fundamentals = md_service.get_company_fundamentals("RELIANCE", "NSE")
    assert isinstance(fundamentals, dict)
