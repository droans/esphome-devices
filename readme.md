# Waveshare Display Configuration
----
For use with the Waveshare 7.5inch e-Paper B V2 display.

To use:


## Home Assistant
___
##### You will need:
* Device trackers showing the location for two people
* ICS Calendar Sensor custom component
* Commute sensors for two people from current location to home and to work (preferably Waze)
* A local weather source providing:
  * Current temperature as a state
  * A current weather entity providing current conditions as the state with temperature and forecast for the attributes
  * An hourly weather entity providing compatible attributes:
    * `forecast`, organized by hour, displaying `temperature`, `condition`, and `datetime`

##### Steps:

1. Install the ICS Calendar Sensor custom component. This is available through HACS or you can search for installation instructions.
2. Retrieve the ICS link for you calendar. Set up the ICS Calendar Sensor with that link.
3. Copy `hass-config/display.yaml` to your HA packages directory.
4. Use the instructions at the top of `display.yaml` to replace the entity IDs with the proper IDs for your installation.
5. Restart Home Assistant and validate the sensors are working. 

# AppDaemon
---
AppDaemon is used as the ICS sensors reports all events starting at 12:00 AM today, leading often to the sensors showing events which already occurred. The code used will cycle through the sensors and discard the data from any which are stale. It will create new sensors using the `updated_sensors` data. 

You can use your own abilities to replicate these elsewhere if you choose.

##### Steps:
1. Copy the files for `appdaemon-config` to their respective AppDaemon configuration directories.
2. Adjust `events.yaml` to match your needs.
3. Validate the sensors are created and are reporting properly.

# ESPHome
---
1. Create a subdirectory for your device files and copy the files under `esphome-config` into that directory.
2. Update the data in `secrets.yaml` and each substitution file under `substitutions`. You do not need to update all of the substitutions. Instead, focus primarily on entities (generally labeled as `XXXX_ENTITY`), attributes (`XXXX_ATTR`), display, network and ESPHome configuration, and directory paths. Where possible, the important items are separated from the unimportant items. 
3. Validate and install the configuration. 