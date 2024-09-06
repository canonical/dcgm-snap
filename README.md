# DCGM Snap

This is a snap delivering NVIDIA dcgm components.
The snap consists of [dcgm](https://developer.nvidia.com/dcgm) and [dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter).

## Build the snap

You can build the snap locally by using the command:

```shell
make build
```

## Install the snap

```shell
snap install --dangerous ./dcgm.snap
sudo systemctl enable snap.dcgm.dcgm-exporter.service --now # enable and start dcgm-exporter service
```
