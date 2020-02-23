#!/usr/bin/env python3

### IMPORTS ###
import os
import sys
import shutil
import glob
import json
import time
import re
import uuid
from argparse import ArgumentParser
from PyPDF2 import PdfFileReader
sys.path.append("..")  # Adds higher directory to python modules path.
# needs imagemagick, pdftk

__prog_name__ = "sync"

# Parameters and folders for sync
syncDirectory = "/ReMarkable/sync"
remarkablePCDirectory = "/ReMarkable/device"
remContent = "/xochitl"
remTemplates = "/templates/"
remarkableDirectory = "/home/root/.local/share/remarkable/xochitl"
remarkableDirectoryTemplates = "/usr/share/remarkable/templates"
remarkableUsername = "root"
remarkableIP = "10.11.99.1"
emptyFilePath = "/root/script/empty.pdf"


def main():
    while True:
        print(" ")
        print("Remarkable Sync Script. Please choose a command.")
        print("d)   Download files from the ReMarkable tablet")
        print("u)   Upload files to the ReMarkable tablet")
        print("e)   Export files to the Library folder")
        print("i)   Import files from the Library folder")
        print("s)   Sync files (download, export, import, upload)")
        print("c)   Config program")
        print("h)   Print help")
        print("q)   Quit program")
        print("d/u/e/i/s/c/h/q> ")
        command = input()

        if command == "q":
            break
        elif command == "d":
            downloadRM()
        elif command == "u":
            loadOnRM()
        elif command == "e":
            convertFiles()
        elif command == "i":
            prepareUploadPDF(False)
            prepareUploadEBUP(False)
        elif command == "s":
            print("Sync in progress")
            downloadRM()
            convertFiles()
            prepareUploadPDF(False)
            prepareUploadEBUP(False)
            loadOnRM()
        elif command == "c":
            config()
        elif command == "h":
            helpInfo()
        else:
            helpInfo()


def helpInfo():
    print("Help")


def config():
    print("Configuring the sync script and rclone")
    print("Configuring rclone, please follow the instruction.")
    rcloneConfig = "rclone config"
    os.system(rcloneConfig)

### BACK UP  (FULL) ###


def downloadRM():
    print("Backing up your remarkable files")
    # Sometimes the remarkable doesnt connect properly. In that case turn off & disconnect -> turn on -> reconnect
    backupCommand = "".join(["rclone copy -P --exclude '*.{thumbnails,cache}/**' ", "remarkable:",
                             remarkableDirectory, " ", "'", remarkablePCDirectory + remContent, "'"])
    os.system(backupCommand)
    backupCommandTemplates = "".join(
        ["rclone copy -P ", "remarkable:", remarkableDirectoryTemplates, " ", "'", remarkablePCDirectory + remTemplates, "'"])
    os.system(backupCommandTemplates)

### BACK UP  (FULL) ###


def loadOnRM():
    print("Sync remarkable files")
    # Sometimes the remarkable doesnt connect properly. In that case turn off & disconnect -> turn on -> reconnect
    backupCommand = "".join(["rclone copy -P  --exclude '*.{thumbnails,cache}/**' ",  "'",
                             remarkablePCDirectory + remContent,  "'",  " ", "remarkable:", remarkableDirectory])
    os.system(backupCommand)
    sync = "".join(["ssh ", remarkableUsername, "@",
                    remarkableIP, " ",  "systemctl restart xochitl"])
    os.system(sync)


def setDirectory(parent):
    basePath = remarkablePCDirectory + remContent + "/"
    path = ""
    pathArray = []
    while parent != "":
        meta = json.loads(open(basePath + parent + ".metadata").read())
        pathArray.insert(0, meta["visibleName"])
        path = meta["visibleName"] + "/" + path
        parent = meta["parent"]
    return path

### CONVERT TO PDF ###


