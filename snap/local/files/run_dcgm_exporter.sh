#!/bin/bash
set -euo pipefail

# Build the argument list for the dcgm-exporter command
args=()

# Add the dcgm-exporter-address option if it is set. Default: “:9400”
dcgm_exporter_address="$(snapctl get dcgm-exporter-address)"
# Add the dcgm-exporter-metrics-file option if it is set.
dcgm_exporter_metrics_file="$(snapctl get dcgm-exporter-metrics-file)"
dcgm_exporter_metrics_file_path="$SNAP_COMMON/$dcgm_exporter_metrics_file"

if [ -n "$dcgm_exporter_address" ]; then
    args+=("-a" "$dcgm_exporter_address")
fi

# File should be available in the snap data directory under $SNAP_COMMON
if [[ -n "$dcgm_exporter_metrics_file" && -f "$dcgm_exporter_metrics_file_path" ]]; then
    args+=("-f" "$dcgm_exporter_metrics_file_path")
fi

exec "$SNAP/bin/dcgm-exporter" "${args[@]}"
