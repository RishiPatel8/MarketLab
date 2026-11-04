from typing import List, Optional, Dict, Any
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_sync_db
from app.db.models.experiment_run import ExperimentRun, ExperimentMetric
from app.db.models.instrument import Instrument
from app.schemas.experiment import ExperimentCreate, ExperimentResponse, ExperimentMetricResponse
from app.services.instrument_service import InstrumentService
from app.services.market_data_service import MarketDataService
from app.services.quantitative_engine import QuantitativeEngine
from app.core.security import get_current_user_or_api_key

router = APIRouter()

@router.post("", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def create_experiment(
    req: ExperimentCreate,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """
    Executes a deterministic quantitative backtest and stores the experiment.
    Prevents look-ahead bias and calculates transaction fees & slippage.
    """
    inst_service = InstrumentService(db)
    inst = None
    if req.instrument_id:
        inst = inst_service.get_by_id(req.instrument_id)
    if not inst and req.symbol:
        res = inst_service.resolve_instrument(req.symbol)
        inst = res.instrument

    if not inst:
        raise HTTPException(status_code=400, detail=f"Could not resolve instrument for experiment ({req.symbol})")

    # Retrieve bars
    md_service = MarketDataService(db)
    bars, val = md_service.get_and_validate_bars(symbol=inst.symbol, exchange=inst.exchange, instrument_id=inst.id)
    benchmark_bars, _ = md_service.get_and_validate_bars(symbol=req.benchmark_symbol, exchange="NSE")

    # Run deterministic backtest
    fast_p = req.parameters.get("fast_period", 20)
    slow_p = req.parameters.get("slow_period", 50)

    try:
        metrics_res = QuantitativeEngine.run_sma_crossover_backtest(
            bars=bars,
            fast_period=fast_p,
            slow_period=slow_p,
            initial_capital=req.initial_capital,
            fee_pct=req.transaction_fee_pct,
            slippage_pct=req.slippage_pct,
            benchmark_bars=benchmark_bars
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Backtest execution failed: {str(e)}")

    exp_id = str(uuid.uuid4())
    db_exp = ExperimentRun(
        id=exp_id,
        instrument_id=inst.id,
        strategy_type=req.strategy_type,
        strategy_configuration=json.dumps(req.parameters),
        dataset_reference=f"OHLCV_{inst.symbol}_bars_{len(bars)}",
        benchmark_symbol=req.benchmark_symbol,
        cost_assumptions=json.dumps({"fee_pct": req.transaction_fee_pct, "slippage_pct": req.slippage_pct}),
        status="completed",
        engine_version=QuantitativeEngine.ENGINE_VERSION
    )
    db.add(db_exp)

    db_metric = ExperimentMetric(
        experiment_run_id=exp_id,
        cagr=metrics_res.cagr,
        sharpe_ratio=metrics_res.sharpe_ratio,
        sortino_ratio=metrics_res.sortino_ratio,
        max_drawdown=metrics_res.max_drawdown,
        calmar_ratio=metrics_res.calmar_ratio,
        annualized_volatility=metrics_res.annualized_volatility,
        win_rate=metrics_res.win_rate,
        profit_factor=metrics_res.profit_factor,
        total_trades=metrics_res.total_trades,
        benchmark_cagr=metrics_res.benchmark_cagr,
        benchmark_max_drawdown=metrics_res.benchmark_max_drawdown,
        equity_curve_json=json.dumps(metrics_res.equity_curve),
        trades_json=json.dumps(metrics_res.trades)
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_exp)

    return ExperimentResponse(
        id=db_exp.id,
        instrument_id=inst.id,
        symbol=inst.symbol,
        strategy_type=db_exp.strategy_type,
        strategy_configuration=req.parameters,
        cost_assumptions={"fee_pct": req.transaction_fee_pct, "slippage_pct": req.slippage_pct},
        status=db_exp.status,
        engine_version=db_exp.engine_version,
        created_at=db_exp.created_at,
        metrics=metrics_res
    )

@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment_details(
    experiment_id: str,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Retrieves stored experiment configuration, trade series, and evaluation metrics."""
    exp = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    inst = db.query(Instrument).filter(Instrument.id == exp.instrument_id).first()
    m = db.query(ExperimentMetric).filter(ExperimentMetric.experiment_run_id == experiment_id).first()

    metric_resp = None
    if m:
        metric_resp = ExperimentMetricResponse(
            cagr=m.cagr,
            sharpe_ratio=m.sharpe_ratio,
            sortino_ratio=m.sortino_ratio,
            max_drawdown=m.max_drawdown,
            calmar_ratio=m.calmar_ratio,
            annualized_volatility=m.annualized_volatility,
            win_rate=m.win_rate,
            profit_factor=m.profit_factor,
            total_trades=m.total_trades,
            benchmark_cagr=m.benchmark_cagr,
            benchmark_max_drawdown=m.benchmark_max_drawdown,
            equity_curve=json.loads(m.equity_curve_json) if m.equity_curve_json else [],
            trades=json.loads(m.trades_json) if m.trades_json else []
        )

    return ExperimentResponse(
        id=exp.id,
        instrument_id=exp.instrument_id,
        symbol=inst.symbol if inst else "UNKNOWN",
        strategy_type=exp.strategy_type,
        strategy_configuration=json.loads(exp.strategy_configuration),
        cost_assumptions=json.loads(exp.cost_assumptions),
        status=exp.status,
        engine_version=exp.engine_version,
        created_at=exp.created_at,
        metrics=metric_resp
    )

@router.post("/{experiment_id}/rerun", response_model=ExperimentResponse)
def rerun_experiment(
    experiment_id: str,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Creates a new versioned experiment run using the stored configuration."""
    existing = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Original experiment not found")

    params = json.loads(existing.strategy_configuration)
    costs = json.loads(existing.cost_assumptions)

    create_req = ExperimentCreate(
        instrument_id=existing.instrument_id,
        strategy_type=existing.strategy_type,
        parameters=params,
        transaction_fee_pct=costs.get("fee_pct", 0.001),
        slippage_pct=costs.get("slippage_pct", 0.0005),
        benchmark_symbol=existing.benchmark_symbol
    )
    return create_experiment(create_req, db, user)

@router.delete("/{experiment_id}", status_code=status.HTTP_200_OK)
def delete_experiment(
    experiment_id: str,
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Deletes a specific backtest experiment and its metrics."""
    exp = db.query(ExperimentRun).filter(ExperimentRun.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
    db.query(ExperimentMetric).filter(ExperimentMetric.experiment_run_id == experiment_id).delete()
    db.delete(exp)
    db.commit()
    return {"status": "success", "message": f"Experiment {experiment_id} deleted successfully"}

@router.delete("", status_code=status.HTTP_200_OK)
def clear_all_experiments(
    db: Session = Depends(get_sync_db),
    user: dict = Depends(get_current_user_or_api_key)
):
    """Clears all historical experiments and metrics."""
    db.query(ExperimentMetric).delete()
    count = db.query(ExperimentRun).delete()
    db.commit()
    return {"status": "success", "deleted_count": count, "message": "All experiments cleared successfully"}
