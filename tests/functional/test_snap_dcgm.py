import subprocess
import time


def test_dcgm_exporter_endpoint():
    """Test of the dcgm-exporter service and its endpoint."""
    endpoint = "localhost:9400/metrics"
    timeout = 60  # seconds
    start_time = time.time()

    def query_endpoint():
        return subprocess.run(["curl", endpoint], text=True, capture_output=True)

    while (result := query_endpoint()).returncode != 0 or not result.stdout.strip():
        if time.time() - start_time > timeout:
            assert False, f"Failed to reach '{endpoint}' of the dcgm-exporter service"
        time.sleep(5)

    assert "DCGM_FI_DRIVER_VERSION" in result.stdout, "No dcgm exported metrics found"


def test_dcgm_configs():
    """Test snap configuratin."""
    pass


def test_dcgm_nv_hostengine():
    """Test of the dcgm-nv-hostengine service and its endpoint."""
    pass


def test_dcgmi():
    """Test of the dcgmi command."""
    pass


def test_dcgmproftesters():
    """Test of the dcgmproftesters."""
    pass