def convertFiles():
    # Get file lists
    files = [x for x in os.listdir(
        remarkablePCDirectory+remContent) if "." not in x]
    files = [x for x in files if glob.glob(
        remarkablePCDirectory+remContent + "/" + x + ".metadata") != []]

    for i in range(0, len(files)):
        # get file reference number
        refNrPath = remarkablePCDirectory + remContent + "/" + files[i]
        print("ID: "+refNrPath)
        # get meta Data
        meta = json.loads(open(refNrPath + ".metadata").read())
        content = json.loads(open(refNrPath + ".content").read())
        fname = meta["visibleName"]
        # Does this lines file have an associated pdf?
        isPDF = content["fileType"] == "pdf"

        pathDirectoryFile = setDirectory(meta["parent"])
        # will create the directory only if it does not exist
        os.makedirs(syncDirectory + "/" + pathDirectoryFile, exist_ok=True)

        # Get list of all rm files i.e. all pages
        rmPaths = glob.glob(refNrPath+"/*.rm")
        npages = len(rmPaths)

        syncFilePath = syncDirectory + "/" + pathDirectoryFile + fname + ".pdf"
        if npages != 0 & (not meta["deleted"]):
            if isPDF:
                # deal with annotated pdfs
                # have we exported this thing before?
                print("exporting PDF: " + fname +
                      "\n    path: " + syncFilePath)
                local_annotExist = True if glob.glob(
                    syncFilePath[:-4] + ".annot.pdf", recursive=True) != [] else False
                remoteChanged = True
                if local_annotExist:
                    local_annotPath = glob.glob(
                        syncFilePath[:-4]+".annot.pdf", recursive=True)[0]
                    local_annot_mod_time = os.path.getmtime(local_annotPath)
                    remote_annot_mod_time = int(
                        meta["lastModified"])/1000  # rm time is in ms
                    # has this version changed since we last exported it?
                    remoteChanged = remote_annot_mod_time > local_annot_mod_time
                if remoteChanged:
                    # only then fo we export
                    origPDF = refNrPath + ".pdf"
                    # get info on origin pdf
                    input1 = PdfFileReader(open(origPDF, "rb"))
                    # Override pages number to maintain correspondence to the original PDF
                    npages = input1.getNumPages()
                    pdfsize = input1.getPage(0).mediaBox
                    pdfx = int(pdfsize[2])
                    pdfy = int(pdfsize[3])

                    try:
                        os.mkdir('temp')
                    except:
                        pass

                    merged_rm = "temp/merged_rm.pdf"
                    rm2pdfCommand = "".join(
                        ["./rm2pdf", " ", refNrPath, " ", merged_rm, " -t ./empty.pdf"])
                    os.system(rm2pdfCommand)

                    stampCmd = "".join(["pdftk ", "\""+origPDF+"\"", " multistamp ",
                                        merged_rm, " output ", "\""+syncFilePath[:-4] + ".annot.pdf\""])
                    os.system(stampCmd)
                    # Remove temporary files
                    shutil.rmtree("temp", ignore_errors=False, onerror=None)
                    print("exporting done!")
                else:
                    print(fname + " has not changed")
            else:
                # deal with notes
                # needs imagemagick
                print("exporting Notebook: " + fname)
                inSyncFolder = True if glob.glob(
                    syncFilePath[:-4] + ".notes.pdf", recursive=True) != [] else False
                remoteChanged = True
                if inSyncFolder:
                    local_annot_mod_time = os.path.getmtime(
                        syncFilePath[:-4] + ".notes.pdf")
                    remote_annot_mod_time = int(
                        meta['lastModified'])/1000  # rm time is in ms
                    # has this version changed since we last exported it?
                    remoteChanged = remote_annot_mod_time > local_annot_mod_time
                if remoteChanged:

                    # Create merged_backgound
                    try:
                        os.mkdir('temp')
                    except:
                        pass
                    with open(refNrPath+".pagedata") as file:
                        backgrounds = [line.strip() for line in file]

                    bg_pg = 0
                    bglist = []

                    # Add missing backgrounds at the end (which are sometimes omitted)
                    pagesNumber = content['pageCount']
                    diff = pagesNumber - len(backgrounds)
                    for i in range(diff):
                        backgrounds.append("Blank")

                    for bg in backgrounds:
                        convertSvg2PdfCmd = "".join(["rsvg-convert -f pdf -o ", "temp/bg_" + str(
                            bg_pg) + ".pdf ", "'", remarkablePCDirectory + remTemplates + bg + ".svg", "'"])
                        os.system(convertSvg2PdfCmd)
                        bglist.append("temp/bg_"+str(bg_pg)+".pdf ")
                        bg_pg += 1
                    merged_bg = "temp/merged_bg.pdf"
                    os.system("convert " + (" ").join(bglist) +
                              " " + merged_bg)
                    input1 = PdfFileReader(open(merged_bg, 'rb'))

                    merged_rm = "temp/merged_rm.pdf"
                    rm2pdfCommand = "".join(
                        ["./rm2pdf", " ", refNrPath, " ", merged_rm, " -t ./empty.pdf"])
                    os.system(rm2pdfCommand)

                    stampCmd = "".join(["pdftk ", "\""+merged_bg+"\"", " multistamp ",
                                        merged_rm, " output " + "\""+syncFilePath[:-4] + ".notes.pdf"+"\""])
                    os.system(stampCmd)
                    # Delete temp directory
                    shutil.rmtree("temp", ignore_errors=False, onerror=None)
                else:
                    print(fname + " has not changed")
        if isPDF & (not meta["deleted"]):
            # copy file
            print("copying PDF: " + fname)
            inSyncFolder = True if glob.glob(syncFilePath) != [] else False
            remoteChanged = True
            if inSyncFolder:
                local_annot_mod_time = os.path.getmtime(syncFilePath)
                remote_annot_mod_time = int(
                    meta['lastModified'])/1000  # rm time is in ms
                # has this version changed since we last exported it?
                remoteChanged = remote_annot_mod_time > local_annot_mod_time
            if remoteChanged:
                shutil.copy2(refNrPath+".pdf", syncFilePath)
                print("copying done!")
            else:
                print(fname + " has not changed")

