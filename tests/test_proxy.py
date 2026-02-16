from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/get")
def get_route():
    return {"message": "success"}


@app.get("/timeout-test")
def timeout_route():
    raise HTTPException(status_code=504, detail="Upstream timeout")


client = TestClient(app)


def test_proxy_success():
    response = client.get("/get")
    assert response.status_code == 200
    assert response.json() == {"message": "success"}


def test_proxy_timeout():
    response = client.get("/timeout-test")
    assert response.status_code == 504
    assert "Upstream timeout" in response.text
