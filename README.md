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

## Configuration

The snap supports a `default-configure` hook which runs once during the installation of the snap to allow automated startup of `dcgm-exporter` service. This is particularly useful when deployed with a custom gadget snap , as it helps override the default service status of the exporter (which is disabled at installation).

### Autostart via Gadget Snap

If the `exporter.autostart` configuration is set to `true` by a gadget snap, the `dcgm-exporter` service will be enabled and started automatically upon installation.

#### Gadget Snap Configuration Example:

In your gadget snap's `defaults` section:

```YAML
defaults:
  #dcgm snap ID
  e2YXZYWeF3P3divT2g7G5mxaqAmPVZxj:
    exporter:
      autostart: true
```

## Test

You can test the snap locally by using the command:

```shell
tox -e func
```

User documentation can be found on the [snap page](https://snapcraft.io/dcgm).