### UPLOAD ###


def prepareUploadPDF(dry):
    # list of files in Library
    syncFilesList = glob.glob(syncDirectory + "/**/*.pdf", recursive=True)
    # remove noted files and notes
    syncFilesList = [x for x in syncFilesList if ".annot" not in x]
    syncFilesList = [x for x in syncFilesList if ".notes" not in x]

    # list of files on the rM (hashed)
    rmPdfList = glob.glob(remarkablePCDirectory + remContent + "/*.pdf")
    rmPdfList = [x[:-4] for x in rmPdfList]

    # list of all elements in the remarkable
    rmElements = glob.glob(remarkablePCDirectory + remContent + "/*.content")
    rmElements = [x[:-8] for x in rmElements]

    # list of all folders in the remarkable
    rmDirectories = [x for x in rmElements if x not in rmPdfList]

    for pathFile in syncFilesList:
        pathFile = pathFile[:-4]

        relativePath = os.path.relpath(pathFile, syncDirectory)
        fName = os.path.basename(pathFile)
        directoryPath = os.path.dirname(relativePath)

        directoriesName = re.split("/|\\)", directoryPath)

        parentUUID = ""
        for directory in directoriesName:
            parentUUID = mkdir(rmDirectories, parentUUID, directory, dry)
            rmDirectories.append(remarkablePCDirectory +
                                 remContent + '/' + parentUUID)

        cp(rmPdfList, directoryPath, fName, parentUUID, "pdf", dry)


def prepareUploadEBUP(dry):
    # list of files in Library
    syncFilesList = glob.glob(syncDirectory + "/**/*.epub", recursive=True)
    # remove noted files and notes
    syncFilesList = [x for x in syncFilesList if ".annot" not in x]
    syncFilesList = [x for x in syncFilesList if ".notes" not in x]

    # list of files on the rM (hashed)
    rmPdfList = glob.glob(remarkablePCDirectory + remContent + "/*.epub")
    rmPdfList = [x[:-5] for x in rmPdfList]

    # list of all elements in the remarkable
    rmElements = glob.glob(remarkablePCDirectory + remContent + "/*.content")
    rmElements = [x[:-8] for x in rmElements]

    # list of all folders in the remarkable
    rmDirectories = [x for x in rmElements if x not in rmPdfList]

    for pathFile in syncFilesList:
        pathFile = pathFile[:-5]

        relativePath = os.path.relpath(pathFile, syncDirectory)
        fName = os.path.basename(pathFile)
        directoryPath = os.path.dirname(relativePath)

        directoriesName = re.split("/|\\)", directoryPath)

        parentUUID = ""
        for directory in directoriesName:
            parentUUID = mkdir(rmDirectories, parentUUID, directory, dry)
            rmDirectories.append(remarkablePCDirectory +
                                 remContent + '/' + parentUUID)
        cp(rmPdfList, directoryPath, fName, parentUUID, "epub", dry)

# Creates folder if it doesn't exist
# returns UUID


