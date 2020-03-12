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

	if (extCheck != ".txt") inputFile += ".txt";

	// Open streams for the input and output files.
	ifstream input(inputFile);

	for(int i = 0; i < inputFile.length() - 4; i++){
		outputFile += inputFile[i];
	}

	ofstream output(outputFile+".csv");

	// Write the header line to the new file.
	output << "Sentence" << endl;

	string sentence;

	// For the ADE-NEG.txt:
	// 3rd column is the sentence.

	if (input.is_open()) {
		while (getline (input,line)) {

			size_t pos = line.find("NEG ");
			pos += 4;

			sentence = line.substr(pos);

			// Send the string to the output stream.
			output << sentence << endl;

		}

		// Close the input and output streams.
		input.close();
		output.close();
	}

	else cout << "Error opening file!" << endl;

	return 0;
}