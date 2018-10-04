import unittest
from solution import XMLParser
from constants import *

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.xml_parser = XMLParser(URL,FIELDS,OUTPUT_FILE,SORT_KEY)
        self.xml_parser.build_tree()

    #Compare automatically downloaded xml to manual download
    def test_download(self):
        with open('test_xml.xml', 'r') as f:
            contents = f.read()
            self.assertEqual(contents, self.xml_parser.download_xml())

    #Test that descriptions without "and" get filtered
    def test_post_process_and_filter(self):
        row = {"DateListed": "2016-03-03 00:00:00", "Description": "This description does not contain a required keyword"}
        self.assertEqual(self.xml_parser.post_process_row(row), None)

    #Test that listings outside of 2016 get filtered
    def test_post_process_year_filter(self):
        row = {"DateListed": "2015-03-03 00:00:00", "Description": "This description contains the required keyword \"and\", but was not listed in 2016"}
        self.assertEqual(self.xml_parser.post_process_row(row), None)

    #Test that long descriptions are truncated.
    def test_post_process_year_filter(self):
        long_description = "and" * 250
        row = {"DateListed": "2016-03-03 00:00:00", "Description": long_description}
        self.assertEqual(len(self.xml_parser.post_process_row(row)["Description"]), 200)

    #Test that entries are converted to expected dictionaries
    def test_field_dict(self):
        expected_dict = {'MlsName': 'CLAW', 'Bathrooms': None, 'Description': 'Enjoy amazing ocean and island views from this 10+ acre parcel situated in a convenient and peaceful area of the Santa Monica mountains. Just minutes from beaches or the 101, Castro Peak is located off of Latigo canyon in an area sprinkled with vineyards, ranches and horse properties. A paved road leads you to the site which features considerable useable land and multiple development areas. This is an area of new development. Build your dream.', 'Price': '535000.00', 'Bedrooms': '0', 'StreetAddress': '0 Castro Peak Mountainway', 'DateListed': '2014-10-03 00:00:00', 'Appliances': None, 'MlsId': '14799273', 'Rooms': ''}
        self.assertNotEqual(len(self.xml_parser.root), 0)
        self.assertEqual(self.xml_parser.get_field_dict(self.xml_parser.root[0]), expected_dict)

    #Test that the output is sorted
    def test_rows_sorted(self):
        self.xml_parser.build_rows()
        self.xml_parser.sort_rows()
        rows = self.xml_parser.rows
        sort_key = self.xml_parser.sort_key
        self.assertTrue(all(rows[i][sort_key] <= rows[i+1][sort_key] for i in xrange(len(rows)-1)))

if __name__ == '__main__':
    unittest.main()