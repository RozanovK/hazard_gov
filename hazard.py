from urllib2 import urlopen
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader
import re


content = urlopen("https://www.hazard.mf.gov.pl/api/Register").read()
root = ET.fromstring(content)
values = []

m = re.match('\{.*\}', root.tag)
namespace = m.group(0) if m else ''

for child in root.findall(namespace + "PozycjaRejestru"):
	lp = child.get("Lp")
	zone = child.find(namespace + "AdresDomeny").text
	date = child.find(namespace + "DataWpisu").text
	values.append([lp, date, zone])

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('template.html')
output = template.render(values=values)


with open("hazard", "wb") as f:
    f.write(output)



	




		


