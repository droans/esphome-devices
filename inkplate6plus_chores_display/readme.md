# Inkplate 6 Plus Chores Display
Chore tracking for two people, including the ability to select and check off the chore. Uses ESPHome, Home Assistant, and Grocy

<img style="float" src="/static/tasks.jpeg" alt="Example of Weather Display Screen Tab" width="39.4%"/> <img style="float" align="right" src="/static/tasks_selected.jpeg" alt="Example of Calendar Display Screen Tab" width="40%"/>

## Updates:
### Jan 3, 2024
* Initial Release
---

## Instructions:

### Notes:
This is not plug-and-play. It is likely that you will need to debug some things. It is presumed you know how to debug any issues or at least search for help.

All files were taken from my personal installation. You will need to adjust parts of each file so they work for you. If an issue is caused by a bug in my configurations or missing details, please raise an issue. If you are still running into issues, contact me on Discord or Reddit (@droans). 

---

###   Home Assistant

#####   You will need:
* An Instance of Grocy and the Grocy HACS integration (alternatives may work but you will need to figure it out on your own)

#####  Steps:

1. Install the Grocy Integration.
2. Copy the files in `hass-config/` to your HA packages directory.
3. Go through each file and make adjustments as necessary
4. Restart Home Assistant and validate the sensors are working. 

---
###   ESPHome

1. Create a subdirectory for your device files and copy the files under `esphome-config` into that directory.
2. Update the data in `secrets.yaml` and each substitution file under `substitutions`. You do not need to update all of the substitutions. Instead, focus primarily on entities (generally labeled as `XXXX_ENTITY`), attributes (`XXXX_ATTR`), display, network and ESPHome configuration, and directory paths. Where possible, the important items are separated from the unimportant items. 
3. Create a `display.yaml` file (or however you would like to name it) in the root configuration directory for your ESPHome instance. Add the lines below into the file:

```
packages:
  config: !include display/config.yaml #Points to the config file you added
```

3. Validate and install the configuration. 