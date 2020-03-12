# Explainability feedback tool for Natural Language Processing

## How to run

Start the parser:
```
python parser.py
```

Navigate to /semantic_similarity and run:

```
python wmd.py
```

Navigate to /explainability and run:
```
python explainer.py
```

Navigate to /web and start the Flask server with:

```
python ui.py
```

The website can now be accessed at localhost:5000

## File Converters

The file converters are used to convert the .rel and .txt files to .csv delimited by vertical bars.

Compile instructions (Linux):

```
g++ -o txt_to_csv txt_to_csv.cpp
g++ -o rel_to_csv rel_to_csv.cpp
```

Run instructions (Linux):

```
./txt_to_csv ADE-NEG.txt
./rel_to_csv DRUG-AE.rel
```
