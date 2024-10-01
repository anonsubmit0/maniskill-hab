#!/usr/bin/bash

sources=(ycb ReplicaCAD ReplicaCADRearrange)

for s in "${sources[@]}"
do
    echo "downloading $s"
    python -m anonymized_asset_download.download_asset "$s" -y
    echo ""
done
