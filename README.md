# Forum Handler Scripts for NPTEL

# Installation instructions
	1. pip install --upgrade google-api-python-client

	2. Go to https://console.developers.google.com/apis/credentials

	3. Login using "reviewer1@nptel.iitm.ac.in" as email id.

	4. Click the download button to the right of the "ForumHandler" client ID.

	5. Move this file to this directory and rename it client_secret.json

	6. pip install tabulate

# Running instructions

	For getting the forum usage statistics:

		Fill groups.txt with the list of nptel group email ids as follows:
		noc17-cs27-discuss
		noc17-cy11-discuss
		...

		$ python get_forum_activity.py

		This will open a Google sign-in page in the browser. Sign-in with "reviewer1@nptel.iitm.ac.in" 
		The script will now run. It will display a table within the shell and also store the same data as a csv file with the name table.csv 

	For extracting all mails from "Introduce Yourself" thread corresponding to a particular nptel group:

		$ python get_introductions.py --group="<group-name>"

		eg.
		  python get_introductions.py --group="noc17-cs27-discuss"

		This will open a Google sign-in page in the browser. Sign-in with "reviewer1@nptel.iitm.ac.in" .
		The script will now run. It will store the data as a csv file with the name <group-name>-intros.csv 
		eg. noc17-cs27-discuss-intros.csv

