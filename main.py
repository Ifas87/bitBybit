# Required libraries from Flask to File and OS utilities

from flask import *
import os
import time
import sys
from datetime import datetime
import tarfile
import secrets
import re
from threading import Thread
import shutil
from werkzeug.utils import secure_filename


# Global variables required for later use in the project.
current_chat = ""

# Regex for finding room names
newRoomRegex = "^(\w+)$"
customPath = r""

# Creating a relative path to the project files for the "content" directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Creating flask environment variables as relative paths
app = Flask(__name__)
app.config.update(
    UPLOADED_PATH= os.path.join(basedir,'content')
)

# Global variables to be utilised later
# PATH strings as a shortcut to important folders
PATH_chats = app.config["UPLOADED_PATH"] + r"\chatrooms.txt"
PATH_tempfiles = app.config["UPLOADED_PATH"] + r"\tempZipFiles"

# Error messages to be flashed for the create and join variables 
ERR_pass = "Wrong passcode provided!"
ERR_room = "No room by that name present!"
ERR_word = "Room names are only one word long!"
ERR_same = "Room with that name already exists!"

# Session creating temporary variables
secret = secrets.token_urlsafe(32)
app.secret_key = secret


"""
    desc- a function that replaces the '.' character in a filename to a '-' to serve as a folder name and vice versa
    param- the original filename, the old delimiter either '.' or '-', the replacement delimiter either '.' or '-'
"""
def switchFiletoFolder(filename, olddelim, newdelim):
    if olddelim in filename:
        real_type = filename.split(olddelim)[0] + newdelim + filename.split(olddelim)[1]
    else:
        real_type = filename
    return real_type


"""
    desc- a function that returns the version comment from the VersionInfo txt file using a 'version number'
    i.e "Version 1", "Version 2" etc. This is done by looping through line of the file until the right version appears.

    param- the version number and the path where that file is located
"""
def lineExtractor(version, versionFile):
    result = ""
    with open(versionFile, "r") as f:
        for line in f:
            if (version in line):
                result = line
    return result

"""
    desc- a function that returns the version number attached to a file when tracking changes by splitting the 
    filename on the delimiter '.' and getting the text on the left side of the delimiter (the filename not the extension)

    param- the base filename without the additional PATH attached to it.
"""
def getVersion(filename):
    return os.path.splitext(filename)[0]


"""
    desc- a function that returns a list of filenames and foldernames present in a directory. the result is a list of file
    and folder names

    param- the path of the directory to loop through.
"""
def lister(dir_path):
    result = []
    for file in os.listdir(dir_path):
        result.append(os.fsdecode(file))
    
    return result


"""
    desc- a function that returns a list of filenames and excludes folder names. the result is a list of
    filenames

    param- the path of the directory to loop through.
"""
def lister2(dir_path):
    result = []
    for file in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, os.fsdecode(file))):
            continue
        result.append(os.fsdecode(file))
    
    return result


"""
    desc- a function that returns all filenames within a directory, reserved for use in a version control folder
    to return the filename as an Integer

    param- the filename from a list
"""
def extract_file_number(f):
    s = re.findall("\d{1,3}",f)
    return (int(s[0]) if s else -1,f)

"""
    desc- a chat deletion timer, runs on a separate thread and countsdown to 0, at the end of the timer
    the directory associated to the chat is removed erasing all content in the chat. 

    param- the countdown value from the dropdown box value and the chatname/directory name to delete later
"""
def timer(t, chatname):
    time.sleep(3)
    print(current_chat, chatname)
    with app.app_context(), app.test_request_context():
        while t:
            time.sleep(1)
            t -= 1
            print(t)
    
        if current_chat == chatname:
            print("same")
            os.rmdir(app.config["UPLOADED_PATH"] + "/" + chatname)
        else:
            print("not same")
            os.rmdir(app.config["UPLOADED_PATH"] + "/" + chatname)
    
    with open(PATH_chats, "r") as f:
        lines = f.readlines()
    with open(PATH_chats, "w") as f:
        for line in lines:
            print(line)
            if chatname not in line.strip("\n"):
                f.write(line)


"""
    desc- The primary URL route. Displays the index page and sets up initial session
    variable "current_room" as the temporary folder

    param- none
"""
@app.route('/')
def hello():
    session["current_room"] = "placeholder"
    return render_template('index.html', template_folder='templates')


