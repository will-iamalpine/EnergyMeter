from decoding_serial import convert2bits,decode
from serial import *
from bitstring import *
import sys,argparse,binascii,struct,io
from datetime import datetime

ser = Serial(port='/dev/ttyAMA0',baudrate=38400,timeout=.1) #IMPORTANT: TIMEOUT MUST BE < TIME_BETWEEN_READINGS
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

np.set_printoptions(precision=3,suppress=True) #fixes weird printout

sig_data = []

def report_train(hex,app_name):
	power_factor,phase,P_real,P_reac,P_app,Vrms,Irms = decode(hex)
	# now = int(datetime.now().second) + round(datetime.now().microsecond/1e+6, 3)
	now = round((datetime.now().second + datetime.now().microsecond)/1e4, 2)
	val = [app_name,now,round(power_factor,2),round(phase,2),round(P_real,2),round(P_reac,2),round(P_app,2),round(Vrms,2),round(Irms,2)]
	# print(val)
	return val

if __name__ == '__main__':
	print('WE NEED TO FIX BATCHING ISSUE') #TODO FIX THIS

	app_name = raw_input("Please enter the name of the appliance. Once appliance name is entered, sampling phase will begin.  Please be ready to plug appliance in.  Appliance name: ")
	print("Plug in the device in 5 seconds")
	start = datetime.now()
	sample_period = 60 #seconds
	while (ser.is_open & ((datetime.now() - start).seconds <= sample_period)):
		try:
			print(((datetime.now() - start).seconds),"of", sample_period,"complete")
			line = sio.readline()
			if len(line) > 100:
				if line[1] == 'E': ser.write('1q')  # suppress bad packets
				if line[:2] == 'OK':
					output = report_train(convert2bits(line[5:-6]), app_name)
					sig_data.append(output)
		except ReadError:
			print('FIX ME: ReadError..reading off the end of the data. Tried to read 32 bits when only 16 available.')
			print('maybe this can be fixed by splitting the packet into two and running report 2X?')
		except ValueError:
			print('VALUE ERROR',line[5:-6]) #print raw packet
		except KeyboardInterrupt:
			ser.close()
			print('\nSAMPLE ABORTED, FILE NOT SAVED. PLEASE RETRY\n')
			sys.exit() #exits without writing file

	file_name = str(app_name+'.csv')
	with open(file_name, 'a+') as file:
	    file.write(str(sig_data))
	    print("You've written data to ",file_name)

