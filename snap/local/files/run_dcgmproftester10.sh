#!/bin/bash
set -euo pipefail

# Due to limitations of the snapcraft.yaml, this wrapper is needed for the build to not fail for ARM, 
# as there is no dcgmproftester10 in the ARM DCGM deb package

BINARY="$SNAP/usr/bin/dcgmproftester10"

if [[ -x "$BINARY" ]]; then
    exec "$BINARY"
else
    echo "ERROR: dcgmproftester10 is not supported on the $(uname -m) platform."
    exit 127
fi
