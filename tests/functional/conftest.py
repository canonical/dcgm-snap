import os
import subprocess
from time import sleep

import pytest


@pytest.fixture(scope="session", autouse=True)
def install_dcgm_snap():
    """Install the snap and enable dcgm-exporter service for testing."""
    snap = os.environ["TEST_SNAP"]
    dcgm_exporter_service = "snap.dcgm.dcgm-exporter.service"
    assert 0 == subprocess.run(["sudo", "snap", "install", "--dangerous", snap]).returncode

    subprocess.run(["sudo", "systemctl", "enable", "--now", dcgm_exporter_service])
    sleep(5)  # Give some time for the service to start

    assert (
        0
        == subprocess.run(
            ["sudo", "systemctl", "is-active", "--quiet", dcgm_exporter_service]
        ).returncode
    )

    yield

    subprocess.run(["sudo", "snap", "remove", "--purge", "dcgm"])
