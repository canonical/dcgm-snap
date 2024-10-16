#!/bin/bash
set -euo pipefail

if [[ "$1" != "10" && "$1" != "11" && "$1" != "12" ]]; then
    exit 1
fi

BINARY="$SNAP/usr/bin/dcgmproftester$1"
ARCH=$(uname -m)

if [[ -x "$BINARY" ]]; then
    exec "$BINARY"
else
    echo "ERROR: dcgmproftester$1 is not supported on the $ARCH platform."
    exit 1
fi
