#!/usr/bin/env python3 
class vrfy:
    import os
    import subprocess
    
    GLOBAL_VERBOSITY = None
    CREATE_CSV = "-c"
    VERIFY_CSV = "-v"
    RECURSIVE = "-r"
    OPTION_RECURSIVE = False
    
    def __init__(self, arguments):
        # decode arguments
        # find options
        for index in range(0, len(arguments)):
            if arguments[index] == self.RECURSIVE:
                self.OPTION_RECURSIVE = True                   
        
        if len(arguments) >= 3 and self.os.path.isdir(arguments[1]) and self.os.path.isdir(arguments[2]):
            # only two path are given: verify paths
            print("Validating directories:")
            print("Master: " + str(arguments[1]))
            print("Clone: " + str(arguments[1]))
            self.OPTION_RECURSIVE = True
            self.printResults(self.walker(arguments[1], arguments[2], self.verifyFiles))
        else:        
            for index in range(0, len(arguments)):
                if arguments[index] == self.CREATE_CSV and self.os.path.isdir(arguments[index + 1]) and len(arguments) > (index + 1):
                    # create sums
                    print("Creating checksums for files:")
                    self.printResults(self.walker(arguments[index + 1], arguments[index + 1], self.createSums))
                if arguments[index] == self.VERIFY_CSV and self.os.path.isdir(arguments[index + 1]) and len(arguments) > (index + 1):
                    # verify sums
                    print("Verifying files against checksums:")
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
             
    def calcChecksum(self, filePath):
        # execute command sha256sum for given file
        cmd = "sha256sum " + "'" + str(filePath) + "'"
        return self.subprocess.check_output(cmd, stderr=self.subprocess.STDOUT,shell=True).split()[0]

    def verifyFiles(self, pathMaster, filesMaster, pathClone, filesClone):
        result = True
        if len(filesMaster) > 0:
            print("" + str(result), end=" : ", flush=True)
            for fileNameMaster in filesMaster:
                if fileNameMaster not in filesClone:
                    print("\nERROR: File " + str(fileNameMaster) + "not found in clone!", end=" : ", flush=True) 
                    result = False
                else:
                    checksumMaster = self.calcChecksum(str(pathMaster) + "/" + str(fileNameMaster))
                    checksumClone = self.calcChecksum(str(pathClone) + "/" + str(fileNameMaster))
                    if checksumClone == checksumMaster:
                        pass
                    else:
                        print("\nMismatch of file " + str(fileNameMaster) + " detected!", end=" : ", flush=True)
                        result = False
            if result == True:
                print("PASS")
            else:
                print("FAILED!!!")
        return result  

    def createSums(self, pathMaster, filesMaster, pathClone, filesClone):
        #create sums.csv, if directory contains files
        if len(filesMaster) > 0:
            print("" + str(pathMaster), end=" : ", flush=True)
            f = open(pathMaster + "/sums.csv", "w")
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")
            for file in filesMaster:
                f.write(str(file) + ";" + str(self.calcChecksum(str(pathMaster) + "/" + str(file))) + "\n")
            f.close()
            print("DONE")
        return True
        
    def verifySums(self, pathMaster, filesMaster, pathClone, filesClone):
        if len(filesMaster) > 0:
            print("" + str(pathMaster), end=" : ", flush=True)
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")
        
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
                    print("\n>>> File missing in sums.csv: " + item, end="", flush=True)
                resultVerify = False
            if len(additionalItemsInSumsCSV) != 0:
                for item in additionalItemsInSumsCSV:
                    print("\n>>> File missing in directory but in sums.csv: " + item, end="", flush=True)
                resultVerify = False
                
            for file in filesMaster:
                checksumCalc = str(self.calcChecksum(str(pathMaster) + "/" + str(file)))
                checksumSaved = sumsDict[file]
                if checksumCalc != checksumSaved:
                    resultVerify = False
                    print("\n>>> File mismatch: " + file + " == Saved: " + checksumSaved + " / Calc: " + checksumCalc, end="", flush=True)
                elif checksumCalc == checksumSaved:
                    pass
                else:
                    resultVerify = False
                    print("EXECUTION ERROR")
                    exit(1)
            
            if resultVerify == True:
                print("PASS")
            else:
                print("Verified files at path: " + str(pathMaster) + " : FAILED!!!")
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

import sys
verify = vrfy(sys.argv)

  
            
