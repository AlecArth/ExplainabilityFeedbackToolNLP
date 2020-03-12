from __future__ import print_function
import spacy
import sys
import os
import time
from filelock import FileLock

drugNLP = spacy.load('./Drugs')
eventNLP = spacy.load('./Events')

upload_path = "./Inputs/"
positives = "../positives.csv"
log_file = "../explained.csv"

def analyser(file_name):

	input_file = open(upload_path + file_name, 'r')
	sentences = input_file.readlines()

	for lineId in range(0, len(sentences)):
		sentence = str(sentences[lineId].rstrip())
		drug = ''
		event = ''
		print("\nChecking sentence: " + sentence)

		drugEnts = drugNLP(sentence)
		for ent in drugEnts.ents:
				# print(ent.text, ent.start_char, ent.end_char, ent.label_)
				drug = ent.text

		eventEnts = eventNLP(sentence)
		for ent in eventEnts.ents:
				# print(ent.text, ent.start_char, ent.end_char, ent.label_)
				event = ent.text


		if drug != '' and event != '':
			print("Sentence approved!")

			lock = FileLock(positives + ".lock")
			with lock:
				output = open(positives, 'a')
				output.write("POS|" + sentence + "|" + event + "|" + drug + "\n")
				output.close()

			lock = FileLock(log_file + ".lock")
			with lock:
				log_out = open(log_file, 'a')
				log_out.write(sentence + "\n")
				log_out.close()



print("\n--- Explainer ready ---")

while 1:

	# Wait for files from aligner.
	wait = 1
	while not os.listdir(upload_path):
		time.sleep(1)
		if wait == 1:
			print("\nwaiting for files")
			wait = 0

	# Get name of first file in folder.
	files = os.listdir(upload_path)
	file_name = files[0]
	if file_name == ".DS_Store":
		os.remove(upload_path + file_name)
		continue

	print("\nAnalyser working on " + file_name)

	# Run align tool on file and delete it.
	analyser(file_name)
	print("deleted " + file_name)

	# Delete first file in folder.
	os.remove(upload_path + file_name)
