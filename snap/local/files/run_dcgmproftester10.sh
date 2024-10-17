#!/bin/bash
set -euo pipefail

# Due to limitations of the snapcraft.yaml syntax, apps cannot be enabled or disabled depending on the build architecture. This wrapper allows the ARM build to not fail and avoids having to maintain two separate snapcraft.yaml files 
# as there is no dcgmproftester10 in the ARM DCGM deb package

BINARY="$SNAP/usr/bin/dcgmproftester10"

if [[ -x "$BINARY" ]]; then
    exec "$BINARY"
else
    echo "ERROR: dcgmproftester10 is not supported on the $(uname -m) platform."
    exit 127
fi
