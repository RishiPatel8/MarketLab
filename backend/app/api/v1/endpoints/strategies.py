from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_sync_db
from app.core.security import get_current_user_or_api_key
from app.analytics.strategy_engine import StrategyRegistry
from app.schemas.strategy import (
    StrategyDefinitionSchema,
    StrategyRunRequest,
    MultiStrategyRunRequest,
    StrategyConsensusResult
)
from app.schemas.experiment import ExperimentMetricResponse
from app.services.market_data_service import MarketDataService

router = APIRouter()

@router.get("", response_model=List[StrategyDefinitionSchema])
def list_available_strategies():
    """Lists all 10 registered quantitative strategy definitions, categories, and parameter schemas."""
    return StrategyRegistry.list_strategies()

@router.post("/run", response_model=ExperimentMetricResponse)
def run_strategy_backtest(
    req: StrategyRunRequest,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Executes a deterministic historical backtest for a specific strategy."""
    md_service = MarketDataService(db)
    bars, val = md_service.get_and_validate_bars(symbol=req.symbol, exchange=req.exchange)
    if not bars:
        raise HTTPException(status_code=400, detail=f"No market data available for {req.symbol}")

    bench_bars, _ = md_service.get_and_validate_bars(symbol=req.benchmark_symbol, exchange="NSE")

    try:
        return StrategyRegistry.run_strategy(
            key=req.strategy_key,
            bars=bars,
            parameters=req.parameters,
            initial_capital=req.initial_capital,
            fee_pct=req.fee_pct,
            slippage_pct=req.slippage_pct,
            benchmark_bars=bench_bars
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Strategy execution error: {str(e)}")

@router.post("/consensus", response_model=StrategyConsensusResult)
def evaluate_strategy_consensus(
    req: MultiStrategyRunRequest,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Executes an ensemble of strategies and synthesizes their consensus BUY/HOLD/SELL vote."""
    md_service = MarketDataService(db)
    bars, val = md_service.get_and_validate_bars(symbol=req.symbol, exchange=req.exchange)
    if not bars:
        raise HTTPException(status_code=400, detail=f"No market data available for {req.symbol}")

    bench_bars, _ = md_service.get_and_validate_bars(symbol="^NSEI", exchange="NSE")

    return StrategyRegistry.run_multi_strategy_consensus(
        bars=bars,
        strategy_keys=req.strategy_keys,
        initial_capital=req.initial_capital,
        benchmark_bars=bench_bars
    )
