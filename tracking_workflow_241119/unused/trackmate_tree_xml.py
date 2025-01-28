#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 23:04:44 2024

@author: u2260235
"""

import numpy as np
#from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

#data_dir = "//Users/u2260235/Documents/Y3 Project/Stracking_workflow_241119/"
raw_data_path = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/240408_240411_WT_150nM_pos33_masks.xml"

"""
# loads XML
with open(raw_data_path, 'r') as f:
    raw_data = f.read()
# parses xml
data = BeautifulSoup(raw_data, "xml")
"""

# parses xml file
tree = ET.parse(raw_data_path)
# gets root element of xml
root = tree.getroot()

root.tag
