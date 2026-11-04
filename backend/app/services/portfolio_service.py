from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models.virtual_portfolio import VirtualPortfolio, VirtualPosition, VirtualOrder
from app.db.models.scenario import ScenarioSimulation
from app.db.models.instrument import Instrument
from app.schemas.portfolio import (
    VirtualPortfolioCreate,
    VirtualPortfolioResponse,
    VirtualPositionResponse,
    VirtualOrderCreate,
    VirtualOrderResponse,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse
)
from app.services.market_data_service import MarketDataService

class PortfolioService:
    """
    Deterministic Virtual Investment Environment and Paper Trading Service.
    Maintains virtual portfolios, simulated order execution, mark-to-market valuations,
    and stress-testing scenario simulations without connecting to real brokerages.
    """

    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)

    def create_portfolio(self, req: VirtualPortfolioCreate, user_id: Optional[str] = None) -> VirtualPortfolioResponse:
        port = VirtualPortfolio(
            user_id=user_id,
            name=req.name,
            initial_capital=req.initial_capital,
            cash_balance=req.initial_capital,
            currency=req.currency,
            portfolio_type=req.portfolio_type,
            description=req.description
        )
        self.db.add(port)
        self.db.commit()
        self.db.refresh(port)
        return self.get_portfolio(port.id)

    def list_portfolios(self, user_id: Optional[str] = None) -> List[VirtualPortfolioResponse]:
        query = self.db.query(VirtualPortfolio)
        if user_id:
            query = query.filter_by(user_id=user_id)
        ports = query.all()
        return [self.get_portfolio(p.id) for p in ports]

    def get_portfolio(self, portfolio_id: str) -> VirtualPortfolioResponse:
        port = self.db.query(VirtualPortfolio).filter_by(id=portfolio_id).first()
        if not port:
            raise HTTPException(status_code=404, detail="Virtual portfolio not found")

        positions = self.db.query(VirtualPosition).filter_by(portfolio_id=portfolio_id).all()
        pos_responses: List[VirtualPositionResponse] = []
        invested_total = 0.0
        current_value_total = 0.0
        unrealized_pnl_total = 0.0
        realized_pnl_total = 0.0

        for pos in positions:
            if pos.quantity <= 0:
                continue

            # Update mark-to-market current price
            try:
                latest_p = self.market_data_service.provider.get_latest_price(pos.symbol, pos.exchange) or pos.average_entry_price
            except Exception:
                latest_p = pos.average_entry_price

            cur_val = round(pos.quantity * latest_p, 2)
            invested = round(pos.quantity * pos.average_entry_price, 2)
            u_pnl = round(cur_val - invested, 2)
            u_pnl_pct = round((u_pnl / max(invested, 0.01)) * 100.0, 2)

            pos.current_price = latest_p
            pos.current_value = cur_val
            pos.invested_amount = invested
            pos.unrealized_pnl = u_pnl
            pos.updated_at = datetime.now(timezone.utc)

            invested_total += invested
            current_value_total += cur_val
            unrealized_pnl_total += u_pnl
            realized_pnl_total += (pos.realized_pnl or 0.0)

            pos_responses.append(VirtualPositionResponse(
                id=pos.id,
                portfolio_id=pos.portfolio_id,
                instrument_id=pos.instrument_id,
                symbol=pos.symbol,
                exchange=pos.exchange,
                quantity=pos.quantity,
                average_entry_price=round(pos.average_entry_price, 2),
                current_price=round(latest_p, 2),
                invested_amount=invested,
                current_value=cur_val,
                realized_pnl=round(pos.realized_pnl or 0.0, 2),
                unrealized_pnl=u_pnl,
                unrealized_pnl_pct=u_pnl_pct
            ))

        self.db.commit()

        total_port_val = round(port.cash_balance + current_value_total, 2)
        total_ret_pct = round(((total_port_val - port.initial_capital) / port.initial_capital) * 100.0, 2)

        return VirtualPortfolioResponse(
            id=port.id,
            name=port.name,
            initial_capital=round(port.initial_capital, 2),
            cash_balance=round(port.cash_balance, 2),
            invested_capital=round(invested_total, 2),
            total_portfolio_value=total_port_val,
            total_unrealized_pnl=round(unrealized_pnl_total, 2),
            total_realized_pnl=round(realized_pnl_total, 2),
            total_return_pct=total_ret_pct,
            currency=port.currency,
            portfolio_type=port.portfolio_type,
            status=port.status,
            positions=pos_responses,
            created_at=port.created_at
        )

    def execute_order(
        self,
        portfolio_id: str,
        req: VirtualOrderCreate,
        fee_pct: float = 0.001,       # 0.1% STT & brokerage
        slippage_pct: float = 0.0005   # 0.05% slippage
    ) -> VirtualOrderResponse:
        """
        Executes a virtual paper trading order deterministically.
        Applies realistic transaction costs and slippage; enforces non-negative cash balances.
        """
        port = self.db.query(VirtualPortfolio).filter_by(id=portfolio_id).first()
        if not port:
            raise HTTPException(status_code=404, detail="Virtual portfolio not found")

        # Resolve instrument
        inst = self.db.query(Instrument).filter(
            (Instrument.symbol == req.symbol) |
            (Instrument.nse_symbol == req.symbol) |
            (Instrument.bse_code == req.symbol)
        ).first()

        inst_id = inst.id if inst else str(uuid.uuid4())

        # Resolve market price
        try:
            market_price = self.market_data_service.provider.get_latest_price(req.symbol, req.exchange)
        except Exception:
            market_price = None

        if not market_price:
            market_price = req.requested_price or 100.0

        side_upper = req.side.upper()
        if side_upper not in ("BUY", "SELL"):
            raise HTTPException(status_code=400, detail="Side must be BUY or SELL")

        # Compute execution price with directional slippage
        if side_upper == "BUY":
            exec_price = round(market_price * (1.0 + slippage_pct), 2)
            slippage_cost = round(market_price * slippage_pct * req.quantity, 2)
            gross_val = round(req.quantity * exec_price, 2)
            fee = round(gross_val * fee_pct, 2)
            total_required = gross_val + fee

            if port.cash_balance < total_required:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient virtual cash balance. Required: ₹{total_required:.2f}, Available: ₹{port.cash_balance:.2f}"
                )

            # Deduct cash
            port.cash_balance -= total_required

            # Update or create position
            pos = self.db.query(VirtualPosition).filter_by(portfolio_id=portfolio_id, symbol=req.symbol).first()
            if not pos:
                pos = VirtualPosition(
                    portfolio_id=portfolio_id,
                    instrument_id=inst_id,
                    symbol=req.symbol,
                    exchange=req.exchange,
                    quantity=req.quantity,
                    average_entry_price=exec_price,
                    current_price=exec_price,
                    invested_amount=gross_val,
                    current_value=gross_val
                )
                self.db.add(pos)
            else:
                # Weighted average cost
                old_shares = pos.quantity
                new_shares = old_shares + req.quantity
                new_avg = ((old_shares * pos.average_entry_price) + gross_val) / new_shares
                pos.quantity = new_shares
                pos.average_entry_price = round(new_avg, 2)
                pos.invested_amount = round(new_shares * new_avg, 2)
                pos.current_value = round(new_shares * exec_price, 2)

        elif side_upper == "SELL":
            pos = self.db.query(VirtualPosition).filter_by(portfolio_id=portfolio_id, symbol=req.symbol).first()
            if not pos or pos.quantity < req.quantity:
                available_q = pos.quantity if pos else 0
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient position quantity. Requested sell: {req.quantity}, Available: {available_q}"
                )

            exec_price = round(market_price * (1.0 - slippage_pct), 2)
            slippage_cost = round(market_price * slippage_pct * req.quantity, 2)
            gross_proceeds = round(req.quantity * exec_price, 2)
            fee = round(gross_proceeds * fee_pct, 2)
            net_proceeds = gross_proceeds - fee

            # Credit cash
            port.cash_balance += net_proceeds

            # Calculate realized P&L
            cost_basis = req.quantity * pos.average_entry_price
            realized_pnl_trade = gross_proceeds - cost_basis - fee
            pos.realized_pnl = (pos.realized_pnl or 0.0) + realized_pnl_trade
            pos.quantity -= req.quantity
            pos.invested_amount = round(pos.quantity * pos.average_entry_price, 2)
            pos.current_value = round(pos.quantity * exec_price, 2)

        # Record order
        order = VirtualOrder(
            portfolio_id=portfolio_id,
            instrument_id=inst_id,
            symbol=req.symbol,
            exchange=req.exchange,
            order_type=req.order_type.upper(),
            side=side_upper,
            quantity=req.quantity,
            requested_price=req.requested_price,
            executed_price=exec_price,
            transaction_fee=fee,
            slippage=slippage_cost,
            status="FILLED",
            executed_at=datetime.now(timezone.utc)
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        return VirtualOrderResponse(
            id=order.id,
            portfolio_id=order.portfolio_id,
            symbol=order.symbol,
            exchange=order.exchange,
            order_type=order.order_type,
            side=order.side,
            quantity=order.quantity,
            requested_price=order.requested_price,
            executed_price=order.executed_price,
            transaction_fee=order.transaction_fee,
            slippage=order.slippage,
            status=order.status,
            executed_at=order.executed_at,
            created_at=order.created_at
        )

    def run_scenario_simulation(
        self,
        portfolio_id: str,
        req: ScenarioSimulationRequest
    ) -> ScenarioSimulationResponse:
        """
        Evaluates a What-If market shock scenario across virtual portfolio positions.
        """
        portfolio_resp = self.get_portfolio(portfolio_id)
        base_val = portfolio_resp.total_portfolio_value
        shock = req.shock_pct / 100.0

        # Equity positions bear the full shock
        invested = portfolio_resp.invested_capital
        cash = portfolio_resp.cash_balance

        sim_equity = invested * (1.0 + shock)
        sim_total = round(cash + sim_equity, 2)
        sim_pnl = round(sim_total - base_val, 2)
        sim_pnl_pct = round((sim_pnl / max(base_val, 0.01)) * 100.0, 2)

        name_map = {
            "bull_rally": "Bull Rally Simulation",
            "market_correction": "Market Correction Simulation",
            "severe_bear": "Severe Bear Crash Simulation",
            "rate_hike": "Interest Rate Shock Simulation",
            "sector_shock": "Sector Disruption Simulation"
        }
        s_name = name_map.get(req.scenario_type, f"What-If Shock ({req.shock_pct:+.1f}%)")

        scenario_record = ScenarioSimulation(
            portfolio_id=portfolio_id,
            scenario_name=s_name,
            scenario_type=req.scenario_type,
            market_shock_pct=req.shock_pct,
            simulated_pnl=sim_pnl,
            simulated_portfolio_value=sim_total,
            estimated_max_loss=abs(sim_pnl) if sim_pnl < 0 else 0.0,
            notes=req.notes
        )
        self.db.add(scenario_record)
        self.db.commit()
        self.db.refresh(scenario_record)

        return ScenarioSimulationResponse(
            id=scenario_record.id,
            scenario_name=scenario_record.scenario_name,
            scenario_type=scenario_record.scenario_type,
            shock_pct=scenario_record.market_shock_pct,
            baseline_portfolio_value=base_val,
            simulated_portfolio_value=sim_total,
            simulated_pnl=sim_pnl,
            simulated_pnl_pct=sim_pnl_pct,
            estimated_max_loss=scenario_record.estimated_max_loss or 0.0,
            notes=scenario_record.notes,
            created_at=scenario_record.created_at
        )
