import threading
import urllib.request
import pytest
import importlib.util
import os
import sys
from http.server import HTTPServer


# current_dir is the 'test/' directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level, then into 'app', and target 'app.py'
app_path = os.path.abspath(os.path.join(current_dir, "..", "app", "app.py"))

if not os.path.exists(app_path):
    raise FileNotFoundError(f"Could not find app.py at {app_path}")

# Load the file explicitly bypassing any folder naming conflicts
spec = importlib.util.spec_from_file_location("app_module", app_path)
app = importlib.util.module_from_spec(spec)
sys.modules["app_module"] = app
spec.loader.exec_module(app)

# Extract the classes we need from the explicitly loaded file
HealthCheckHandler = app.HealthCheckHandler
run_server = app.run_server


# ──────────────────────────────────────────────
# Test Server Fixture
# ──────────────────────────────────────────────
@pytest.fixture(scope="module")
def test_server():
    """Start the app's HTTP server on a random free port for the test session."""
    server = HTTPServer(("127.0.0.1", 0), HealthCheckHandler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield port  # provide the port to tests

    server.shutdown()


# ──────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────
def test_healthcheck_status_200(test_server):
    port = test_server
    url = f"http://127.0.0.1:{port}/healthcheck"
    response = urllib.request.urlopen(url)
    assert response.status == 200, "Expected HTTP 200 from /healthcheck"

def test_healthcheck_response_body(test_server):
    port = test_server
    url = f"http://127.0.0.1:{port}/healthcheck"
    response = urllib.request.urlopen(url)
    body = response.read().decode("utf-8")
    assert "healthy" in body

def test_healthcheck_content_type(test_server):
    port = test_server
    url = f"http://127.0.0.1:{port}/healthcheck"
    response = urllib.request.urlopen(url)
    content_type = response.headers.get("Content-type", "")
    assert "application/json" in content_type

def test_unknown_route_returns_404(test_server):
    port = test_server
    url = f"http://127.0.0.1:{port}/unknown"
    try:
        urllib.request.urlopen(url)
        assert False, "Expected HTTPError 404 but got a 200 response"
    except urllib.error.HTTPError as e:
        assert e.code == 404, f"Expected 404, got {e.code}"

def test_memory_increment_calculation():
    target_increase_mb = 400
    duration_seconds = 120
    expected_increment = target_increase_mb / duration_seconds
    increment_bytes = int(expected_increment * 1024 * 1024)

    assert increment_bytes > 0, "Increment bytes must be positive"
    assert 3_000_000 < increment_bytes < 4_000_000

def test_log_message_suppressed(capsys):
    handler = HealthCheckHandler.__new__(HealthCheckHandler)
    handler.log_message("GET /healthcheck HTTP/1.1", 200, "-")
    captured = capsys.readouterr()
    assert captured.out == "", "log_message should produce no stdout output"
    assert captured.err == "", "log_message should produce no stderr output"
