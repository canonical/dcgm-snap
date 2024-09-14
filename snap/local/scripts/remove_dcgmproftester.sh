#!/bin/bash


LIBS_TO_REMOVE=(
    "dcgmproftester*"
    "libdcgm_cublas_proxy*"
    # libs that library linter warn that is unused
    # see https://snapcraft.io/docs/linters-library
    "libnvperf_dcgm_host.so"
    "libnvml_injection.so.1.0"
    "libdcgmmodulesysmon.so.*"
    "libdcgmmoduleprofiling.so.*"
    "libdcgmmodulepolicy.so.*"
    "libdcgmmodulenvswitch.so.*"
    "libdcgmmoduleintrospect.so.*"
    "libdcgmmodulehealth.so.*"
    "libdcgmmodulediag.so.*"
    "libdcgmmoduleconfig.so.*"
)


echo "Removing dcgmproftester libs"


for lib in "${LIBS_TO_REMOVE[@]}"; do
    find "$SNAPCRAFT_PRIME" -type f -name "$lib" | while read -r file; do
        echo "Removing file $file"
        rm -f "$file"
    done
done


echo "Removing libs that are missing cuda libs"
find "$SNAPCRAFT_PRIME" -type d -name "cuda[0-9]*" | while read -r dir; do
    echo "Removing directory $dir"
    rm -rf "$dir"
done

echo "Finished cleanup"
