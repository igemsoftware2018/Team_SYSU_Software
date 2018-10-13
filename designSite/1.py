import os

path = os.path.join("static", "img", "Team_img", "2017", "Aachen")
count = 0



for dirpath,dirnames,filenames in os.walk(path):
    print(dirpath, filenames)
    for filename in filenames:
        if 'logo' == filename.split('.')[0]:
            print(filename)    
