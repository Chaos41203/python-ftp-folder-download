from ftplib import FTP
import os 
from multiprocessing import Pool
from datetime import datetime, timedelta
import warnings
import re

ftime = datetime.now()

remoteDirTree = []

#Download file quene
fileQuene = []

#Sub path
cellPath = ''

#Local root path (windows)
localRootPath = r"C:\test\5G"
#remote root path
remoteDestPath = r"/5G"

#declare pool object
pool = None

#Init pool object and change directory to the destination
def init():
    global pool
    print("PID %d: initializing pool..." % os.getpid())
    pool = ftpLogin()
    warnings.simplefilter("ignore")
    cwdToDestDir(pool)

#Login to the FTP server
def ftpLogin():
    host, port, usr, pwd = '60.248.106.201', 21, 'joseph', 'admin'
    ftp=FTP()
    # ftp.set_debuglevel(2)     #For the debug usage
    #Connect to the FTP server
    ftp.connect(host, port)
    #Login
    ftp.login(usr, pwd)
    #Disable passive mode
    ftp.set_pasv(False)

    return ftp

def addFileToQuene_upload(ftp):
    global remoteDirTree, localFileQuene
    localFilePath = ''
    remoteFilePath = ''
    for dirPath, dirNames, fileNames in os.walk(localRootPath):
        if dirPath != localRootPath:
            remoteDirTree.append(remoteDestPath + dirPath.split(localRootPath)[-1].replace('\\','/'))
        for f in fileNames:
            localFilePath = os.path.join(dirPath, f)
            remoteFilePath = remoteDestPath + dirPath.split(localRootPath)[-1].replace('\\','/') + '/' + f
            fileQuene.append((localFilePath, remoteFilePath))

#Get the object list of work directory and determine if the object is file or directory
def listRemoteDir(ftp):
    #Parameter init
    ls = []
    fileOrDir = []
    objWithAttr = []

    #Get the list of all object in current directory with only object name
    ls = ftp.nlst()

    #Get thelist of all object in current directory with detail information
    ftp.dir(fileOrDir.append)

    #Combine the object and the file-or-directory attribute as key and value
    for i in range(len(ls)):
        objWithAttr.append(ls[i] + ':' + fileOrDir[i][0])
    return objWithAttr

#Create folder if the object in work directory is folder
def mkCellDir(fullPath, ifFolderExist):
    localDirList = []

    #Change directory back(cd ..) to check if the folder is created or not
    localDirList = os.listdir(fullPath.split(ifFolderExist)[0])
    if fullPath.split('\\')[-1] not in localDirList:
        os.mkdir(fullPath)

#Download the file using the tuple object in fileQuene list
def downloadObj(localFile, remoteFile):
    #Get the logged in FTP object
    ftp = pool

    #Create local file
    lf = open(localFile, "wb")

    print(localFile, " <-- ", remoteFile)

    #Downloading file
    ftp.retrbinary("RETR " + remoteFile, lf.write)

    print("success")

    #Local file close
    lf.close()

def cwdToDestDir(ftp):
    #Split the remote root as list and change the directory to destination
    route = remoteDestPath.split('/')
    for folder in route:
        if folder != "":
            ftp.cwd(folder)

def addFileToQuene_download(ftp, TargetDirList):
    #Parameter init
    localFilePath = ''
    localFullCellPath = ''
    remoteFullCellPath = ''
    counter = 0

    for obj in TargetDirList:
        counter = counter + 1

        #The sub-path is about to change
        global cellPath

        #If the object is file
        if obj.split(':')[1] == '-':

            #About to add tuple object into fileQuene list
            global fileQuene

            #Join the path with file name
            cellPath = os.path.join(cellPath, obj.split(':')[0])

            #Join the full path with download location
            localFullCellPath = os.path.join(localRootPath, cellPath)

            #Full path of FTP server file
            remoteFullCellPath = os.path.join(remoteDestPath, cellPath)

            #Change the path format to linux format
            remoteFullCellPath = remoteFullCellPath.replace('\\','/')

            #Append the tuple(localFullPath, remoteFullPath) into fileQuene list
            fileQuene.append((localFullCellPath,remoteFullCellPath))

            #Delete the file name from path string
            cellPath = cellPath.split(obj.split(':')[0])[0]

            #If meet the last file, change the directory back(cd ..) to previous directory 
            if counter == len(TargetDirList):
                complete_Folder = cellPath.split("\\")[-2]
                cellPath = cellPath.split(complete_Folder)[0]

        #If the object is directory
        elif obj.split(':')[1] == 'd':
            #List init
            cellDirList = []

            #Join the path with directory name
            cellPath = os.path.join(cellPath, obj.split(':')[0])

            #Join the full path with download location
            localFullCellPath = os.path.join(localRootPath, cellPath)

            #Full path of FTP server directory
            remoteFullCellPath = os.path.join(remoteDestPath, cellPath)

            #Change the path format to linux format
            remoteFullCellPath = remoteFullCellPath.replace('\\','/')

            #Create directory if not exist
            mkCellDir(localFullCellPath, obj.split(':')[0])

            #Change directory into directory object
            ftp.cwd(remoteFullCellPath)

            #Get the object fle into directory object
            cellDirList = listRemoteDir(ftp)

            #Recusive the function
            addFileToQuene_download(ftp, cellDirList)

if __name__ == '__main__':
    # #Login
    ftp = ftpLogin()

    addFileToQuene_upload(ftp)

    # #Parameter init
    # TargetDirList = []

    # #Change directory to destination
    # cwdToDestDir(ftp)
    
    # #Get the object list of work directory and determine if the object is file or directory
    # TargetDirList = listRemoteDir(ftp)

    
    # addFileToQuene_download(ftp, TargetDirList)
    # # print(fileQuene)
    # p = Pool(initializer=init, processes=6)
    # print(p.starmap(downloadObj,fileQuene))
    # p.close()
    # p.join()
    # ftp.quit()
    # etime = datetime.now() - ftime
    # print(etime)