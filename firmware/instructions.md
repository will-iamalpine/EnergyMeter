# Firmware Instructions

## Make A Copy Of Your SD Card
Never a bad idea...

## Disable Bluetooth To Allow Serial Interface
Follow [these instructions](https://scribles.net/disabling-bluetooth-on-raspberry-pi/#02)

## Swap Firmware Files
Find & replace files in /emonpi/firmware/ with the files in the firmware folder of this repo

## Upload modified firmware using [PlatformIO](https://docs.platformio.org/en/latest/userguide/cmd_run.html)
Install PlatformIO on your pi. 

`sudo pip install -U platformio`

Navigate to the folder /emonpi/firmware/, enter the following commands: 

`sudo pio init`

`sudo pio run` #compiles

`sudo pio run -t upload` #uploads

You should see the following after compiling and uploading:

![image](https://user-images.githubusercontent.com/8934290/54469486-d7cf7380-4755-11e9-91e9-2bc8a0cce5cd.png)
![image](https://user-images.githubusercontent.com/8934290/54469543-896ea480-4756-11e9-9186-f154ee11eaa2.png)


## Verify Serial Interface
In terminal, you will see this streaming JeeLibs packet info after typing teh following:

`minicom -b38400 -D/dev/ttyAMA0`
![image](https://user-images.githubusercontent.com/8934290/54469604-58db3a80-4757-11e9-806b-9ba033cef38a.png)
