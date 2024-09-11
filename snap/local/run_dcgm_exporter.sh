#!/bin/bash
set -euo pipefail

# Build the argument list for the dcgm-exporter command
args=()

# Add the dcgm-exporter-port option if it is set. Default: “:9400”
dcgm_exporter_listen="$(snapctl get dcgm-exporter-listen)"

if [ -n "$dcgm_exporter_listen" ]; then
    args+=("-a" "$dcgm_exporter_listen")
fi

exec "$SNAP/bin/dcgm-exporter" "${args[@]}"
