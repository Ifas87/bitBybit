PATH_chats = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content\placeholder\search-fzb"

import os
import glob
import re

lister = []

for file in os.listdir(PATH_chats):
    lister.append(os.fsdecode(file))

def extract_file_number(f):
    s = re.findall("\d{1,3}",f)
    return (int(s[0]) if s else -1,f)

print(max(lister,key=extract_file_number))