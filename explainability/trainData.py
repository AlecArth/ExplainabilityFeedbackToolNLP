from __future__ import print_function
import spacy
import random


TRAIN_DATA = [
#ENTER TRAINING DATA GENERATED HERE
]


def train_spacy(data,iterations):
    TRAIN_DATA = data
    nlp = spacy.blank('en')
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)
    else:
        ner = nlp.get_pipe("ner")
       
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes)  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(iterations):
            print("Statring iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                nlp.update([text], [annotations], drop=0.2, sgd=optimizer, losses=losses)
            print(losses)
    return nlp


prdnlp = train_spacy(TRAIN_DATA, 20)

# Save our trained Model
modelfile = raw_input("Enter your Model Name: ")
prdnlp.to_disk(modelfile)
