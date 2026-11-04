import pytest
import time

def test_health_endpoints(client):
    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"

    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"

def test_instrument_search(client):
    res = client.get("/api/v1/instruments/search?q=green")
    assert res.status_code == 200
    data = res.json()
    items = data["items"] if "items" in data else data
    assert len(items) >= 1
    symbols = [item["symbol"] for item in items]
    assert "GREENPOWER" in symbols

def test_experiment_creation_and_retrieval(client):
    req_body = {
        "symbol": "GREENPOWER",
        "parameters": {"fast_period": 20, "slow_period": 50},
        "initial_capital": 100000.0,
        "transaction_fee_pct": 0.001,
        "slippage_pct": 0.0005
    }
    res = client.post("/api/v1/experiments", json=req_body)
    assert res.status_code == 201
    exp = res.json()
    assert exp["symbol"] == "GREENPOWER"
    assert exp["metrics"]["cagr"] is not None
    assert len(exp["metrics"]["equity_curve"]) > 50

    # Retrieve by ID
    exp_id = exp["id"]
    get_res = client.get(f"/api/v1/experiments/{exp_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == exp_id

def test_research_run_and_report_lifecycle(client):
    # Queue research run
    res = client.post("/api/v1/research", json={"question": "Research Orient Green Power for a six-month horizon"})
    assert res.status_code == 202
    run_id = res.json()["run_id"]

    # Poll status until completed
    completed = False
    for _ in range(30):
        st = client.get(f"/api/v1/research/{run_id}").json()
        if st["status"] in ("completed", "completed_with_limitations"):
            completed = True
            break
        time.sleep(0.5)

    assert completed is True

    # Retrieve generated cited report
    rep_res = client.get(f"/api/v1/research/{run_id}/report")
    assert rep_res.status_code == 200
    report = rep_res.json()
    assert report["run_id"] == run_id
    assert report["instrument"]["symbol"] == "GREENPOWER"
    assert len(report["sources"]) > 0
    assert report["verification"]["verification_passed"] is True
