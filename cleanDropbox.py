import dropbox
import os
from pathlib import Path
import paho.mqtt.publish as publish
# >>> Next up: make it send two contents: successes and failures. Then the sensors would work better
#scp to copy via ssh
workingDirectory = "/home/gandalf/dropboxSweeper"
#--mqtt variables
broker = "mchome.local"
port = 1883
topic = "homeassistant/dropbox/"

#--------------------------------------------------------------------------------
#  Started working toward bringing up multiple dropboxes and transfer locations.
#    Created a file, but got no further than opening it here(commented out below)
#  Would need to finish that and make it a .gitignore to start putting this on Github
# f = open("dropBoxes.txt", "r")
#----------------------------------------------------------------------------------
#os.chdir("/home/pi/Documents/dropbox")
def mqttPost(postable):
    f = open("mq", "r")
    l = f.readline()[:-1].split(",")#strip the newline character before splitting it
    f.close()
    publish.single(topic, payload=postable, hostname=broker, client_id = "boardPoster", port = port, auth = {'username':l[0], 'password':l[1]} )
def getToken():
    f = open("dbToken", "r")
    l = f.readline()[:-1]#strip the newline character I couldn't get rid of in file
    return l
os.chdir(workingDirectory)
aToken = getToken()

destLoc = "/mnt/musicShare/"
destPath = Path(destLoc)
print("initializing dropbox")
dbx = dropbox.Dropbox(aToken)
result = dbx.files_list_folder("/Camera Uploads")
#print(result.entries)
count = 0
failCount = 0
msgText = ""
for e in result.entries:
    if (isinstance(e, dropbox.files.FileMetadata)):
       # print(e.name)
        try:
            dbx.files_download_to_file(destPath / e.name, "/Camera Uploads/" + e.name)
            dbx.files_delete("/Camera Uploads/" + e.name)
            count += 1
            msgText = msgText + "\n:) " + e.name
        except Exception as err:
            failCount += 1
            msgText = msgText + "\n:( " + str(err)


        if count + failCount >= 25:
            break
print("Success: " + str(count))
print("failures: " + str(failCount))
if ((count + failCount) > 0):
    mqttPost(msgText)
    



