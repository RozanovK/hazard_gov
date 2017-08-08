from urllib2 import urlopen
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader


content = urlopen("https://www.hazard.mf.gov.pl/api/Register").read()
root = ET.fromstring(content)
values = []
namespace = root.tag.split("Rejestr", 1)[0]

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



	




		


