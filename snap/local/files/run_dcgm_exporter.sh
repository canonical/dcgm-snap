#!/bin/bash
set -euo pipefail

# Build the argument list for the dcgm-exporter command
# startup validation dynamic generates and check libs that are not possible in snap confinement
# See https://github.com/NVIDIA/dcgm-exporter/issues/553
args=("--disable-startup-validate")

nv_hostengine_port="$(snapctl get nv-hostengine-port)"
dcgm_exporter_address="$(snapctl get dcgm-exporter-address)"
dcgm_exporter_metrics_file="$(snapctl get dcgm-exporter-metrics-file)"

if [ -n "$dcgm_exporter_address" ]; then
    args+=("-a" "$dcgm_exporter_address")
fi

if [ -n "$nv_hostengine_port" ]; then
    args+=("-r" "localhost:$nv_hostengine_port")
fi

# File should be available in the snap data directory under $SNAP_COMMON
if [ -n "$dcgm_exporter_metrics_file" ]; then
    args+=("-f" "$SNAP_COMMON/$dcgm_exporter_metrics_file")
else
    echo "Using default DCGM exporter metrics file."
fi

exec "dcgm-exporter" "${args[@]}"
