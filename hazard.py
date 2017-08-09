from urllib2 import urlopen
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader
import configparser

CONFIG_FILE= 'hazard.ini'


def get_config(config_file=CONFIG_FILE):
	settings = configparser.ConfigParser()
	settings.read(config_file)
	api_time = settings.get('API', 'API_TIME')
	api_register = settings.get('API', 'API_REGISTER')
	last_modif = settings.get('Dates', 'Last_Modif')
	output_file = settings.get('Paths', 'Output_File')
	return api_time, api_register, last_modif, output_file


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


def generate_file(output_file, api_register):
	values = get_data(api_register)
	env = Environment(loader=FileSystemLoader('templates'))
	template = env.get_template('template.html')
	output = template.render(values=values)

	with open(output_file, "wb") as f:
    		f.write(output)
		f.close()



if __name__ == "__main__":

	api_time, api_register, last_modif, output_file = get_config()
	generate_file(output_file, api_register)



	




		


