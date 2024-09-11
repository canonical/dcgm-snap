import os
import subprocess
import time

import pytest


@pytest.fixture(scope="session", autouse=True)
def install_dcgm_snap():
    """Install the snap and enable dcgm-exporter service for testing."""
    snap = os.environ["TEST_SNAP"]
    dcgm_exporter_service = "snap.dcgm.dcgm-exporter.service"

    assert (
        0 == subprocess.run(["sudo", "snap", "install", "--dangerous", snap]).returncode
    ), f"Failed to install {snap}"

    subprocess.run(["sudo", "systemctl", "enable", "--now", dcgm_exporter_service])

    dcgm_exporter_is_active = (
        lambda: subprocess.call(
            ["sudo", "systemctl", "is-active", "--quiet", dcgm_exporter_service]
        )
        == 0
    )

    timeout = 30  # seconds
    start_time = time.time()

    while not dcgm_exporter_is_active():
        if time.time() - start_time > timeout:
            assert False, f"Failed to start {dcgm_exporter_service} service"
        time.sleep(5)

    yield

    subprocess.run(["sudo", "snap", "remove", "--purge", "dcgm"])
