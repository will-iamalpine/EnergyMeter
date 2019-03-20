### Buy Supplies
You will need:
* [EmonPi](https://openenergymonitor.com/emonpi-3/), CT & Voltage (from emonpi store) ($350 USD-ish)
* 32gb SD card ($10 USD)
* Power strip ($10 USD)
### Build Experimental Setup
* Strip insulation and clip to black or white wire. If you clip to white, you'd need to invert your current readings in the firmware.

![image](https://user-images.githubusercontent.com/8934290/54722330-86423280-4b21-11e9-843a-1506b9358652.png)

### Calibrate EmonPi 
* Per [these instructions](https://learn.openenergymonitor.org/electricity-monitoring/ctac/calibration)
### Clone SD card to 32gb
#TODO
### Install Required Packages
* Tensorflow #TODO
* Numpy 
`sudo apt install --no-install-recommends python2.7-minimal python2.7` 
or 
`#sudo apt install python-numpy python-scipy`
* Scikit-learn #TODO

### Compile & Upload Firmware 
* Per [these instructions](https://github.com/quicksell-louis/EnergyMeter/blob/master/firmware/instructions.md) 

### Create Necessary Folders
* `mkdir /home/pi/DEV/` (where scripts will reside)
* `mkdir /home/pi/DEV/data_train` (where training dataset will reside)

### Train Data Collection
* Run train.py and collect your desired number of samples of each appliance. We did 100 of each, for 700 samples.
Note that as you cycle appliances constantly, their properties will change as they warm up. 
Might be smart to let it cool after each run, but that would take a ton of time.
* Run 'train.py --empty' to collect another 100 empty windows for baseline comparison. This helps the accuracy of the model
* Copy from training folder on your pi to your favorite Google Drive local location you'll be running CoLab:

`scp -r pi@(your pi's IP):/home/pi/DEV/data_train/ /Users/name/YourFavoriteGoogleDriveLocation/`
* Convert to .zip file and grab the GD sharing url that follows the 'id=....' e.g. "1ShWZ4olv0SdT6jpRbVgF2C7q0tZZVKYc"
  Be sure to put this as "zip_id" variable under the 'LINK DATA TO INSTANCE' title block in the colab training file

### Neural Network Model Creation/Upload
* Open Google Colaboratory and run the jupyter notebook "model_creation.ipynb"
* Find your file in your Google Drive and download locally. Navigate to that folder
* Upload the .h5 file (the model) to your pi's main DEV folder, e.g.:

`scp wb_model_1.h5 pi@(your pi's IP):/home/pi/DEV/`

### Test Model Functionality Locally
* [Here's a script](https://github.com/quicksell-louis/EnergyMeter/blob/master/scripts/test_classify.py) to allow local test before uploading to the pi, which saves a bit of hassle


### Upload Classifier Encoding To Pi
* In "model_creation.ipynb", copy the dictionary printout from line `print("appliance_dict = ",encoding)`
* Paste it into your main script: 

`appliance_dict = {0: 'cell', 1: 'desklamp', 2: 'fan', 3: 'kettle', 4: 'laptop', 5: 'monitor', 6: 'none', 7: 'sadlamp'} #N.B. update this with each model!`

### Classify!
* The script will print out the result of the classification and the confidence. 
* See future work for inspiration to expand the capabilities, as there is no shortage of work to be done
* Please contribute!

![image](https://user-images.githubusercontent.com/8934290/54723395-ab847000-4b24-11e9-972c-41f37fc29c30.png)
![image](https://user-images.githubusercontent.com/8934290/54723425-be974000-4b24-11e9-9a49-8d0b971353e8.png)
![image](https://user-images.githubusercontent.com/8934290/54723448-d53d9700-4b24-11e9-9cc0-7cc9c2840edd.png)
![image](https://user-images.githubusercontent.com/8934290/54723488-f56d5600-4b24-11e9-94cf-ceb84dfbced2.png)
![image](https://user-images.githubusercontent.com/8934290/54723532-19309c00-4b25-11e9-8dd8-79155f74c0c1.png)
![image](https://user-images.githubusercontent.com/8934290/54723581-3bc2b500-4b25-11e9-82bb-cd1f05078126.png)
![image](https://user-images.githubusercontent.com/8934290/54723618-5bf27400-4b25-11e9-8adc-63e49a7a231c.png)
