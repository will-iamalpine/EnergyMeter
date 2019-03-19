### Build experimental setup
### Calibrate device per [these instructions](https://learn.openenergymonitor.org/electricity-monitoring/ctac/calibration)
### Clone SD card to 32gb
### Do magic with SD card to install tf
### Import necessary modules (numpy pi version etc)
### Compile & upload firmware per [these instructions](https://github.com/quicksell-louis/EnergyMeter/blob/master/firmware/instructions.md) 
### Collect training data
Copy from training folder to the file location you'll be running CoLab from 
scp -r pi@(your pi's IP):/home/pi/DEV/data_train/ /Users/name/Desktop/
### Run colab notebook to extract training info
### Update decode_serial with new appliance dictionary
### Run decode_serial
