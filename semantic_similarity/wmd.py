import os
import re
import time
from string import punctuation

import gensim.downloader as api
from gensim.models import KeyedVectors
from nltk.corpus import stopwords
from nltk import download
from nltk import word_tokenize
from filelock import FileLock
import csv

# import pyemd

upload_path = "./Inputs/"
score_threshold = 0.5

# Takes a model name as input.
#	If the model has already been normalised and compiled in the .model format, load the model.
#	Else if the model exists but has not been normalised and compiled as a model, compile it
#	Else check if the model can be found online and if so download it, otherwise exit
# Once the model has been loaded in the correct format, return it.
def get_model(model_name):
	pre_file = model_name
	#final_file = os.path.splitext(model_name)[1] + ".model"
	final_file = model_name + ".model"

	if os.path.exists(final_file):
		print(model_name + " Loaded Successfully")
		return KeyedVectors.load(final_file, mmap='r')
	elif os.path.exists(pre_file):
		if pre_file[-3:] == "bin":
			pre_model = KeyedVectors.load_word2vec_format(pre_file, binary = True, limit = 500000)
		else:
			pre_model = KeyedVectors.load_word2vec_format(pre_file, binary = False, limit = 500000)
  	else:
		try:
			print("Checking Gensim API for Model...")
			pre_model = api.load(model_name)
		except Exception as e:
			print("Specified Model Unavaliable from Gensim API and not found locally")
			exit(-1)

	print("Building Model...")
	pre_model.init_sims(replace=True)
	pre_model.save(final_file)
	print(model_name + " Loaded Successfully")
	return KeyedVectors.load(final_file, mmap='r')


def multiple_replace(string, rep_dict):
    pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)

# Improve performance of sentence matching by removing stop-words
def preprocess_sent(sentence):
	stop_words = set(stopwords.words('english'))
	sentence = multiple_replace(sentence, {'/':' / ', '.-':' .- ', '.':' . ', '\'':' \' '})
	sentence = sentence.lower()
	#try:
	tokens = [token for token in word_tokenize(sentence) if token not in punctuation and token not in stop_words]
	#except Exception as e:
		#print("An error has occured. Please ensure NLTK + NLTK_data are installed")
	return tokens

# Compare sentences using the model provided earlier, using the Word Mover Distance algorithm
# Returns a distance value. The smaller the distance, the greater the similarity.
def compare_sent(sentence1, sentence2, model):
	return model.wmdistance(preprocess_sent(sentence1), preprocess_sent(sentence2))

# Import and download stopwords from NLTK (if they dont already exist).
download('stopwords')
model = get_model("glove-wiki-gigaword-50") # can change this, loaded model is a small download and seems accurate enough

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
			# print(sentences1[lineId1])
			# sentence1 = unicode(sentences1[lineId1].rstrip())
			sentence1 = sentences1[lineId1].decode('utf-8').strip()

			# Check if explainability module has already produced a match
			lock = FileLock("../explained.csv.lock")
			with lock:
				explain_file = open("../explained.csv", 'r')
				explained_sentences = explain_file.readlines()
				explain_file.close()

			skip = 0

			for index, line in enumerate(explained_sentences):
				line = line.decode('utf-8').strip()
				if line == sentence1:
					skip = 1
					break

			if skip == 1:
				print("Skipping sentence: " + sentence1)
				continue

			POS_bestscore = 1.0
			NEG_bestscore = 1.0
			print("\n" + sentence1)
			print("--- Checking Positives ---")
			for lineId2 in range(0, len(sentences2)):
				# if lineId2 % 100 == 0: print(lineId2)
				sentence2 = sentences2[lineId2]

				score = unicode(compare_sent(sentence1, sentence2, model))

				if float(score) < float(POS_bestscore):
					POS_bestscore = score
			print("--- Checking Negatives ---")
			for lineId3 in range(0, len(sentences3)):
				# if lineId3 % 100 == 0: print(lineId3)
				sentence3 = sentences3[lineId3]

				score = unicode(compare_sent(sentence1, sentence3, model))

				if float(score) < float(NEG_bestscore):
					NEG_bestscore = score

			print("POS: " + str(POS_bestscore) + " NEG: " + str(NEG_bestscore))

			# Select the best score and append to matching csv.
			if float(POS_bestscore) > float(NEG_bestscore) and float(NEG_bestscore) < float(score_threshold):
				lock = FileLock("../output_sentences.csv.lock")
				with lock:
					output = open("../output_sentences.csv", 'a')
					output.write("NEG|" + sentence1 + "\n")
					output.close()
				print("NEG: " + sentence1)
			elif float(POS_bestscore) < float(NEG_bestscore) and float(POS_bestscore) < float(score_threshold):
				lock = FileLock("../output_sentences.csv.lock")
				with lock:
					output = open("../output_sentences.csv", 'a')
					output.write("POS|" + sentence1 + "\n")
					output.close()
				print("POS: " + sentence1)

		print "deleted " + file_name

	  # Delete first file in folder.
		os.remove(upload_path + file_name)