"""
    desc- The create route that allows users to create rooms deternmine their lifetime
"""
@app.route('/create',methods=['POST','GET'])
def create():
    # Response to POST request scenario
    if request.method == 'POST':
        # Accessing form element values
        room = request.form.get('links')
        passcode = request.form.get('passcodes')
        duration = int(request.form.get('TTL'))
        allRoomNames = []

        with open(PATH_chats, encoding = 'utf-8') as f:
            line = f.readline()
            while line:
                allRoomNames.append(line.split(":")[0].strip())
                line = f.readline()

        reg = re.compile( r'^(?=.*\b(?:' + "|".join(allRoomNames) + r')\b).*foo' )

        # Initial search to find related or similar rooms
        if(re.search(newRoomRegex, room)):

            # String matching all rooms str with the value obtained from
            # Return error message in the event it does not work
            if(reg.findall(room)):
                flash(ERR_same)
                return redirect(url_for('create'))
            
            # Setting the room session variable to the created one
            session["current_room"] = room

            # Create room directory
            if not (os.path.exists( os.path.join(app.config["UPLOADED_PATH"], room) )):
                os.mkdir((app.config["UPLOADED_PATH"]+"/"+room))
            # Add new room to the roomList
            with open(PATH_chats, "a", encoding = 'utf-8') as f:
                f.write("{} : {}\n".format(room, passcode))
            
            # Check the timer value obtained from the form. 
            if(not(duration >= 20000)):
                thread = Thread(target = timer, args = (duration, room)) # !!!! Change this line in code to the value of the TTL dropdown box 
                thread.start()
            
            # forward to user to the created chat page
            return redirect(url_for('chat'))
        else:

            # Error scenarios that return to the previous page
            flash(ERR_word)
            return redirect(url_for('create'))
    
    # default route when redirected to this page instead of a form request  
    return render_template('create.html', template_folder='templates')


"""
    desc- The select route that allows users to select rooms that are already present
"""
@app.route('/select',methods=['POST','GET'])
def select():

    # Response to form POST request scenario
    if request.method == 'POST':

        # obtaining values from the FORM posted
        room = request.form.get('links')
        passcode = request.form.get('passcodes')

        # Cross checking with the room file to find the appropriate group
        with open(PATH_chats, encoding = 'utf-8') as f:
            
            # initial line read
            line = f.readline()
            while line:

                # scenrio one, the lack of a pascode attached to the room
                # in this scenario so long as the room exists it will be loaded in
                # redirect to the chat page with the correct room as the reference
                if(line.split(" : ")[0] == room):
                    if not (line.split(" : ")[1]).strip():
                        session["current_room"] = room
                        return redirect(url_for('chat'))
                    
                    # scenario two, the room has a passcode and the input passcode
                    # from the user is correct
                    # redirect to the chat page with the correct room as the reference
                    else:
                        if ((line.split(" : ")[1]).strip() == passcode):
                            session["current_room"] = room
                            return redirect(url_for('chat'))
                        
                        # Incorrect passcode scenario, highlight the error and refresh the page
                        else:
                            flash(ERR_pass)
                            line = f.readline()
                            return redirect(url_for('select'))
                else:
                    # If the line is not part of the room List then continue to the next line
                    line = f.readline()
                    continue
            
            # no room scenrio, highlight the error and refresh the page
            flash(ERR_room)
            return redirect(url_for('select'))

    # default route when redirected to this page instead of form request         
    return render_template('select.html', template_folder='templates')
 

"""
    desc- The chat route common for all users that uses a roomname to dynamically
    generate the contents in the room when redirected to.
"""
@app.route('/chat',methods=['POST','GET'])
def chat():
    # Initial PATH and name related fields
    roomname = session["current_room"]
    customPath = "" + app.config["UPLOADED_PATH"] + "/" + roomname
    global current_chat
    current_chat = session["current_room"]

    # Scenario for when users enter and submit a message
    if request.method == 'POST':

        # Obtaining the message string from within the form
        text = request.form.get('chatarea')
        if not text == "":

            # Saving the message in a .txt file with a unique date related name
            # format tEXt followed by the year month date hour minute and second
            timestr = time.strftime("tEXt%Y%m%d-%H%M%S") + ".txt"
            with open((customPath+"/"+timestr), "w") as f:
                f.write(text)

    # Dynamic generation of content using files present in the room folder
    keyCount = 0
    chat_content = {}

    directory = os.fsencode(app.config["UPLOADED_PATH"])

    # Scanning section of the room to extract all the content from the file.    
    for file in os.listdir(customPath):
        filename = os.fsdecode(file)
        if filename.startswith("tEXt"):

            # Unload string messages from each text file
            with open((customPath + "/" + filename), "r", encoding = 'utf-8') as f:
                data = f.read().replace('\n', ' ')
            chat_content[("tEXt"+str(keyCount))] = data
            keyCount+=1

        # Section to unload a version control file
        elif(os.path.isdir(customPath+"/"+filename)):
            # Create a path into the file folder
            inner_dir_path = customPath + r"\\" + filename
            inner_dir_path_contents = lister(inner_dir_path)
            
            # Extract the fike with the highest version number
            inner_latest_file = max(inner_dir_path_contents, key=extract_file_number)

            # Replace the version number name of a file with the original file
            # replace 1.pdf with the original filename.pdf
            real_filename = switchFiletoFolder(filename, "-", ".")
            chat_content[real_filename+": Version "+getVersion(inner_latest_file)] = (inner_dir_path) 

        else:
            # Final scenario for stand alone files and ZIP files
            chat_content[filename] = (customPath + "/" + filename)
            keyCount+=1
        
    return render_template('chat_template.html', template_folder='templates', var=roomname, dict_item=chat_content)


