#!/usr/bin/env python3 
class vrfy:
    import os
    import subprocess
    
    GLOBAL_VERBOSITY = None
    CREATE_CSV = "-c"
    VERIFY_CSV = "-v"
    RECURSIVE = "-r"
    VERBOSE = "-verbose"
    OPTION_RECURSIVE = False
    OPTION_VERBOSE = None
    
    def __init__(self, arguments):
        # decode arguments
        # find options
        for index in range(0, len(arguments)):
            if arguments[index] == self.RECURSIVE:
                self.OPTION_RECURSIVE = True
                print("Option: recursive - " + str(self.OPTION_RECURSIVE))
            if arguments[index] == self.VERBOSE:
                if len(arguments) > (index + 1):
                    if arguments[index + 1] == "None":
                        self.OPTION_VERBOSE = "None"
                    elif arguments[index + 1] == "MEDIUM":
                        self.OPTION_VERBOSE = "MEDIUM"
                    else:
                        self.OPTION_VERBOSE = "ALL"
                else:
                    self.OPTION_VERBOSE = "ALL"
                    
        
        if len(arguments) >= 3 and self.os.path.isdir(arguments[1]) and self.os.path.isdir(arguments[2]):
            # only two path are given: verify paths
            print("Verify paths:")
            self.OPTION_RECURSIVE = True
            self.OPTION_VERBOSE = "MEDIUM"
            self.printResults(self.walker(arguments[1], arguments[2], self.verifyFiles))
        else:        
            for index in range(0, len(arguments)):
                if arguments[index] == self.CREATE_CSV and self.os.path.isdir(arguments[index + 1]) and len(arguments) > (index + 1):
                    # create sums
                    self.printResults(self.walker(arguments[index + 1], arguments[index + 1], self.createSums))
                if arguments[index] == self.VERIFY_CSV and self.os.path.isdir(arguments[index + 1]) and len(arguments) > (index + 1):
                    # verify sums
                    print("Verify sums:")
                    self.printResults(self.walker(arguments[index + 1], arguments[index + 1], self.verifySums))
    
    def printResults(self, res):
        if res:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("++++ PASS! ++++")
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        else:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("                   XXXXX     FAIL!!!!     XXXXX")
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            
    def vprint(self, message, level = None):
        if self.OPTION_VERBOSE == "ALL":
            print(message)
        elif self.OPTION_VERBOSE == "MEDIUM" and (level == "HIGH" or level == "MEDIUM"):
            print(message)
        else:
            if level == "HIGH":
                print(message)
 
    def calcChecksum(self, filePath):
        # execute command sha256sum for given file
        cmd = "sha256sum " + "'" + str(filePath) + "'"
        return self.subprocess.check_output(cmd, stderr=self.subprocess.STDOUT,shell=True).split()[0]

    def verifyFiles(self, pathMaster, filesMaster, pathClone, filesClone):
        result = True
        if len(filesMaster) > 0:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("Path : " + pathMaster)
            for fileNameMaster in filesMaster:
                if fileNameMaster not in filesClone:
                    self.vprint("ERROR: File " + str(fileNameMaster) + "not found in clone!", "HIGH") 
                    result = False
                else:
                    checksumMaster = self.calcChecksum(str(pathMaster) + "/" + str(fileNameMaster))
                    checksumClone = self.calcChecksum(str(pathClone) + "/" + str(fileNameMaster))
                    if checksumClone == checksumMaster:
                        self.vprint("File " + str(fileNameMaster) + ": PASS!")
                    else:
                        self.vprint("File " + str(fileNameMaster) + ": +++FAILED+++", "MEDIUM")
                        result = False
            self.vprint("Sucessfully verified path: " + str(result), "MEDIUM")
        return result  

    def createSums(self, pathMaster, filesMaster, pathClone, filesClone):
        #create sums.csv
        if len(filesMaster) > 0:
            print("Path : " + pathMaster)
            f = open(pathMaster + "/sums.csv", "w")
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")
            for file in filesMaster:
                f.write(str(file) + ";" + str(self.calcChecksum(str(pathMaster) + "/" + str(file))) + "\n")
            f.close()
            self.vprint("Created sums.csv for path: " + str(pathMaster), "MEDIUM")
        return True
        
    def verifySums(self, pathMaster, filesMaster, pathClone, filesClone):
        if len(filesMaster) > 0:
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")
                
            print("Path : " + pathMaster)
            f = open(pathMaster + "/sums.csv", "r")
            sumsDict = dict() 
            for line in f.readlines():
                entry = line.replace("\n","").split(";")
                sumsDict[entry[0]] = entry[1] 
            f.close()
            
            resultVerify = True
            
            missingItemsInSumsCSV = [i for i in filesMaster if i not in sumsDict.keys()]
            additionalItemsInSumsCSV = [i for i in sumsDict.keys() if i not in filesMaster]
            if len(missingItemsInSumsCSV) != 0:
                for item in missingItemsInSumsCSV:
                    print(">>> File missing in sums.csv: " + item)
                resultVerify = False
            if len(additionalItemsInSumsCSV) != 0:
                for item in additionalItemsInSumsCSV:
                    print(">>> File missing in directory but in sums.csv: " + item)
                resultVerify = False
                
            for file in filesMaster:
                checksumCalc = str(self.calcChecksum(str(pathMaster) + "/" + str(file)))
                checksumSaved = sumsDict[file]
                if checksumCalc != checksumSaved:
                    resultVerify = False
                    print(">>> File mismatch: " + file + " == Saved: " + checksumSaved + " / Calc: " + checksumCalc)
                elif checksumCalc == checksumSaved:
                    self.vprint(">>> File check: " + file + " :: PASS", "LOW")
                else:
                    resultVerify = False
                    print("EXECUTION ERROR")
                    exit(1)
            
            self.vprint("Sucessfully verified path: " + str(resultVerify), "MEDIUM")
            return resultVerify
        return True

    def walker(self, pathMaster, pathClone, func):
        # check if received strings are valid paths
        if self.os.path.isdir(pathMaster) and self.os.path.isdir(pathClone):
            # create lists of files and directories that are included in current path
            filesM = [entryA for entryA in self.os.listdir(pathMaster) if not self.os.path.isdir(pathMaster + "/" + entryA)]
            filesC = [entryB for entryB in self.os.listdir(pathClone) if not self.os.path.isdir(pathClone + "/" + entryB)]
            dictsM = [entryDir for entryDir in self.os.listdir(pathMaster) if self.os.path.isdir(pathMaster + "/" + entryDir)]
            
            # execute requested operation
            resultVerify = func(pathMaster, filesM, pathClone, filesC)  
            
            # jump into child directories
            if self.OPTION_RECURSIVE == True:
                for nextFolder in dictsM:
                    resultVerify = self.walker(pathMaster + "/" + nextFolder, pathClone + "/" + nextFolder, func) & resultVerify
            
            return resultVerify
        else:
            # terminate, since paths are not pointing to valid directories
            return False

    def walkFolder(pathMaster, pathClone):
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Verifing directory: " + str(pathMaster))
        if self.os.path.isdir(pathMaster) and self.os.path.isdir(pathClone):
            filesM = [entryA for entryA in self.os.listdir(pathMaster) if not self.os.path.isdir(pathMaster + "/" + entryA)]
            dictsM = [entryDir for entryDir in self.os.listdir(pathMaster) if self.os.path.isdir(pathMaster + "/" + entryDir)]
            filesC = [entryB for entryB in self.os.listdir(pathClone) if not self.os.path.isdir(pathClone + "/" + entryB)]
            
            resultFileNo = True
            if len(filesM) != len(filesC):
                print("ERROR! Mismatch in file numbers!")
                print("No. Master files: " + str(len(filesM)))
                print("No. Clone files: " + str(len(filesC)))
                resultFileNo = False
                
            if len(dictsM) > 0:
                print("Additional directories found: " + str(dictsM))
                
            print("----------------------------------------------------------------------------------------------------")
            
            resultVerify = True
            if len(filesM) > 0:
                resultVerify = verifyFiles(pathMaster, filesM, pathClone, filesC)
                if resultVerify == True:
                    print(" +++ PASS +++")
                else:
                    print(" XXX FAIL XXX ")
            
            resultWalk = True
            for nextFolder in dictsM:
                resultWalk = walkFolder(pathMaster + "/" + nextFolder, pathClone + "/" + nextFolder) & resultWalk
            
            return resultVerify & resultWalk & resultFileNo
            
        else:
            print("Folder does not exist: " + str(pathClone))
            return False


import sys
verify = vrfy(sys.argv)

  
            
