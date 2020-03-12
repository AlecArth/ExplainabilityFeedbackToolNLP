# Python 2
# -*- coding: utf-8 -*

from aligner import *
import re
import sys
import unicodedata
import math
import os.path
import time
import csv
from cStringIO import StringIO
from fileinput import *
import shutil

reload(sys)
sys.setdefaultencoding("utf-8")
score_threshold = float(0.7)
upload_path = "../uploaded_files/"

# Remove white space and tokenise sentences (one sentence per line) and other junk.
def parse_txt_file():
	output = ""
	return output

print "\nrunning align server"
while 1:

	# Wait for files to be uploaded.
	wait = 1
	while not os.listdir(upload_path):
		time.sleep(1)
		if wait == 1:
			print "\nwaiting for files"
			wait = 0

	# Get name of first file in folder.
	files = os.listdir(upload_path)
	file_name = files[0]
	if file_name == ".DS_Store":
		os.remove(upload_path + file_name)
	else:
		print("\nsending file to aligner and explainability module: ") + file_name

		shutil.copy(upload_path + file_name, "../DAE-Analyser/Inputs/")
		shutil.copy(upload_path + file_name, "../aligner_files/")

		#test_align(file_name)
		print "deleted " + file_name

		# Delete first file in folder.
		os.remove(upload_path + file_name)
