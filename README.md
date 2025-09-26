# dcgm-snap

This is a snap delivering NVIDIA dcgm components.
The snap consists of [dcgm](https://developer.nvidia.com/dcgm) and [dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter).

## Build the snap

From v4, the `snapcraft.yaml` file is dynamically generated using the `snapcraft.yaml.in` file
as template. To create the file run:

```shell
# generate v4 using cuda11 packages
CUDA_VERSION=11 envsubst '$CUDA_VERSION'  < snap/snapcraft.yaml.in > snap/snapcraft.yaml

# generate v4 using cuda12 packages
CUDA_VERSION=12 envsubst '$CUDA_VERSION'  < snap/snapcraft.yaml.in > snap/snapcraft.yaml

# generate v4 using cuda13 packages
CUDA_VERSION=13 envsubst '$CUDA_VERSION'  < snap/snapcraft.yaml.in > snap/snapcraft.yaml
```

You can build the snap locally by using the command:

```shell
snapcraft pack -v
```

## Test

You can test the snap locally by using the command:

```shell
tox -e func
```

User documentation can be found on the [snap page](https://snapcraft.io/dcgm).
