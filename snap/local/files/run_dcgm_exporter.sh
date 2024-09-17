#!/bin/bash
set -euo pipefail

# Build the argument list for the dcgm-exporter command
args=()

# Check if the nv-hostengine-port option is set.
nv_hostengine_port="$(snapctl get nv-hostengine-port)"
# Add the dcgm-exporter-address option if it is set. Default: “:9400”
dcgm_exporter_address="$(snapctl get dcgm-exporter-address)"

if [ -n "$dcgm_exporter_address" ]; then
    args+=("-a" "$dcgm_exporter_address")
fi

if [ -n "$nv_hostengine_port" ]; then
    args+=("-r" "localhost:$nv_hostengine_port")
fi

exec "$SNAP/bin/dcgm-exporter" "${args[@]}"
