# IHCServer

A brief guide on installing and configuring the IHCServer.

## Installing the IHCServer

Clone the IHCServer repo:

```bash
mkdir /opt
cd /opt
git clone https://github.com/skumlos/ihcserver.git
```

The `utils` subdirectory is a separate repo, you have to clone it as well:

```bash
cd ihcserver
git clone https://github.com/skumlos/utils.git
```

> [!WARNING]
> I had to revert a certain commit in the original `utils` repository as it
  seemed to have a negative impact on the performance of the server.

```bash
cd utils
git revert 4275df8ab99ec077d238d7e4ee40f399126483e5
```

> [!NOTE]
> Make sure you have the `libssl-dev` library installed:
> ```bash
> apt-get install libssl-dev
> ```

When you have cloned both repos and optionally reverted the commit I referred
to, proceed to compile the code:

```bash
cd /opt/ihcserver
make
```

> [!NOTE]
> The source is quite old - to compile the code with modern compilers you may
  have to add the following option to `Makefile` and `utils/Makefile`:
> ```
> CXXFLAGS=-std=c++14
> ```

If the compilation is successful, there should now be the IHCServer
application `/opt/ihcserver/ihcserver`.

Start it now:

```bash
/opt/ihcserver/ihcserver
```

If you start it for the first time, it creates a sample configuration file
`/etc/ihcserver.cfg` and exits.

Configure the following parameters in `/etc/ihcserver.cfg`:

```output
"serialDevice" : "/dev/ttyUSB.IHC"
"webroot" : "/opt/ihcserver-webinterface"
```

and in the end of the file:

```output
		{
			"key" : "HTTP_PORT",
			"value" : "8081"
		},
```

Now proceed to install the web interface for the IHCServer.

## Installing the web interface for the IHCServer

Clone the IHCServer web interface repo:

```bash
cd /opt
git clone https://github.com/skumlos/ihcserver-webinterface.git
```

Start the IHCServer manually once again.

You can now open the IHCServer web interface at `http://<host>:8081`

Click the "Login" button at the upper right corner of the webpage and enter
the default PIN code for "ADMIN" user (`12345678`). Now click
the "Configuration" button and enable the I/O modules that you have connected
to the IHC controller.

All settings will be saved in the same configuration file (`/etc/ihcserver.cfg`).

## Enabling the IHCServer service

You probably want to set the IHCServer to start automatically as a daemon on
system boot.

Create a `systemd` unit file `/etc/systemd/system/ihcserver.service` with the
following content (or just copy the unit file from the installation directory):

```output
[Unit]
Description=IHC server daemon

[Service]
Type=simple
ExecStart=/opt/ihcserver/ihcserver -d
StandardOutput=null
Restart=always
RestartSec=2

[Install]
WantedBy=sysinit.target
```

To enable the automatic start:

```bash
systemctl daemon-reload
systemctl enable ihcserver
systemctl start ihcserver
```

To check the service status:

```bash
systemctl status ihcserver
```

## Debugging

For debugging the WebSocket connection you can use for example the
[WebSocket cat utility](https://www.npmjs.com/package/wscat).

Install it with:

```bash
npm install -g wscat
```

Establish the connection to your IHCServer:

```bash
wscat -c http://192.168.1.111:8081/ihcevents-ws
```

You should now see the events flowing in:

```json
< {
	"type" : "outputState",
	"moduleNumber" : 4,
	"ioNumber" : 4,
	"state" : false,
	"lastEventNumber" : 1097028703
}
< {
	"type" : "outputState",
	"moduleNumber" : 4,
	"ioNumber" : 6,
	"state" : false,
	"lastEventNumber" : 1104180253
}
< {
	"type" : "outputState",
	"moduleNumber" : 4,
	"ioNumber" : 8,
	"state" : true,
	"lastEventNumber" : 1104180253
}
```
