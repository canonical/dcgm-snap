import json
import os
import subprocess
import urllib.request

import pytest
from tenacity import Retrying, retry, stop_after_delay, wait_fixed


class TestDCGMComponents:
    @classmethod
    def check_service_active(cls, service: str):
        assert 0 == subprocess.call(
            f"sudo systemctl is-active --quiet {service}".split()
        ), f"{service} is not running"

    @retry(wait=wait_fixed(5), stop=stop_after_delay(30))
    def test_dcgm_exporter(self) -> None:
        """Test of the dcgm-exporter service and its endpoint."""
        dcgm_exporter_service = "snap.dcgm.dcgm-exporter"
        endpoint = "http://localhost:9400/metrics"

        self.check_service_active(dcgm_exporter_service)

        # Will raise an exception if the endpoint is not reachable
        response = urllib.request.urlopen(endpoint)

        # The output of the exporter endpoint is not tested
        # as in a virtual environment it will not have any GPU metrics
        assert 200 == response.getcode(), "DCGM exporter endpoint returned an error"

    def test_dcgm_nv_hostengine(self) -> None:
        """Check the dcgm-nv-hostengine service."""
        nv_hostengine_service = "snap.dcgm.nv-hostengine"
        nv_hostengine_port = 5555

        self.check_service_active(nv_hostengine_service)

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
    def set_config(cls, service: str, config: str, value: str = "") -> None:
        """Set a configuration value for a snap service."""
        assert 0 == subprocess.call(
            f"sudo snap set dcgm {config}={value}".split()
        ), f"Failed to set {config} to {value}"

        # restart the service to apply the configuration
        subprocess.run(f"sudo snap restart {service}".split(), check=True)

    @classmethod
    def check_bind_config(cls, service: str, bind: str) -> None:
        """Check if a service is listening on a specific bind."""
        for attempt in Retrying(wait=wait_fixed(2), stop=stop_after_delay(10)):
            with attempt:
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
    def check_metric_config(cls, metric_file: str) -> None:
        dcgm_exporter_service = "snap.dcgm.dcgm-exporter"

        result = subprocess.check_output(
            f"sudo systemctl show -p ActiveEnterTimestamp {dcgm_exporter_service}".split(),
            text=True,
        )

        start_timestamp = result.strip().split("=")[1]

        result = subprocess.check_output(
            f"sudo journalctl -u {dcgm_exporter_service} --since '{start_timestamp}'",
            shell=True,
            text=True,
        )

        assert metric_file in result, f"Metric file {metric_file} is not loaded"

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

        self.set_config(service, config, new_value)
        self.check_bind_config(service, new_value)

        # Revert back
        self.set_config(service, config, old_value)
        self.check_bind_config(service, old_value)

    def test_dcgm_metric_config(self) -> None:
        service = "dcgm.dcgm-exporter"
        config = "dcgm-exporter-metrics-file"
        metric_file = "test-metrics.csv"
        metric_file_path = os.path.join(os.getenv("SNAP_COMMON"), metric_file)

        self.get_config(config)

        # $SNAP_COMMON requires root permissions to create a file
        subprocess.check_call(f"sudo touch {metric_file_path}".split())

        self.set_config(service, config, metric_file)
        self.check_metric_config(metric_file_path)

        # Revet back
        self.set_config(service, config)
        self.check_metric_config("default-counters.csv")

        subprocess.check_call(f"sudo rm {metric_file_path}".split())
