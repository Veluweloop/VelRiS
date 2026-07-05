# for RFID reader
import usb.core
import usb.util
import datetime
import threading
import config

class RFID(threading.Thread):
	buffer = [] #create empty buffer on initialising class 

	def __init__(self):
		threading.Thread.__init__(self)
		self.VendorID = 6790 #vendorID
		self.ProductID = 57360 #productID
		self.device = usb.core.find(idVendor = self.VendorID, idProduct=self.ProductID) #link to USB based on productID and vendorID

	def run(self):
		if self.device is not None: #when RFID reader is found
			print("RFID device found") #print RFID reader is found
			config_all = config.config_read()
			config_all['system']['RFID_reader'] = "TRUE"
			config.config_write(config_all)

			self.interface = 0
			self.endpoint = self.device[0][(0,0)][0]

			if self.device.is_kernel_driver_active(self.interface) is True: #claim USB device by this script even when something else had claimed USB device
				self.device.detach_kernel_driver(self.interface)
				usb.util.claim_interface(self.device, self.interface)
    
			while True: #endless loop for reading data from RFID reader
				try: #failsave for errors
					self.data = self.device.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize).tolist() #save data to variable and transform array into list

					if " ".join(map(str, self.data[0:2])) == "31 67": #get the data and split the data on their meaning
						self.readerID = " ".join(map(str, self.data[17:18]))
						self.antennaID = " ".join(map(str, self.data[18:19])) 
						self.result = " ".join(map(str, self.data[19:31])) #RFID chip ID
						self.rss = " ".join(map(str, self.data[31:32])) #Received Signal Strength

						self.datetime_current = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat() #current system datetime

						self.buffer_temp = (self.datetime_current, self.result, self.rss) #combine al data into a single variable
						RFID.buffer.append(self.buffer_temp) #append received data to buffer in memory

				except usb.core.USBError as e: #when errors occurs 
					self.data = None
					if e.args == ('Operation timed out', ):
						continue

		else: #in casae no RFID device is found
			print("No RFID device found")
			config_all = config.config_read()
			config_all['system']['RFID_reader'] = "FALSE"
			config.config_write(config_all)
