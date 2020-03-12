# Python 2
# -*- coding: utf-8 -*

import re
import sys
import unicodedata
import math
import os.path
import time
import csv
from nltk import tokenize
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from fileinput import *
import shutil

reload(sys)
sys.setdefaultencoding("utf-8")
score_threshold = float(0.7)
upload_path = "./uploaded_files/"

def pdf_to_txt(file_name):
	fp = open(upload_path + file_name, 'r')

	rsrcmgr = PDFResourceManager()
	retstr = StringIO()
	codec = 'utf-8'
	laparams = LAParams()
	device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	password = ""
	maxpages = 0
	caching = True
	pagenos=set()

	for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
		interpreter.process_page(page)

	text = retstr.getvalue()

	fp.close()
	device.close()
	retstr.close()

	# Remove trailing blank lines/spaces.
	text = text.strip()

	# Delete pdf and save as txt.
	os.remove(upload_path + file_name)
	print "\nConverted " + file_name + " to txt file and deleted the pdf."
	file_name = file_name[:-3] + "txt"
	output = open(upload_path + file_name, 'w')
	output.write(text + '\n')
	output.close()

# Remove white space and tokenise sentences (one sentence per line) and other junk.
def parse_txt_file(file_name):

	fp = open(upload_path + file_name, 'r')
	data = fp.read()
	process = tokenize.sent_tokenize(data)
	processed = []

	for i, item in enumerate(process):
		process[i] = process[i].rstrip() # Remove trailing newline
		process[i] = re.sub('\n|\r| +', ' ', process[i]) # Replace other newlines and multiple whitespaces with single space
		process[i] = re.sub(' +', ' ', process[i]) # Replace all double whitespace formed from replacing a space then a newline

		#print("process: " + process[i])

		# if sentence is short, very unlikely to contain a DAE
		if len(process[i]) < 25:
			continue

		space = 0.0
		nonalpha = 0.0

		for j in process[i]:
			if j.isspace():
				space+=1
			if not j.isalpha():
				nonalpha+=1

		percentNA = (nonalpha - space)/(len(process[i]) - space)

		# if percent of non-alpha characters is greater than 50%, setence is very unlikely to be a DAE
		if percentNA < 0.5:
			processed.append(process[i].encode("utf-8"))

	print(processed)

	fp.close()
	fp = open(upload_path + file_name, 'w')
	for i, item in enumerate(processed):
		fp.write(processed[i] + '\n')
	fp.close()
	return 0


print "\n--- Parser ready ---"
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
		# If file type is pdf, convert it.
		file_type = file_name[-3:len(file_name)]
		if(file_type == "pdf"):
			pdf_to_txt(file_name)
			file_name = file_name[:-3] + "txt"

		parse_txt_file(file_name)

		shutil.copy(upload_path + file_name, "./explainability/Inputs/")
		shutil.copy(upload_path + file_name, "./semantic_similarity/Inputs/")

		#test_align(file_name)
		print "deleted " + file_name

	  # Delete first file in folder.
		os.remove(upload_path + file_name)
