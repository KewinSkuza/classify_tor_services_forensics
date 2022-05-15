This application goes though Tor's secret services and categorizes them. Additionally it displays the resutls in a pie chart alongside how many services are available from the dataset provided

NOTE:
	- Required Files:
		- Tor_Forensics.py
		- requirenments.txt
		
	- Prerequisites:
		- Python 3.9 or higher
		- pip
		- Windows operating system
		- Tor browser
		
Installation:

	- Open command prompt in directory where the files are located

	- Make sure that python is installed on your device
		= This can be done using the command py --version or python --version
		= Version Python 3.9 is confirmed to work

	- Make sure that pip is installed on your machine
		= Can be done using pip --version command

	- Download dependencies by issuing:
		= pip install -r requirenments.txt
		
	- Download the Tor browser
	
	- You need to launch the Tor service for the application to work. You can do this byb going to the directory where you downloaded Tor and following this directory structure -> Browser -> TorBrowser -> Tor -> and launch the tor.exe application. This will allow you to use the application. Remember that in order to turn this off you need to go to task Manager and manually turn of the application

	- Now you are ready to launch the application
	
Usage:

	Run the application in python using command: py Tor_Forensics.py OR
	python Tor_Forensics.py
	
Results:
	
	- The applciaion will display the contents of the database inside the terminal window
	
	- An additional window will be displayed with graphs visualizing the data gathered