from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_sync_db
from app.core.security import get_current_user_or_api_key
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import (
    VirtualPortfolioCreate,
    VirtualPortfolioResponse,
    VirtualOrderCreate,
    VirtualOrderResponse,
    ScenarioSimulationRequest,
    ScenarioSimulationResponse
)

router = APIRouter()

@router.post("", response_model=VirtualPortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_virtual_portfolio(
    req: VirtualPortfolioCreate,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Creates a new virtual portfolio with initial starting capital in INR."""
    service = PortfolioService(db)
    user_id = user.get("id") if isinstance(user, dict) else None
    return service.create_portfolio(req, user_id=user_id)

@router.get("", response_model=List[VirtualPortfolioResponse])
def list_virtual_portfolios(
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Lists all active virtual portfolios."""
    service = PortfolioService(db)
    user_id = user.get("id") if isinstance(user, dict) else None
    return service.list_portfolios(user_id=user_id)

@router.get("/{portfolio_id}", response_model=VirtualPortfolioResponse)
def get_virtual_portfolio(
    portfolio_id: str,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Returns real-time mark-to-market holdings, cash balance, and P&L for a virtual portfolio."""
    service = PortfolioService(db)
    return service.get_portfolio(portfolio_id)

@router.post("/{portfolio_id}/orders", response_model=VirtualOrderResponse)
def execute_virtual_order(
    portfolio_id: str,
    req: VirtualOrderCreate,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Executes a virtual paper trade (BUY or SELL) with realistic slippage and fee accounting."""
    service = PortfolioService(db)
    return service.execute_order(portfolio_id, req)

@router.post("/{portfolio_id}/scenarios", response_model=ScenarioSimulationResponse)
def run_scenario_simulation(
    portfolio_id: str,
    req: ScenarioSimulationRequest,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Evaluates What-If stress tests (market correction, bull rally, severe crash) across portfolio positions."""
    service = PortfolioService(db)
    return service.run_scenario_simulation(portfolio_id, req)
