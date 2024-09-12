import json
import subprocess
import urllib.request
from time import sleep

from tenacity import retry, stop_after_delay, wait_fixed


@retry(wait=wait_fixed(5), stop=stop_after_delay(15))
def test_dcgm_exporter():
    """Test of the dcgm-exporter service and its endpoint."""
    endpoint = "http://localhost:9400/metrics"
    dcgm_exporter_service = "dcgm.dcgm-exporter"

    subprocess.run(f"sudo snap start {dcgm_exporter_service}".split(), check=True)

    result = subprocess.run(
        f"sudo snap services {dcgm_exporter_service}".split(),
        check=True,
        capture_output=True,
        text=True,
    )
    assert " active" in result.stdout.strip(), "dcgm-exporter service is not active"

    urllib.request.urlopen(endpoint)


def test_dcgm_nv_hostengine():
    """Check the dcgm-nv-hostengine service."""
    nv_hostengine_service = "dcgm.nv-hostengine"

    service = subprocess.run(
        f"snap services {nv_hostengine_service}".split(),
        check=True,
        capture_output=True,
        text=True,
    )

    assert " active" in service.stdout.strip(), "nv-hostengine service is not active"


def test_dcgmi():
    """Test of the dcgmi command."""
    result = subprocess.run(
        "dcgm.dcgmi discovery -l".split(), check=True, capture_output=True, text=True
    )
    assert "GPU ID" in result.stdout.strip(), "DCGMI is not working"


def test_dcgm_port_configs():
    """Test snap port configuratin."""
    services = ["dcgm.dcgm-exporter", "dcgm.nv-hostengine"]
    configs = ["dcgm-exporter-address", "nv-hostengine-port"]
    new_values = [":9466", "5666"]

    result = subprocess.run(
        "sudo snap get dcgm -d".split(), check=True, capture_output=True, text=True
    )
    dcgm_snap_config = json.loads(result.stdout.strip())
    assert all(config in dcgm_snap_config for config in configs), "Missing snap configuration keys"

    for config, new_value in zip(configs, new_values):
        subprocess.run(
            f"sudo snap set dcgm {config}={new_value}".split(), check=True
        ), f"Failed to set {config}"

    # restart the service to apply the new configuration
    for service in services:
        subprocess.run(f"sudo snap restart {service}".split(), check=True)

    sleep(5)

    for service, port in zip(services, new_values):
        subprocess.run(
            f"sudo lsof -i :{port.lstrip(':')}".split(), check=True
        ), f"{service} port is not listening"
