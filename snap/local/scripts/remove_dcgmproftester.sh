#!/bin/bash


FILES_TO_REMOVE=(
    "dcgmproftester*"
    "libdcgm_cublas_proxy*"
)


echo "Removing dcgmproftester libs"


for lib in "${FILES_TO_REMOVE[@]}"; do
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
