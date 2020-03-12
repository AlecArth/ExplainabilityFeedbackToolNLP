from __future__ import print_function
from spacy.lang.en import English

import spacy
import csv
import sys

parser = English()
nlp = spacy.load('en_core_web_sm') #call "python -m spacy download en_core_web_sm" in shell if you lack this model
nlp.entity.add_label('EVENT') #can be 'DRUG'

with open('./DRUG-AE.csv', mode='r') as lex:
    reader = csv.reader(lex, delimiter='|')
    next(reader)
    sentList = []
    i = 0
    for rows in reader:
        startSub = rows[0].find(rows[1])
        endSub = startSub + len(rows[1])
        print('("""' + rows[0] + '""", {"""entities""": [(' + str(startSub) + ', ' + str(endSub) + ', """EVENT""")]}),', file=open("output.txt", "a"))