def mkdir(rmDirectories, parentUUID, name, dry):
    candiates = []
    for d in rmDirectories:
        meta = json.loads(open(d + ".metadata").read())
        if meta["parent"] == parentUUID:
            candiates.append(d)

    UUID = ""

    for c in candiates:
        meta = json.loads(open(c + ".metadata").read())
        if meta["visibleName"] == name:
            UUID = os.path.basename(c)

    if UUID:  # Folder exists
        return UUID
    # Create the new folder
    return writeDir(parentUUID, name, dry)

# Creates folder
# returns UUID


def writeDir(parentUUID, name, dry):

    UUID = str(uuid.uuid4())

    metadata = {
        "deleted": False,
        "lastModified":  int(time.time()*1000.0),
        "metadatamodified": False,
        "modified": False,
        "parent": parentUUID,
        "pinned": False,
        "synced": True,
        "type": "CollectionType",
        "version": 1,
        "visibleName": name
    }

    content = {}
    basePath = remarkablePCDirectory + remContent + "/" + UUID

    print("write dir: " + name + " \t" + basePath)
    if not dry:
        with open(basePath + ".content", 'w') as outfile:
            json.dump(content, outfile)
        with open(basePath + ".metadata", 'w') as outfile:
            json.dump(metadata, outfile)
    return UUID


# Creates folder if it doesn't exist
# returns UUID
def cp(rmPdfList, directoryPath, fName, parentUUID, fType, dry):

    candiates = []
    for d in rmPdfList:
        meta = json.loads(open(d + ".metadata").read())
        if meta["parent"] == parentUUID:
            candiates.append(d)

    UUID = ""
    fileExist = False

    for c in candiates:
        meta = json.loads(open(c + ".metadata").read())
        if meta["visibleName"] == fName:
            UUID = os.path.basename(c)
            fileExist = True

    localChanged = True

    basePath = remarkablePCDirectory + remContent + "/" + UUID

    local_annot_mod_time = int(os.path.getmtime(
        syncDirectory + "/" + directoryPath + "/" + fName + "." + fType))

    if fileExist:
        meta = json.loads(open(basePath + ".metadata").read())
        remote_annot_mod_time = int(
            int(meta['lastModified'])/1000)  # rm time is in ms
        # has this version changed since we last exported it?
        localChanged = remote_annot_mod_time < local_annot_mod_time
        if localChanged:
            meta['lastModified'] = local_annot_mod_time*1000
            if not dry:
                with open(basePath + ".metadata", 'w') as outfile:
                    json.dump(meta, outfile)
            print("update file: " + fName)
    else:
        UUID = str(uuid.uuid4())
        basePath = remarkablePCDirectory + remContent + "/" + UUID

        pagesNumber = 0

        if fType == "pdf":
            f = open(syncDirectory + "/" + directoryPath + "/" +
                     fName + "." + fType, "rb")
            input1 = PdfFileReader(f)
            pagesNumber = input1.getNumPages()
            f.close()

        content = {
            "dummyDocument": False,
            "extraMetadata": {},
            "fileType": fType,
            "lastOpenedPage": 0,
            "lineHeight": -1,
            "margins": 180,
            "textScale": 1,
            "pageCount": pagesNumber,
            "transform": {}
        }

        metadata = {
            "deleted": False,
            "lastModified":  local_annot_mod_time*1000,
            "metadatamodified": False,
            "modified": False,
            "parent": parentUUID,
            "pinned": False,
            "synced": True,
            "type": "DocumentType",
            "version": 1,
            "visibleName": fName
        }
        if not dry:
            os.mkdir(basePath)
            os.mkdir(basePath + ".thumbnails")
            os.mkdir(basePath + ".textconversion")
            os.mkdir(basePath + ".highlights")
            os.mkdir(basePath + ".cache")
            with open(basePath + ".content", 'w') as outfile:
                json.dump(content, outfile)
            with open(basePath + ".metadata", 'w') as outfile:
                json.dump(metadata, outfile)
            open(basePath + ".pagedata", 'w')
        print("write file: " + fName + " \t" + basePath)

    if localChanged:  # perform copy

        if not dry:
            shutil.copy(syncDirectory + "/" + directoryPath + "/" +
                        fName + "." + fType, basePath + "." + fType)

    return UUID


if __name__ == "__main__":
    print("main")
    main()
