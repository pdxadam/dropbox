# https://blog.devgenius.io/mastering-dropbox-api-communication-with-python-e2b001b371a8
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
import os
from pathlib import Path
import paho.mqtt.publish as publish
import shelve

# >>> Next up: make it send two contents: successes and failures. Then the sensors would work better
#scp to copy via ssh
workingDirectory = "/home/gandalf/dropboxSweeper"
# workingDirectory = "C:\\Users\\cmsmc\\Documents\\Programming\\dropbox"
#--mqtt variables
broker = "mchome.local"
port = 1883
topic = "homeassistant/dropbox/"
appKey = ""
appSecret = ""
shelfFile = "dbData"
#--------------------------------------------------------------------------------
#  Started working toward bringing up multiple dropboxes and transfer locations.
#    Created a file, but got no further than opening it here(commented out below)
#  Would need to finish that and make it a .gitignore to start putting this on Github
# f = open("dropBoxes.txt", "r")
#----------------------------------------------------------------------------------
#os.chdir("/home/pi/Documents/dropbox")
def getShelveData():
    global appKey, appSecret
    with shelve.open(shelfFile) as f:
        try:
            appKey = f["ak"]
            appSecret = f["as"]
        except:
            initShelf()
def initShelf():
    global appKey, appSecret
    with shelve.open(shelfFile) as f:
        appKey = input("What is the app key?")
        appSecret = input("What is the app secret?")
        #I know I should be doing this with pkce.  We'll see if I can get there.
        f["ak"] = appKey
        f["as"] = appSecret
def saveRefreshToken(token):
    with shelve.open(shelfFile) as f:
        f["refresh"] = token

def getRefreshToken():

    with shelve.open(shelfFile) as f:
        try:
            rTok = f["refresh"]
        except:
            rTok = None
        return rTok


def mqttPost(postable):
    f = open("mq", "r")
    l = f.readline()[:-1].split(",")#strip the newline character before splitting it
    f.close()
    publish.single(topic, payload=postable, hostname=broker, client_id = "boardPoster", port = port, auth = {'username':l[0], 'password':l[1]} )
def getToken():
    global appKey, appSecret
    f = open("dbToken", "r")
    appKey = f.readline().strip()
    appSecret = f.readline().strip()

    l = f.readline().strip()#strip the newline character I couldn't get rid of in file
    return l
def oAuthProcess():
    auth_flow = DropboxOAuth2FlowNoRedirect(appKey, appSecret,token_access_type="offline")
    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()
    try:
        oauth_result = auth_flow.finish(auth_code)
        print(oauth_result)
        print("==========")
    except Exception as e:
        print('Error: %s' % (e,))
        exit(1)
    print("initializing dropbox")
    refresh = oauth_result.refresh_token
    
    return refresh

os.chdir(workingDirectory)
getShelveData()
rToken = getRefreshToken()
if rToken == None: #we don't have a refresh token to work from, so we have to authenticate
    #what we ought to do is post a 'need to authenticate' to mqtt, then look in args for an authenticate request and run this
    mqttPost("Error: authentication needed")
    rToken = oAuthProcess()
    saveRefreshToken(rToken)

destLoc = "/mnt/musicShare/"
destPath = Path(destLoc)
print (" Oauth process")


dbx = dropbox.Dropbox(app_key=appKey, app_secret=appSecret,oauth2_refresh_token=rToken)
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
    



