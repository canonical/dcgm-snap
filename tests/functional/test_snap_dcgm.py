import json
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


def test_dcgm_nv_hostengine():
    """Check the dcgm-nv-hostengine service."""
    assert 0 == subprocess.call(
        ["sudo", "systemctl", "is-active", "--quiet", "snap.dcgm.nv-hostengine.service"]
    ), "DCGM NV Hostengine service is not running"


def test_dcgmi():
    """Test of the dcgmi command."""
    result = subprocess.run(["dcgm.dcgmi", "discovery", "-l"], check=True, capture_output=True, text=True)
    assert "GPU ID" in result.stdout.strip(), "DCGMI is not working"


def test_dcgmproftesters():
    """Test of the dcgmproftesters."""
    pass


def test_dcgm_port_configs():
    """Test snap port configuratin."""
    services = ["dcgm.dcgm-exporter", "dcgm.nv-hostengine"]
    configs = ["dcgm-exporter-listen", "nv-hostengine-port"]
    new_values = [":9466", "5666"]

    result = subprocess.run(
        ["sudo", "snap", "get", "dcgm", "-d"], check=True, capture_output=True, text=True
    )
    dcgm_snap_config = json.loads(result.stdout.strip())
    assert all(config in dcgm_snap_config for config in configs), "Missing snap configuration keys"

    for config, new_value in zip(configs, new_values):
        assert 0 == subprocess.call(
            ["sudo", "snap", "set", "dcgm", f"{config}={new_value}"]
        ), f"Failed to set snap configuration key '{config}'"

    # restart the service to apply the new configuration
    for service in services:
        subprocess.run(["sudo", "snap", "restart", service])

    for service, port in zip(services, new_values):
        assert 0 == subprocess.call(
            ["sudo", "lsof", "-i", f":{port.lstrip(':')}"]
        ), f"{service} port is not listening"
