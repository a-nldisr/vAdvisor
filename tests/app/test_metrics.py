import vadvisor
import pytest
import webtest
from vadvisor.store.collector import InMemoryStore as MetricStore


@pytest.fixture
def _app():

    class Collector:

        def collect(self):
            return []

    app = vadvisor.app.rest.app
    app.collector = Collector()
    app.metricStore = MetricStore()
    return app


@pytest.fixture
def app(_app):
    return webtest.TestApp(_app)


def test_metrics(app):
    resp = app.get("/metrics")
    assert resp.status_int == 200
    assert "process_virtual_memory_bytes" in resp


def test_vms(app):
    resp = app.get("/api/v1.0/stats").follow()
    assert resp.status_int == 200
    assert resp.json == {}
