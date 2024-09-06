import subprocess
from time import sleep


def test_dcgm_exporter_endpoint():
    """Smoke test of the dcgm-exporter service and its endpoint."""
    dcgm_exporter_endpoint = "localhost:9400/metrics"
    subprocess.run(["sudo", "snap", "disconnect", "dcgm:network-bind"])

    # The Endpoint should be unavailable with the networking plug
    assert 0 != subprocess.run(["curl", dcgm_exporter_endpoint]).returncode

    subprocess.run(["sudo", "snap", "connect", "dcgm:network-bind"])
    print("reconnect")
    sleep(5)  # should be sufficient for the service to restart

    assert 0 == subprocess.run(["curl", dcgm_exporter_endpoint]).returncode
