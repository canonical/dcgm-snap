import subprocess

import pytest
import yaml


@pytest.fixture(scope="session", autouse=True)
def install_dcgm_snap():
    """Install the snap and enable dcgm-exporter service for testing."""
    with open("snap/snapcraft.yaml") as f:
        snapcraft = yaml.safe_load(f)
        snap_build_name = f"{snapcraft['name']}_*_amd64.snap"

        subprocess.run(
            f"sudo snap install --devmode {snap_build_name}",
            check=True,
            capture_output=True,
            shell=True,
        )

        yield

        subprocess.run("sudo snap remove --purge dcgm".split(), check=True)
