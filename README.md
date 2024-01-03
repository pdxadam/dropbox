Keeps your Dropbox clean.
This project is based on the Dropbox api. It pulls images from the camera uploads folder and saves them to a local directory before deleting it from Dropbox.

Go to Dropbox App Console to create your own App. Give it files.content.read and files.content.write permissions. Then generate a token and put it in a dbToken file. 

Requires dropbox (pip3 install dropbox)
Requires paho-mqtt (pip3 install paho-mqtt)

During implementation of Oauth I switched files to cleanDropbox2.py. It now asks on first run for the app key and app secret. I should be using pkce to remove the need for the secret instead.


