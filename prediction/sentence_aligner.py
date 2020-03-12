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
from filelock import FileLock

reload(sys)
sys.setdefaultencoding("utf-8")
score_threshold = float(0.7)
upload_path = "./Inputs/"

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
		print "\nrunning comparison on " + file_name

		input_file = open(upload_path + file_name, 'r')

		sentences1 = input_file.readlines()

		sentences2 = []
		sentences3 = []

		lock = FileLock("../DRUG-AE.csv.lock")
		with lock:
			with open('../DRUG-AE.csv') as file:
				reader = csv.reader(file, delimiter='|')
				for row in reader:
					sentences2.append(row[0])

		lock = FileLock("../ADE-NEG.csv.lock")
		with lock:
			with open('../ADE-NEG.csv') as file:
				reader = csv.reader(file, delimiter='|')
				for row in reader:
					sentences3.append(row[0])

		print '\n----- Comparison -----'

		# Comparing each sentence from input to DRUG-AE.csv and DRUG-NEG.csv.
		for lineId1 in range(0, len(sentences1)):

			sentence1 = sentences1[lineId1]

			# Check if explainability module has already produced a match
			lock = FileLock("../explained.csv.lock")
			with lock:
				explain_file = open("../explained.csv", 'r')
				explained_sentences = explain_file.readlines()
				explain_file.close()

			skip = 0

			for index, line in enumerate(explained_sentences):
				if line == sentence1:
					skip = 1
					break

			if skip == 1:
				print("Skipping sentence: " + sentence1)
				continue

			sentence1_tokenised = re.findall(r"[\w]+", sentence1)
			# Compare input sentence to all sentences in databases.
			POS_bestscore = 0.0
			NEG_bestscore = 0.0
			# POS
			for lineId2 in range(0, len(sentences2)):
				sentence2 = sentences2[lineId2]
				sentence2_tokenised = re.findall(r"[\w]+", sentence2)

				numerator = 0
				denominator = len(sentence1_tokenised) + len(sentence2_tokenised)

				commonWords = align(sentence1_tokenised, sentence2_tokenised)

				for sentenceId in range(0, len(commonWords)):
					numerator += len(commonWords[sentenceId])

				score = "{0:.3f}".format(float(numerator) / float(denominator))

				# If score is greater than threshold append to output.
				if float(score) > float(POS_bestscore):
					POS_bestscore = score
			# NEG
			for lineId3 in range(0, len(sentences3)):
				sentence3 = sentences3[lineId3]
				sentence3_tokenised = re.findall(r"[\w]+", sentence3)

				numerator = 0
				denominator = len(sentence1_tokenised) + len(sentence3_tokenised)

				commonWords = align(sentence1_tokenised, sentence3_tokenised)

				for sentenceId in range(0, len(commonWords)):
					numerator += len(commonWords[sentenceId])

				score = "{0:.3f}".format(float(numerator) / float(denominator))

				# If score is greater than threshold append to output.
				if float(score) > float(NEG_bestscore):
					NEG_bestscore = score

			# Select the best score and append to matching csv.
			if POS_bestscore < NEG_bestscore and NEG_bestscore > score_threshold:
				lock = FileLock("../output_sentences.csv.lock")
				with lock:
					output = open("../output_sentences.csv", 'a')
					output.write("NEG|" + sentence1)
					output.close()
				print("NEG: " + sentence1)
			elif POS_bestscore > NEG_bestscore and POS_bestscore > score_threshold:
				lock = FileLock("../output_sentences.csv.lock")
				with lock:
					output = open("../output_sentences.csv", 'a')
					output.write("POS|" + sentence1)
					output.close()
				print("POS: " + sentence1)

		print "deleted " + file_name

	  # Delete first file in folder.
		os.remove(upload_path + file_name)