"""
    desc- The options route that allows you to customise the file upload options such as compression and
    add a version control note to each file
"""
@app.route('/options',methods=['POST','GET'])
def options():
    # Initial PATH and name related fields
    roomname = session["current_room"]
    customPath = r"" + app.config["UPLOADED_PATH"] + r"\\" + roomname
    relativePath = "content/tempZipFiles"
    dir_contents = []
    inner_dir_path = r""

    dir_contents = lister(customPath)

    # After form post scenario to handle file uploads
    if request.method == 'POST':

        # adjusting the checkbox value to reflect a boolean value from JS to python
        checks = True if request.form.get("switch") == 'true' else False
        zipname = request.form.get("links")

        # Chekc if there are any files
        print(request.files.getlist("filesInput"))
        if len(request.files.getlist("filesInput")) > 1:
            # obtain a filelist from the client of files sent
            files = request.files.getlist("filesInput")
            folder_name=""

            # Scenario for packing multiple files into a compressed tarfile
            if checks == True:
                # Create a temporary refuge for the files to save into before being
                # compressed into a tarfile
                if not os.path.isdir(PATH_tempfiles):
                    os.mkdir(PATH_tempfiles)
                
                # Manipulate the tarfile and insert each downloaded file into the tarfile as they are downloaded
                with tarfile.open(os.path.join(customPath, secure_filename(zipname))+".tar.gz", "w:gz") as tar_handle:
                    for file in files:
                        if file:
                            filename = secure_filename(file.filename)

                            file.save(os.path.join(PATH_tempfiles, filename))
                            tar_handle.add(os.path.join(relativePath, filename))
                            time.sleep(3)

                            # Remove these temporary files after being added to the tarfile
                            os.remove(os.path.join(PATH_tempfiles, filename))
                return redirect(url_for('chat'))

            # In the event of no compression option and storing files as Version control objects
            else:
                # Loop through all files
                for file in files:

                    # creating a folder for each file and adding a versionFile in as well
                    folder_name = switchFiletoFolder(file.filename, ".", "-")
                    inner_dir_path = os.path.join(customPath, folder_name)
                    version_manager_path = os.path.join(inner_dir_path, "VersionInfo/VersionInfo.txt")
                    
                    # Getting the version note from the current uploading user
                    current_changes = request.form.get(file.filename+"textarea")

                    # Scenario for If the folder already exists
                    if folder_name in dir_contents:
                        # Get the current contents of that folder
                        inner_dir_path_contents = lister2(inner_dir_path)
                        temp_version = ""

                        # The if/else exists for in the event with no extension is added to the program
                        try:
                            inner_dir_path_contents = [int(x.split(".")[0]) if "." in file.filename else int(x) for x in inner_dir_path_contents]
                        except ValueError:
                            print("Value Error anticipated")
                        
                        #print(max(inner_dir_path_contents))

                        # Get the highest version number and increment it by 1
                        temp_version = str(max(inner_dir_path_contents)+1)

                        # Save file as the new version number
                        file.save(os.path.join(app.config['UPLOADED_PATH'],
                            (roomname+"/"+folder_name+"/"+ ( str(temp_version)+"."+(file.filename.split(".")[1] if "." in file.filename else file.filename)) ) ))

                        # Add the changes to the VersionInfo file
                        temp_strs = current_changes.replace("\n", " ") + "\n"

                        # print("Reached file reading part")
                        with open(version_manager_path, 'a') as f:
                            f.write("Version "+temp_version +": "+temp_strs)

                    # Scenario for when this is a new file
                    else:
                        # Make the related files and folders required for version control
                        os.mkdir(inner_dir_path)
                        os.mkdir(os.path.join(inner_dir_path, "VersionInfo"))
                        inner_dir_path_contents = lister2(inner_dir_path)

                        # Save file with that name
                        file.save(os.path.join(app.config['UPLOADED_PATH'], 
                            (roomname+"/"+folder_name+"/"+ ("1." +(file.filename.split(".")[1] if "." in file.filename else file.filename) ) )))

                        try:
                            inner_dir_path_contents = [int(x.split(".")[0]) if "." in file.filename else int(x) for x in inner_dir_path_contents]
                        except ValueError:
                            print("Value Error anticipated")

                        # Add those changes and the the uploading note the versionInfo file
                        temp_strs = current_changes.replace("\n", " ") + "\n"

                        with open(version_manager_path, 'a') as f:
                            f.write("Version 1: "+ temp_strs)
                
                # Go back to the chat page
                return redirect(url_for('chat'))


    # Provide a reference list for verion tracked files so these the status of these files can be tracked
    # client side for less load on the server
    reference = []
    for file in os.listdir(customPath):
        if os.path.isdir(os.path.join(customPath, os.fsdecode(file))):
            reference.append( switchFiletoFolder(os.fsdecode(file), '-', '.') )
    return render_template('options.html', template_folder='templates', reference=reference)


