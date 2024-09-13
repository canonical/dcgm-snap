import subprocess

import pytest
from tenacity import retry, stop_after_delay, wait_fixed


@retry(wait=wait_fixed(5), stop=stop_after_delay(20))
def check_dcgm_exporter_service():
    dcgm_exporter_service = "dcgm.dcgm-exporter"

    result = subprocess.run(
        f"sudo snap services {dcgm_exporter_service}".split(),
        check=True,
        capture_output=True,
        text=True,
    )
    assert " active" in result.stdout.strip(), f"{dcgm_exporter_service} service is not active"


@pytest.fixture(scope="session", autouse=True)
def install_dcgm_snap():
    """Install the snap and enable dcgm-exporter service for testing."""
    snap_build_name = "dcgm_*.snap"

    subprocess.run(
        f"sudo snap install --dangerous {snap_build_name}",
        check=True,
        capture_output=True,
        shell=True,
    )

    subprocess.run("sudo snap start dcgm.dcgm-exporter".split(), check=True)
    check_dcgm_exporter_service()

    yield

    subprocess.run("sudo snap remove --purge dcgm".split(), check=True)
