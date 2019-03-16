# Firmware Instructions

## Disable Bluetooth To Allow Serial Interface
Follow [these instructions](https://scribles.net/disabling-bluetooth-on-raspberry-pi/#02)

## Upload modified firmware using [PlatformIO](https://docs.platformio.org/en/latest/userguide/cmd_run.html)
In terminal, navigate to the src firmware folder on your pi (/emonpi/firmware/src), and replace the existing files on your pi with the ones in this folder.

Now enter the following commands: 
'sudo pio init'
'sudo pio run' #compiles
'sudo pio run -t upload -v' #uploads
You should see a success message after compile 

## View Raw Values Via Serial Interface To Verify Uploads
In terminal, type
'minicom -b38400 -D/dev/ttyAMA0'
