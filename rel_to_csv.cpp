// SEP-AI4 2019 - Callum Lindquist a1703273

#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main(int argc, char *argv[])
{

	string inputFile = ""; // Name of the input file
	string outputFile = ""; // Name of the output file
	string line; // Current line being read in
	
	// Check for input filename as an argument.
	if (argc > 1) inputFile = argv[1];

	// Ask for the input filename if no argument is given.
	while (inputFile.length() < 1) {
		cout << "File to convert: ";
		cin >> inputFile;
	}

	// If the extension hasn't been specified it will be added onto the filename.
	string extCheck = "";

	for (int i = inputFile.length()-4; i < inputFile.length(); i++) {
		extCheck += inputFile[i];
	}

	if (extCheck != ".rel") inputFile += ".rel";

	// Open streams for the input and output files.
	ifstream input(inputFile);

	for(int i = 0; i < inputFile.length() - 4; i++){
		outputFile += inputFile[i];
	}

	ofstream output(outputFile+".csv");

	// Write the header line to the new file.
	output << "Sentence|AE|Drug" << endl;

	string sentence, AE, drug;

	// For the DRUG-AE.rel:
	// 2nd col is the sentence, 3rd col is the AE, 6th col is the drug.

	if (input.is_open()) {
		while (getline (input,line)) {

			sentence = "";
			AE = "";
			drug = "";
			int i = 0; // The current character position.
			int col = 0; // The current column.

			// Skip first column.
			while (line[i] != '|') i++;
			i++;
			col++;

			// Add 2nd column to 'sentence' string.
			while (line[i] != '|') {
				sentence += line[i];
				i++;
			}
			i++;
			col++;

			// Add 3rd column to 'AE' string.
			while (line[i] != '|') {
				AE += line[i];
				i++;
			}
			i++;
			col++;

			// Skip to the 6th column.
			while (col < 5) {
				if (line[i] == '|') col++;
				i++;
			}

			// Add 6th column to 'drug' string.
			while (line[i] != '|') {
				drug += line[i];
				i++;
			}

			// Send the strings to the output stream.
			output << sentence << "|" << AE << "|" << drug << endl;

		}

		// Close the input and output streams.
		input.close();
		output.close();
	}

	else cout << "Error opening file!" << endl;

	return 0;
}