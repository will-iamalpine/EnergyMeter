from decoding_serial import *
from serial import *
from bitstring import *
import os
import sys,argparse,binascii,struct,io
from datetime import datetime

ser = Serial(port='/dev/ttyAMA0',baudrate=38400,timeout=0.005) #IMPORTANT: TIMEOUT MUST BE < TIME_BETWEEN_READINGS
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

np.set_printoptions(precision=3,suppress=True) #fixes weird printout

sig_data = []

def report_train(hex,app,desc,sample_id,time):
	power_factor,phase,P_real,P_reac,P_app,Vrms,Irms = decode(hex)
	val = [app,desc, sample_id,time,round(power_factor,2),round(phase,2),round(P_real,2),round(P_reac,2),round(P_app,2),round(Vrms,2),round(Irms,2)]
	# print(val)
	return val

def split_at(s, c, n):
    words = s.split(c)
    return c.join(words[:n]), c.join(words[n:])

if __name__ == '__main__':
	flag = False
	print("Once appliance name is entered, sampling phase will begin. Please be ready to plug in appliance")
	app_name = raw_input("Please enter the name of the appliance. \nFORMAT: ApplianceName_Descriptor (copy/paste for each run)\nAppliance name: ",)
	#desc = raw_input("Please enter an ID descriptor of the appliance. Descriptor name: ")
	sample_id = raw_input("What batch is this? \nRun number: ")
	print("Plug in the device!")
	start = datetime.now()
	sample_period = 10 #seconds
	appliance = split_at(app_name,"_",1)[0]
	description = split_at(app_name,"_",1)[1]
	while (ser.is_open & ((datetime.now() - start).seconds <= sample_period)):
		try:
			#print(((datetime.now() - start).seconds),"of", sample_period,"complete")
			line = sio.readline()
			time = (datetime.now() - start).seconds
			if time >= 7 and flag == False:
				print('UNPLUG DEVICE NOW!\n'*10)
				flag = True
			if len(line) > 100:
				if line[1] == 'E': ser.write('1q')  # suppress bad packets
				if line[:2] == 'OK':
					now = int((datetime.now() - start).seconds) + round((datetime.now() - start).microseconds / 1e+6, 4)
					output = report_train(convert2bits(line[5:-6]), appliance,description, sample_id,now)
					sig_data.append(output)
					#print(now)
		except ReadError:
			print('PLEASE RETRY USING INITAL BATCH/RUN # \nReadError')
			sys.exit()  # exits without writing file
			# print('FIX ME: ReadError..reading off the end of the data. Tried to read 32 bits when only 16 available.')
			# print('maybe this can be fixed by splitting the packet into two and running report 2X?')
		except SerialException:
			print('SerialException...is someone else already connected?')
			sys.exit()  # exits without writing file
		except ValueError:
			print('PLEASE RETRY USING INITAL BATCH/RUN #,\nVALUE ERROR',line[5:-6]) #print raw packet
			sys.exit()  # exits without writing file
		except KeyboardInterrupt:
			ser.close()
			print('\nSAMPLE ABORTED, FILE NOT SAVED. PLEASE RETRY USING INITAL BATCH/RUN #\n')
			sys.exit() #exits without writing file

	file_name = str(appliance+'_'+description+'_'+sample_id+'.csv')
	with open(os.path.join("/home/pi/DEV/data/",file_name), 'w') as file:
		file.write(str('app_name, app_desc, sample_id, time, power_factor, phase_angle, power_real, power_reactive, power_apparent, vrms, irms\n'))
		if len(sig_data)>0:
			for row in sig_data:
				data_str = " ".join(str(x) + ',' for x in row)
				data_str = data_str[:-1] + '\n'
				file.write(data_str)
		else:
			print('\nFILE NOT WRITTEN DUE TO EMPTY STRING. PLEASE RETRY USING INITAL BATCH/RUN #\n')
			sys.exit()  # exits without writing file
	print("You've written data to ",file_name,'with',len(sig_data),'rows')
