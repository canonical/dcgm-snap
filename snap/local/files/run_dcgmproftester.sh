#!/bin/bash
set -euo pipefail

# Check if the argument is one of 10, 11, or 12
if [[ "$1" != "10" && "$1" != "11" && "$1" != "12" ]]; then
    exit 1
fi

ARCH=$(uname -m)

if [[ "$ARCH" == "x86_64" ]]; then
    exec "$SNAP/usr/bin/dcgmproftester$1"
elif [[ "$ARCH" == "aarch64" ]]; then
    if [[ "$1" == "10" ]]; then
        exec "$SNAP/usr/bin/dcgmproftester10"
    else
        echo "ERROR: dcgmproftester$1 is not supported on ARM64 platform."
    fi
fi

exit 1
