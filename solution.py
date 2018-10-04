import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import csv
from constants import *

class XMLParser:
	def __init__(self, url, required_fields, output_file, sort_key):
		self.url = url
		self.required_fields = required_fields
		self.output_file = output_file
		self.sort_key = sort_key
		self.rows = []

	def download_xml(self):
		response = requests.get(self.url)
		return response.content

	def build_tree(self):
		tree = ET.ElementTree(ET.fromstring(self.download_xml()))
		self.root = tree.getroot()

	def build_rows(self):
		for child in self.root:
			field_dict = self.get_field_dict(child)

			#Perform any row-wise modifications.  Shorten description field to 200 chars, filter rows outside of 2016, etc.
			field_dict = self.post_process_row(field_dict)
			if field_dict is not None:
				self.rows.append(field_dict)

	#This method must be modified if you want to use a different xml
	#Return None if the row has been filtered
	def post_process_row(self, field_dict):
		if "and" not in field_dict["Description"]:
			return None
		elif not field_dict["DateListed"].startswith("2016"):
			return None

		field_dict["Description"] = field_dict["Description"][:200]
		return field_dict

	#This method must be modified if the sort key is not a datetime
	def sort_rows(self):
		self.rows = sorted(self.rows, key=lambda x: datetime.strptime(x[self.sort_key], "%Y-%m-%d %H:%M:%S"))

	def write_csv(self):
		with open(self.output_file, "w+") as output:
			csv_writer = csv.DictWriter(output, self.required_fields)
			csv_writer.writeheader()
			csv_writer.writerows(self.rows)

	def get_field_dict(self, child):
		field_dict = {}
		for field in self.required_fields:
			#Future improvement would be to cache absolute paths to each field at the beginning of the program
			att = child.find(".//" + field)
			#Missing fields are represented by an empty string in the final output
			if att is None:
				field_dict[field] = ""
			#If it has subelements, like with Appliances or Rooms, join them with a comma
			elif len(att) > 0:
				field_dict[field] = ",".join([x.text for x in list(att)])
			#Otherwise just add the contents of the field
			else:
				field_dict[field] = att.text
		return field_dict

	def build_csv(self):
		self.build_tree()
		self.build_rows()
		self.sort_rows()
		self.write_csv()

if __name__ == "__main__":
	xml_parser = XMLParser(URL,FIELDS,OUTPUT_FILE,SORT_KEY)
	xml_parser.build_csv()
