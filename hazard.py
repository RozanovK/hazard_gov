from urllib2 import urlopen
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader
import configparser
from datetime import datetime
import os
import logging
import logging.handlers
from optparse import OptionParser


CONFIG_FILE= 'hazard.ini'
LOG_FILE='/home/rozanovk/hazard.log'

def create_menu():
	parser = OptionParser()
	parser.add_option("--config",
                  action="store", type="string", dest="config")
	parser.add_option("--force",
		action="store_true", dest="force", default=False)
	(options, args) = parser.parse_args()
	return options, args

def log(log_file=LOG_FILE):
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	handler = logging.FileHandler(log_file)
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	def log_syslog(logger):
		handler = logging.handlers.SysLogHandler(address = '/dev/log')
		logger.addHandler(handler)
		formatter = logging.Formatter('hazard_gov: [%(levelname)s] %(message)s')
		handler.setFormatter(formatter)

	log_syslog(logger)
	return logger	

def get_config(config_file=CONFIG_FILE):
	settings = configparser.ConfigParser()
	settings.read(config_file)
	api_time = settings.get('API', 'api_time')
	api_register = settings.get('API', 'api_register')
	output_file = settings.get('Paths', 'output_file')
	log_file = settings.get('Paths', 'log_file')
	zone_file = settings.get('Paths', 'zone_file')
	return api_time, api_register, output_file, log_file, zone_file

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
	time_register = datetime.strptime(root.text, '%Y-%m-%dT%H:%M:%S')
	return time_register

def get_f_time(output_file):	#get last modification of output file
	if os.path.isfile(output_file):
		last_modified_date = datetime.fromtimestamp(os.path.getmtime(output_file))
	else:
    		last_modified_date = datetime.fromtimestamp(0)
		logger.info("No output file found!")
	return last_modified_date

def check_time(api_time, output_file, zone_file, api_register, logger):
	r_t = get_r_time(api_time)
	f_t = get_f_time(output_file)
	if r_t > f_t:
		logger.info("Generating file...")
		generate_file(output_file, api_register,zone_file)
	else:
		logger.info("No updates found!")

def generate_file(output_file, api_register,zone_file, logger):
	values = get_data(api_register)
	env = Environment(loader=FileSystemLoader('templates'))
	template = env.get_template('template.html')
	output = template.render(values=values, zone_file=zone_file)

	with open(output_file, "wb") as f:
    		f.write(output)
	f.close()
	logger.info("File was succesfully generated!")

def set_config_file(config_file):
	try:
		api_time, api_register, output_file, log_file, zone_file = get_config(options.config)
		return api_time, api_register, output_file, log_file, zone_file
	except configparser.NoSectionError:
		logger = log()
		logger.info("No such file or unsupported file type!")
		exit()


if __name__ == "__main__":
	options, args = create_menu()

	if options.config:
		api_time, api_register, output_file, log_file, zone_file = set_config_file(options.config)
	else:
		api_time, api_register, output_file, log_file, zone_file = get_config()
	logger = log(log_file)
	

	if options.force:
		generate_file(output_file, api_register,zone_file, logger)
	else:
		check_time(api_time, output_file, zone_file, api_register, logger)



	




		


