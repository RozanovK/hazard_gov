from urllib2 import urlopen
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader
import configparser
from datetime import datetime
import os

CONFIG_FILE= 'hazard.ini'
TIME_F = '%Y-%m-%dT%H:%M:%S'

def get_config(config_file=CONFIG_FILE):
	settings = configparser.ConfigParser()
	settings.read(config_file)
	api_time = settings.get('API', 'API_TIME')
	api_register = settings.get('API', 'API_REGISTER')
	output_file = settings.get('Paths', 'Output_File')
	return api_time, api_register, output_file


def get_data(api_register):
	content = urlopen(api_register).read()
	root = ET.fromstring(content)
	values = []
	namespace = root.tag.split("Rejestr", 1)[0]

	for child in root.findall(namespace + "PozycjaRejestru"):
		lp = child.get("Lp")
		zone = child.find(namespace + "AdresDomeny").text
		date = child.find(namespace + "DataWpisu").text
		values.append([lp, date, zone])
	return values

def get_r_time(api_time):    #get time of last register modification
	content = urlopen(api_time).read()
	root = ET.fromstring(content)
	time_register = datetime.strptime(root.text, TIME_F)
	return time_register

def get_f_time(output_file):	#get last modification of output file
	if os.path.isfile(output_file):
		last_modified_date = datetime.fromtimestamp(os.path.getmtime(output_file))
	else:
    		last_modified_date = datetime.fromtimestamp(0)
	return last_modified_date

def generate_file(output_file, api_register, config_file=CONFIG_FILE):
	values = get_data(api_register)
	env = Environment(loader=FileSystemLoader('templates'))
	template = env.get_template('template.html')
	output = template.render(values=values)

	with open(output_file, "wb") as f:
    		f.write(output)
	f.close()

	def modification_time(config_file):
		now = datetime.now().strftime(TIME_F)

		settings = configparser.ConfigParser()
		settings.read(config_file)
		settings.set('Dates', 'Last_Modif', now)

		with open(config_file, 'w') as f:
			settings.write(f)
		f.close()
	modification_time(config_file)
	

def check_time(api_time, output_file, api_register, config_file=CONFIG_FILE):
	r_t = get_r_time(api_time)
	f_t = get_f_time(output_file)
	if r_t > f_t:
		generate_file(output_file, api_register, config_file)
	else:
		print ("No updates found!")
		 


if __name__ == "__main__":

	api_time, api_register, output_file = get_config()
	check_time(api_time, output_file, api_register)



	




		