"""
    desc- The version downloading route that allows you to pick different versions and download
    those files to your device 
"""
@app.route('/versions/',methods=['POST','GET'])
def versions():
    versionContent = {}

    # Get the form posted with the user's requested file version
    if request.method == 'POST':
        folder_name = session["parent_directory"]
        filename = request.form.get("versions")

        # Get the real filename from the folder name and download with that name
        original_name = os.path.basename(folder_name + "/" + switchFiletoFolder(os.path.basename(folder_name), "-", "."))
        return send_file((folder_name+"/"+filename), as_attachment=True, download_name=original_name)
    
    folder_name = request.args.get('data-status')
    session["parent_directory"] = folder_name

    # Scenario to generate the page initially if the file is a version control file render the HTML page
    # If not just return the file using the PATH
    if(os.path.isdir(folder_name)):
        temp = lister2(folder_name)
        inner_dir_path_contents = [int(x.split(".")[0]) if "." in x else int(x) for x in temp]

        for index in temp:
            tempStr = "Version "+str(int(index.split(".")[0]) if "." in index else int(index))
            versionContent[index] = lineExtractor(tempStr, (folder_name+"/"+"VersionInfo/VersionInfo.txt"))

        return render_template('versions.html', template_folder='templates', versions = versionContent)
    else:
        return send_file(folder_name)



"""
    desc- Not a Link tied to a webpage. The link is used to update the webpage with activity from new users
    It contains the same commands as the chat codes
"""
@app.route('/updater', methods=['POST','GET'])
def update():
    if request.method == 'POST':
        roomname = str(request.get_data()).split("/")[1]
        customPath = r"" + app.config["UPLOADED_PATH"] + "/" + (str(roomname)[:-1]).strip()
        keyCount = 0
        chat_content = {}

        if os.path.exists(customPath):
            for file in os.listdir(customPath):
                filename = os.fsdecode(file)
                if filename.startswith("tEXt"): 
                    with open((customPath + "/" + filename), "r", encoding = 'utf-8') as f:
                        data = f.read().replace('\n', ' ')
                    chat_content[("tEXt"+str(keyCount))] = data
                    keyCount+=1

                elif(os.path.isdir(customPath+"/"+filename)):
                    inner_dir_path = customPath + r"\\" + filename
                    inner_dir_path_contents = lister(inner_dir_path)
                    
                    inner_latest_file = max(inner_dir_path_contents, key=extract_file_number)

                    real_filename = switchFiletoFolder(filename, "-", ".")

                    chat_content[real_filename+": Version "+getVersion(inner_latest_file)] = (inner_dir_path) 

                else:
                    chat_content[filename] = (customPath + "/" + filename)
                    keyCount+=1

        else:
            chat_content["DELETED"] = "".format('"{}" timer has expired ', roomname)

        return json.dumps(chat_content)


"""
    desc- Canonical start of the program. It utilises the a self-signed certificate and key to
    provide a safer transfer of data
"""
if __name__=='__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))
