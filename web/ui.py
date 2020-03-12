from flask import Flask, flash, request, redirect, render_template
import os
import csv
from werkzeug.utils import secure_filename
from filelock import FileLock

uploadFolder = '../uploaded_files'
sentenceFile = ''
positiveFile = '../DRUG-AE.csv'
negativeFile = '../ADE-NEG.csv'
extensions = set(['pdf', 'txt'])

sentenceType = -1
sentence = ''
activeSentence = 0

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = uploadFolder
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/", methods=['POST'])
def upload_file():
	if request.method == 'POST':
		files = request.files.getlist('files[]')

		# Check for allowable extension, then save to upload folder
		for file in files:
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
					flash('Failed (duplicate file name): ' + file.filename, "uploads")
				else:
					file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
					flash('Uploaded: ' + file.filename, "uploads")
			else:
				flash('Failed (incorrect file type): ' + file.filename, "uploads")

		return redirect("/")

@app.route("/feedback")
def feedback():
	global sentenceType
	global sentence
	global sentenceFile
	global activeSentence

	# Check output_sentences.csv
	lock = FileLock("../positives.csv.lock")
	with lock:
		with open("../positives.csv") as file:
			reader = csv.reader(file, delimiter='|')
			data = list(reader)
			rows = len(data)
			if rows == 0:
				print('No explained sentences to be read!')
				lock1 = FileLock("../output_sentences.csv.lock")
				with lock1:
					with open("../output_sentences.csv") as file1:
						reader = csv.reader(file1, delimiter='|')
						data = list(reader)
						rows = len(data)
						if rows == 0:
							print('No aligned sentences to be read!')
							flash("No sentences are currently pending review.", "POS")
							activeSentence = 0
							return redirect("/")
						else:
							sentence = data[0]
							sentenceFile = "../output_sentences.csv"
							activeSentence = 1
			else:
				sentence = data[0]
				sentenceFile = "../positives.csv"
				activeSentence = 1

	print(sentence)

	if sentence[0] == 'POS':
		flash("Identified as a Drug Adverse Event:", "POS")
		if sentenceFile == "../positives.csv":
			sentenceType = 1
			print("type set to 1")
		else:
			sentenceType = 2
	else:
		flash("Identified as a Non Drug Adverse Event:", "NEG")
		sentenceType = 0
		print("type set to 0")

	flash(sentence[1], "sentences")

	if sentenceType == 1:
		flash(sentence[3], "POS_drug")
		flash(sentence[2], "POS_event")
	elif sentenceType == 2:
		flash("?", "POS_drug")
		flash("? This sentence aligned with the DAE database.", "POS_event")
	else:
		flash("This sentence has aligned with the Non-DAE database.", "NEG_explain")

	return redirect("/")

@app.route("/NDAE")
def NDAE():
	global sentence
	global activeSentence

	if activeSentence == 1:

		duplicate = 0

		# Check for duplicate sentence
		ade_neg = open(negativeFile, "r")
		sentences = ade_neg.readlines()
		for index, line in enumerate(sentences):
			if sentence[1] == line:
				duplicate = 1
				break
		ade_neg.close()

		# Add sentence to ADE-NEG.csv
		if duplicate == 0:
			lock = FileLock(negativeFile + ".lock")
			with lock:
				ade_neg = open(negativeFile, "a")
				ade_neg.write(sentence[1] + "\n")
				ade_neg.close()

		# Remove current sentence from file
		discard()

	return redirect("/")

@app.route("/DAE")
def DAE():
	global sentenceType
	global sentence

	if activeSentence == 1:

		duplicate = 0

		# Check for duplicate sentence
		ade_pos = open(positiveFile, "r")
		sentences = ade_pos.readlines()
		for index, line in enumerate(sentences):
			if sentence[1] == line:
				duplicate = 1
				break
		ade_pos.close()

		# Add sentence to DRUG-AE.csv
		if duplicate == 0:
			lock = FileLock(positiveFile + ".lock")
			with lock:
				ade_pos = open(positiveFile, "a")
				if sentenceType == 1:
					ade_pos.write(sentence[1] + "|" +\
					 sentence[2] + "|" + sentence[3] + "\n")
				else:
					ade_pos.write(sentence[1] + "\n")

				ade_pos.close()

		# Remove sentence from sentenceFile
		discard()

	return redirect("/")

@app.route("/discard")
def discard():
	global sentenceFile
	global activeSentence

	if activeSentence == 1:

		# Remove sentence from sentenceFile
		lock = FileLock(sentenceFile + ".lock")
		with lock:
			file = open(sentenceFile, "r")
			sentence = file.readline()
			sentences = file.readlines()
			file.close()
			file = open(sentenceFile, "w")
			for index, line in enumerate(sentences):
				file.write(line)
			file.close()

		# Show user the next sentence
		feedback()

	return redirect("/")

@app.route("/userGuide/")
def userGuide():
	return render_template("userGuide.html")

@app.route("/controlPanel/")
def controlPanel():
	return render_template("controlPanel.html")

if __name__ == "__main__":
	app.run(debug=True,host='127.0.0.1',port="5000")
