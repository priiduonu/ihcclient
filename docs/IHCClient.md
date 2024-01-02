# Installing the IHCClient

Clone the `ihcclient` repo:

```bash
cd /opt
git clone https://github.com/priiduonu/ihcclient.git
cd ihcclient
```

Make sure you have the following PIP packages installed:

- PyYAML
- requests
- urllib3
- websocket-client

Install them as needed with:

```bash
pip install
```

Using the provided sample files, create your own configuration files in the
installation directory and name them as `settings.yaml` and `modules.yaml`.

## Main settings

Configure the IHCServer and Home Assistant addresses (or names) and port
numbers in the `settings.yaml`. You also must set the Home
Assistant "Long-Lived Access Token" in this file.

You can obtain a token ("Long-Lived Access Token") by logging into the Home
Assistant frontend using a web browser, and going to your profile
http://<hass>:8123/profile and click the "Create Token" button.

## Inputs and outputs

Define the inputs and outputs of the IHC Controller that you need in the
`modules.yaml`.

> [!TIP]
> You can skip the inputs and outputs that you are not interested in.

Add a list of the inputs and outputs:

```yaml
- type: inputState
  moduleNumber: 1
  ioNumber: 4
  entity: input_boolean.pir_1
```

which contain the following keys:

- `type`: `inputState` or `outputState`
- `moduleNumber`: the IHC module number
- `ioNumber`: the IHC module input or output number
- `entity`: `input_boolean.xxx` for inputs or `switch.xxx` for outputs

> [!WARNING]
> Note that the IHC input module has inputs numbered from 1..8 and 11..18, but
  IHCServer maps them to ioNumber 1..16

## Enabling the `ihcclient` service

You can set the IHCClient to start automatically on system boot.

Create a `systemd` unit file `/etc/systemd/system/ihcclient.service` with the
following content (or just copy the unit file from the installation directory):

```output
[Unit]
Description=IHC client daemon

[Service]
Type=simple
ExecStart=/opt/ihcclient/ihcclient.py
WorkingDirectory=/opt/ihcclient/
Restart=always
RestartSec=2

[Install]
WantedBy=sysinit.target
```

To enable the automatic start:

```bash
systemctl daemon-reload
systemctl enable ihcclient
systemctl start ihcclient
```

To check the service status:

```bash
systemctl status ihcclient
```
