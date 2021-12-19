PATH_chats = r"C:\Users\Safi\Desktop\Safi\Year 3\CST 3590 Individual Project\Project files\bitBybit v2\content\chatrooms.txt"

with open(PATH_chats, encoding = 'utf-8') as f:
    line = f.readline()
    while line:
        print(line.split(" : ")[1])
        if not (line.split(" : ")[1]).strip():
            print(True)
        else:
            print(False)

        line = f.readline()
