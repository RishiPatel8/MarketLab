import pytest
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import VirtualPortfolioCreate, VirtualOrderCreate, ScenarioSimulationRequest

def test_virtual_portfolio_lifecycle_and_orders(db_session):
    """Test virtual portfolio creation, order execution with fees, and mark-to-market accounting."""
    service = PortfolioService(db_session)

    # 1. Create Portfolio with ₹100,000 initial capital
    port = service.create_portfolio(VirtualPortfolioCreate(
        name="Test Growth Portfolio",
        initial_capital=100000.0,
        currency="INR"
    ))
    assert port.initial_capital == 100000.0
    assert port.cash_balance == 100000.0
    assert len(port.positions) == 0

    # 2. Execute BUY order for 10 shares of RELIANCE at requested price 2500
    buy_order = service.execute_order(
        portfolio_id=port.id,
        req=VirtualOrderCreate(
            symbol="RELIANCE",
            exchange="NSE",
            order_type="MARKET",
            side="BUY",
            quantity=10,
            requested_price=2500.0
        ),
        fee_pct=0.001,
        slippage_pct=0.0005
    )
    assert buy_order.status == "FILLED"
    assert buy_order.side == "BUY"
    assert buy_order.quantity == 10
    assert buy_order.executed_price > 0
    assert buy_order.transaction_fee > 0

    # Verify portfolio state after buy
    port_after_buy = service.get_portfolio(port.id)
    assert port_after_buy.cash_balance < 100000.0
    assert len(port_after_buy.positions) == 1
    pos = port_after_buy.positions[0]
    assert pos.symbol == "RELIANCE"
    assert pos.quantity == 10
    assert pos.invested_amount > 0

    # 3. Execute partial SELL order for 4 shares
    sell_order = service.execute_order(
        portfolio_id=port.id,
        req=VirtualOrderCreate(
            symbol="RELIANCE",
            exchange="NSE",
            order_type="MARKET",
            side="SELL",
            quantity=4,
            requested_price=2600.0
        ),
        fee_pct=0.001,
        slippage_pct=0.0005
    )
    assert sell_order.status == "FILLED"
    assert sell_order.side == "SELL"

    # Verify portfolio state after sell
    port_after_sell = service.get_portfolio(port.id)
    assert len(port_after_sell.positions) == 1
    assert port_after_sell.positions[0].quantity == 6
    assert port_after_sell.total_realized_pnl != 0.0

def test_virtual_portfolio_overdraft_prevention(db_session):
    """Verify that orders exceeding available cash are rejected."""
    service = PortfolioService(db_session)
    port = service.create_portfolio(VirtualPortfolioCreate(
        name="Small Portfolio",
        initial_capital=5000.0
    ))

    # Try to buy 100 shares of RELIANCE (~₹250,000) with only ₹5,000 cash
    with pytest.raises(Exception) as exc:
        service.execute_order(
            portfolio_id=port.id,
            req=VirtualOrderCreate(
                symbol="RELIANCE",
                side="BUY",
                quantity=100,
                requested_price=2500.0
            )
        )
    assert "Insufficient virtual cash balance" in str(exc.value)

def test_scenario_simulation_what_if(db_session):
    """Verify what-if market stress test calculation."""
    service = PortfolioService(db_session)
    port = service.create_portfolio(VirtualPortfolioCreate(
        name="Scenario Test Port",
        initial_capital=100000.0
    ))

    # Buy 20 shares
    service.execute_order(
        portfolio_id=port.id,
        req=VirtualOrderCreate(symbol="RELIANCE", side="BUY", quantity=20, requested_price=2500.0)
    )

    # Run -15% correction scenario
    scen = service.run_scenario_simulation(
        portfolio_id=port.id,
        req=ScenarioSimulationRequest(scenario_type="market_correction", shock_pct=-15.0)
    )
    assert scen.shock_pct == -15.0
    assert scen.simulated_pnl < 0
    assert scen.simulated_portfolio_value < scen.baseline_portfolio_value
    assert scen.estimated_max_loss > 0

def test_portfolio_and_strategy_api_endpoints(client):
    """Verify REST API endpoints for portfolios and strategies."""
    # List strategies
    strat_resp = client.get("/api/v1/strategies")
    assert strat_resp.status_code == 200
    strat_data = strat_resp.json()
    assert len(strat_data) >= 10

    # Create portfolio via API
    port_resp = client.post("/api/v1/portfolios", json={
        "name": "API Test Portfolio",
        "initial_capital": 50000.0,
        "currency": "INR"
    })
    assert port_resp.status_code == 201
    port_data = port_resp.json()
    assert port_data["initial_capital"] == 50000.0
    port_id = port_data["id"]

    # Place order via API
    order_resp = client.post(f"/api/v1/portfolios/{port_id}/orders", json={
        "symbol": "GREENPOWER",
        "exchange": "NSE",
        "order_type": "MARKET",
        "side": "BUY",
        "quantity": 100,
        "requested_price": 20.0
    })
    assert order_resp.status_code == 200
    order_data = order_resp.json()
    assert order_data["status"] == "FILLED"
