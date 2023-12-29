Gharge, Sandesh, 00821875

Thesis Title - Automatic Source Code Analysis

# AutomaticSourceCodeAnalysis
Desktop Application designed specifically to get overview of any project which includes 

	- Number of files
	- Number of lines
	- Number of code
	- Number of comments

This software was designed along with mentorship of Prof. Udo Garmaan, a tool which can help professors evaluate list of projects submitted by students as assignment or projects. Aim of this software is to ease out the effort professor face during evaluation by providing necessary details required for grading. Results can be stored offline in an excel file in the form of grades, comments, etc. and can be used later for reference.

## Prerequisites: 

Python version 3.10

pyqt6 (PyQt 6.4):
Install command - pip install pyqt6

pandas (for data analysis):
Install command - pip install pandas

pygount (for code Analysis).
Install command - pip install pygount

pyjslint (for analysis of Javascript files):
Install command - pip install pyjslint

pyinstaller (for creating executable files for desktop):
Install command - pip install pyinstaller
Build command - pyinstaller --onefile main.py

pip install requests

## Project Outline

The project has 3 files at the moment:
- main.py
- listmodel.py
- analyserWindow.py

main.py reads a ZIP. In the GUI it is possible to set a name. This name is used as a subfolder name (course folder) in the ./data folder, where the ZIP is extracted to. Then the files and subfolders of the course folder are analysed. A list with the submissions is created.

listmodel.py is mainly used at the moment for the list representation of the submissions.

analyserWindow.py is dialog that opens for evaluation of a project, by default it analses the files types, code written along with the comments added. It has a grading tab to grade the window, remark text field to add comments.

## How to run

1. Dowload or clone project from git
Sample Link - https://github.com/sandeshgharge/thesis-automaticSourceCodeAnalysis

2. Run the application using main.py

3. Upload the zip file and Start the analysis

## Links

# 1. Code Repository

https://github.com/sandeshgharge/thesis-automaticSourceCodeAnalysis

