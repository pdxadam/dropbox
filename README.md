Keeps your Dropbox clean.
This project is based on the Dropbox api. It pulls images from the camera uploads folder and saves them to a local directory before deleting it from Dropbox.

Go to Dropbox App Console to create your own App. Give it files.content.read and files.content.write permissions. Then generate a token and put it in a dbToken file. 

Requires dropbox (pip3 install dropbox)
Requires paho-mqtt (pip3 install paho-mqtt)

The challenge now is that the Dropbox has moved to short-lived tokens, so it can't just sit there and work for months on end the way it used to. I'm not sure there's a good answer to this.
