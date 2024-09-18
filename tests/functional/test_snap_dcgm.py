import json
import os
import subprocess
import urllib.request

import pytest
from tenacity import retry, stop_after_delay, wait_fixed


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _check_service_active(service: str) -> None:
    """Check if a service is active."""
    assert 0 == subprocess.call(
        f"sudo systemctl is-active --quiet {service}".split()
    ), f"{service} is not running"


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _check_service_failed(service: str) -> None:
    """Check if a service is in a failed state."""
    assert 0 == subprocess.call(
        f"sudo systemctl is-failed --quiet {service}".split()
    ), f"{service} is running"


@retry(wait=wait_fixed(5), stop=stop_after_delay(30))
def _check_endpoint(endpoint: str) -> None:
    """Check if an endpoint is reachable."""
    response = urllib.request.urlopen(endpoint)  # will raise if not reachable
    status_code = response.getcode()
    assert status_code == 200, f"Endpoint {endpoint} returned status code {status_code}"


class TestDCGMComponents:
    def test_dcgm_exporter(self) -> None:
        """Test of the dcgm-exporter service and its endpoint."""
        dcgm_exporter_service = "snap.dcgm.dcgm-exporter"
        endpoint = "http://localhost:9400/metrics"

        _check_service_active(dcgm_exporter_service)
        # The output of the exporter endpoint is not tested
        # as in a virtual environment it will not have any GPU metrics
        _check_endpoint(endpoint)

    def test_dcgm_nv_hostengine(self) -> None:
        """Check the dcgm-nv-hostengine service."""
        nv_hostengine_service = "snap.dcgm.nv-hostengine"
        nv_hostengine_port = 5555

        _check_service_active(nv_hostengine_service)

        assert 0 == subprocess.call(
            f"nc -z localhost {nv_hostengine_port}".split()
        ), f"{nv_hostengine_service} is not listening on port {nv_hostengine_port}"

    def test_dcgmi(self) -> None:
        """Test of the dcgmi command."""
        result = subprocess.check_output("dcgm.dcgmi discovery -l".split(), text=True)

        # Test if the command is working and outputs a table with the GPU ID
        # The table will be empty in a virtual environment, but the command should still work
        assert "GPU ID" in result.strip(), "DCGMI didn't produce the expected table"


class TestDCGMConfigs:
    @classmethod
    @retry(wait=wait_fixed(2), stop=stop_after_delay(10))
    def set_config(cls, service: str, config: str, value: str = "") -> None:
        """Set a configuration value for a snap service."""
        assert 0 == subprocess.call(
            f"sudo snap set dcgm {config}={value}".split()
        ), f"Failed to set {config} to {value}"

        subprocess.run(f"sudo snap restart {service}".split(), check=True)

    @classmethod
    @retry(wait=wait_fixed(2), stop=stop_after_delay(10))
    def check_bind_config(cls, service: str, bind: str) -> None:
        """Check if a service is listening on a specific bind."""
        assert 0 == subprocess.call(
            f"nc -z localhost {bind.lstrip(':')}".split()
        ), f"{service} is not listening on {bind}"

    @classmethod
    def get_config(cls, config: str) -> str:
        """Check if a configuration exists in the snap configuration.

        :return: The value of the current configuration
        """
        result = subprocess.check_output("sudo snap get dcgm -d".split(), text=True)
        dcgm_snap_config = json.loads(result.strip())
        assert config in dcgm_snap_config, f"{config} is not in the snap configuration"
        return str(dcgm_snap_config[config])

    @classmethod
    @retry(wait=wait_fixed(2), stop=stop_after_delay(10))
    def check_metric_config(cls, metric_file: str = "") -> None:
        """Check if the metric file is loaded in the dcgm-exporter service.

        :param metric_file: The metric file to check for, if empty check if nothing is loaded
        """
        result = subprocess.check_output(
            "ps -eo cmd | grep '/bin/[d]cgm-exporter'", shell=True, text=True
        )

        if metric_file:
            assert f"-f {metric_file}" in result, f"Metric file {metric_file} is not loaded"
        else:
            assert "-f" not in result.split(), "Metric file is loaded, but should not be"

    @pytest.mark.parametrize(
        "service, config, new_value",
        [
            ("dcgm.dcgm-exporter", "dcgm-exporter-address", ":9466"),
            ("dcgm.nv-hostengine", "nv-hostengine-port", "5566"),
        ],
    )
    def test_dcgm_bind_config(self, service: str, config: str, new_value: str) -> None:
        """Test snap bind configuration."""
        old_value = self.get_config(config)

        # Valid config
        self.set_config(service, config, new_value)
        self.check_bind_config(service, new_value)

        # Invalid config
        self.set_config(service, config, "test")
        _check_service_failed(f"snap.{service}")

        # Revert back
        self.set_config(service, config, old_value)
        self.check_bind_config(service, old_value)

    def test_dcgm_metric_config(self) -> None:
        """Test the metric file configuration of the dcgm-exporter service."""
        service = "dcgm.dcgm-exporter"
        config = "dcgm-exporter-metrics-file"
        metric_file = "test-metrics.csv"
        endpoint = "http://localhost:9400/metrics"
        metric_file_path = os.path.join("/var/snap/dcgm/common", metric_file)

        self.get_config(config)

        # $SNAP_COMMON requires root permissions to create a file
        subprocess.check_call(f"sudo touch {metric_file_path}".split())

        # Empty metric
        self.set_config(service, config, metric_file)
        self.check_metric_config()
        _check_endpoint(endpoint)

        # Non-existing metric
        self.set_config(service, config, "unknown.csv")
        self.check_metric_config()
        _check_endpoint(endpoint)

        # Invalid metric
        subprocess.check_call(f"echo 'test' | sudo tee {metric_file_path}", shell=True)
        self.set_config(service, config, metric_file)
        # The exporter will fail to start due to the invalid metric file
        _check_service_failed(f"snap.{service}")

        # Valid metric
        subprocess.check_call(
            f"echo 'DCGM_FI_DRIVER_VERSION, label, Driver Version' | sudo tee {metric_file_path}",
            shell=True,
        )
        self.set_config(service, config, metric_file)
        self.check_metric_config(metric_file_path)
        _check_endpoint(endpoint)

        # Revert back
        self.set_config(service, config)
        self.check_metric_config()

        subprocess.check_call(f"sudo rm {metric_file_path}".split())
