# Configuring the entities in Home Assistant

The IHCClient connects to Home Assistant via the
[REST API](https://developers.home-assistant.io/docs/api/rest/)
to read and update the states of the IHC Controller input and output entities.

Some configuration must be done on Home Assistant side before that.

## Input entities

You must create the input entities that are defined in `modules.yaml` file as
[Input Boolean helpers](https://www.home-assistant.io/integrations/input_boolean/) in Home
Assistant.

You can do so via the UI by opening
[Settings > Devices & Services > Helpers](https://my.home-assistant.io/redirect/helpers),
clicking on "Create Helper" and choosing a "Toggle" type.

> [!IMPORTANT]
> Verify that the `Entity ID` matches the `entity` value in `modules.yaml` file.

Alternatively you can define the input entities in the Home Assistant
`input_booleans.yaml` configuration file.

A sample `input_booleans.yaml`:

```yaml
# IHC inputs:

pir_1:
  name: Staircase motion sensor

thermostat_1:
  name: Living room thermostat

ihc_2_12:
  name: IHC module 2 input 12

front_door:
  name: Front door magnetic contact

night:
  name: Outdoor light sensor
```

Using these Input Boolean helpers you can now define the
[Binary Sensors](https://www.home-assistant.io/integrations/binary_sensor)
which will be used to represent the state of the inputs in the UI.

A sample `binary_sensors.yaml`:

```yaml
- platform: template
  sensors:

# IHC motion sensors
# (if no movement is detected for 5 seconds, turn off the sensor):

    pir_1:
      value_template: '{{ is_state("input_boolean.pir_1", "on") }}'
      delay_off: 5

# IHC termostats:

    thermostat_1:
      value_template: '{{ is_state("input_boolean.thermostat_1", "on") }}'

# IHC input module 2, input 12:

    ihc_2_12:
      value_template: '{{ is_state("input_boolean.ihc_2_12", "on") }}'

# IHC magnetic contacts:
# (note - if the door is closed -> IHC state is "true" -> HASS state is "off")

    front_door:
      value_template: '{{ is_state("input_boolean.front_door", "off") }}'

# IHC light sensor:
# (using different icons for states)

    night:
      value_template: '{{ is_state("input_boolean.night", "on") }}'
      icon_template: >
        {% if is_state("input_boolean.night", "off") %}
          mdi:weather-sunny
        {% else %}
          mdi:weather-night
        {% endif %}
```

Optionally, if you want to fine-tune the friendly names, device classes and
icons of the input sensors, you can define them in `customize.yaml`.

A sample `customize.yaml`:

```yaml
# IHC sensors (inputs):

binary_sensor.pir_1:
  friendly_name: Motion on staircase during last 5 seconds
  device_class: motion

binary_sensor.thermostat_1:
  friendly_name: Living room thermostat
  icon: mdi:thermostat

binary_sensor.ihc_2_12:
  friendly_name: IHC 2-12
  icon: mdi:water-percent-alert

binary_sensor.front_door:
  friendly_name: Front door
  device_class: door

binary_sensor.night:
  friendly_name: Light sensor
  # device_class: light
```

## Output entities

To be able to switch the IHC Controller outputs, you must define the output
entities as [Command Line](https://www.home-assistant.io/integrations/command_line)
switches in the following Home Assistant configuration files:

- `switches.yaml`
- `customize.yaml` (optional)

The command line switch uses a simple `curl` POST request to connect to the
IHCServer web interface and set the selected controller output to a desired
state.

A sample `switches.yaml`:

```yaml
# IHC outputs:

- platform: command_line
  switches:
    garden:
      friendly_name: Garden lights
      command_on:  curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":4,"ioNumber":3,"state":true}'
      command_off: curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":4,"ioNumber":3,"state":false}'

    p6:
      friendly_name: Power outlet (P6)
      command_on:  curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":5,"ioNumber":6,"state":true}'
      command_off: curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":5,"ioNumber":6,"state":false}'

    bathroom_fan:
      friendly_name: Bathroom fan
      command_on:  curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":8,"ioNumber":1,"state":true}'
      command_off: curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":8,"ioNumber":1,"state":false}'

    ihc_15_2:
      friendly_name: Nuclear reactor mains
      command_on:  curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":15,"ioNumber":2,"state":true}'
      command_off: curl --silent 'http://192.168.1.111:8081/ihcrequest' --data-binary '{"type":"setOutput","moduleNumber":15,"ioNumber":2,"state":false}'
```

> [!WARNING]
> Make sure you use the correct values for IHCServer name and port!

A sample `customize.yaml`:

```yaml
# IHC outputs:

switch.garden:
  assumed_state: false
  icon: mdi:outdoor-lamp

switch.p6:
  assumed_state: false
  icon: mdi:power-socket-eu

switch.bathroom_fan:
  assumed_state: false
  icon: mdi:fan

switch.ihc_15_2:
  assumed_state: false
  icon: mdi:atom
```

## Initial states

When started, the IHCClient requests the states of all inputs and outputs
from the IHCServer. Then it starts listening to the state change events only.
If the Home Assistant is restarted at some point, it does not receive the
state information before a corresponding event is received.

Therefore it is recommended to set up a small automation that will restart the
`ihcclient` service whenever Home Assistant is started.

An example automation:

```yaml
- id: ihc_client_restart
  alias: IHC client restart
  initial_state: true
  trigger:
    platform: homeassistant
    event: start
  action:
    service: shell_command.restart_ihcclient
```

`configuration.yaml`:

```yaml
shell_command: !include shell_commands.yaml
```

`shell_commands.yaml`:

```yaml
restart_ihcclient: /home/homeassistant/.homeassistant/shell_commands/restart_ihcclient.sh
```

The shell script `restart_ihcclient.sh` itself:

```bash
#!/bin/bash

sudo /bin/systemctl restart ihcclient.service
```
