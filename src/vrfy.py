#!/usr/bin/env python3 
class vrfy:
    import os
    import subprocess
    
    GLOBAL_VERBOSITY = None
    CREATE_CSV = "-c"
    VERIFY_CSV = "-v"
    RECURSIVE = "-r"
    OPTION_RECURSIVE = False
    OPTION_CREATE_CSV = False
    OPTION_VERIFY_CSV = False
    
    def __init__(self):
        pass
        
    def parseArgumentsAndExecute(self, arguments):
        """
        Decodes programm arguments and executes required methods.
    
        Parameters:
            arguments (List[str]): List of arguments provided by user.
        
        Returns:
            int:    0, when all execution steps resulted in PASS, else 1.
        """
        # find options
        directories = []
        for index in range(0, len(arguments)):
            if arguments[index] == self.RECURSIVE:
                self.OPTION_RECURSIVE = True 
            if arguments[index] == self.CREATE_CSV:
                self.OPTION_CREATE_CSV = True
            if arguments[index] == self.VERIFY_CSV:
                self.OPTION_VERIFY_CSV = True
            if self.os.path.isdir(arguments[index]):
                directories.append(arguments[index])
        
        executionResult = False
        if len(arguments) == 0:
            # no arguments are provided -> verify checksums of files within current working directory
            import os
            directories.append(os.getcwd())
            self.OPTION_VERIFY_CSV = True
            self.OPTION_RECURSIVE = True
        if len(arguments) == 2 and self.os.path.isdir(arguments[0]) and self.os.path.isdir(arguments[1]):
            # only two paths are provided -> first: golden master / second: clone/copy to be verified
            print("Validating directories:")
            print("Master: " + str(arguments[0]))
            print("Clone: " + str(arguments[1]))
            self.OPTION_RECURSIVE = True
            executionResult = self.walker(arguments[0], arguments[1], self.verifyFiles)
            self.__printResults__(executionResult)
        else:        
            if self.OPTION_CREATE_CSV == True and len(directories) == 1:
                # create sums
                print("Creating checksums for files:")
                executionResult = self.walker(directories[0], directories[0], self.createSums)
                self.__printResults__(executionResult)
            elif self.OPTION_VERIFY_CSV == True and len(directories) == 1:
                # verify sums
                print("Verifying files against checksums:")
                executionResult = self.walker(directories[0], directories[0], self.verifySums)
                self.__printResults__(executionResult)
            else:
                print("No valid argument setting found!")
                return 1
        if executionResult == True:
            return 0
        else:
            return 1
    
    def __printResults__(self, res):
        if res:
            print("+++++++++++++++")
            print("++++ PASS! ++++")
            print("+++++++++++++++")
        else:
            print("++++++++++++++++++++++++++++")
            print("XXXXX     FAIL!!!!     XXXXX")
            print("++++++++++++++++++++++++++++")
        
    def calcChecksum(self, filePath):
        """
        Calculates and returns file hash for >>filePath<<.

        Parameters:
            filePath (str): Path and name of the file that shall get hashed. 
        
        Returns:
            str: Hash digest.
        """
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(filePath, 'rb') as file:
            while True:
                block = file.read(8192)
                if not block:
                    break
                sha256_hash.update(block)
        return sha256_hash.hexdigest()

    def verifyFiles(self, pathMaster, filesMaster, pathClone, filesClone):
        """
        Verifies the contents of directory "pathMaster" against the contents of "pathClone" based on the respective file checksums.
    
        Parameters:
            pathMaster (str): Path to the master directory whose contents are considered valid and unchanged, serving as a baseline for comparison.
            filesMaster (List[str]): Names of all files that are included in the directory >>pathMaster<<.
            pathClone (str): Path to clone directory whose files shall get verified against the master copy.
            filesClone (List[str]): Names of all files that are included in the directory >>pathClone<<.
        
        Returns:
            bool:   True, when contents of directory "pathMaster" are verified successfully against "pathClone".
                    False, when at least one file mismatches.
        """
        result = True
        if len(filesMaster) > 0:
            print("" + str(pathMaster), end=" : ", flush=True)
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
        """
        Creates file sums.csv with checksums for files [filesMaster] in >>pathMaster<<.
        
        Parameters:
            pathMaster (str): Path to directory whose files shall get hashed and checksums stored in sums.csv.
            filesMaster (List[str]): Names of all files that are included in the directory >>pathMaster<<.
            pathClone (str): NOT USED! Included for compatibility reasons only.
            filesClone (List[str]): NOT USED! Included for compatibility reasons only.
        
        Returns:
            bool:   True, when file sums.csv is created successfully, else False.
        """
        #create sums.csv, if directory contains files
        if len(filesMaster) > 0:
            print("" + str(pathMaster), end=" : ", flush=True)
            try:
                f = open(pathMaster + "/sums.csv", "w")
                if "sums.csv" in filesMaster:
                    filesMaster.remove("sums.csv")
                for file in filesMaster:
                    f.write(str(file) + ";" + str(self.calcChecksum(str(pathMaster) + "/" + str(file))) + "\n")
                f.close()
                print("PASS")
            except:
                print("FAILED!!!")
                return False 
        return True
        
    def verifySums(self, pathMaster, filesMaster, pathClone, filesClone):
        """
        Verifies the contents of directory "pathMaster" against the included checksums in sums.csv.

        Parameters:
            pathMaster (str): Path to directory whose files shall get verified.
            filesMaster (List[str]): Names of all files that are included in the directory >>pathMaster<<.
            pathClone (str): NOT USED! Included for compatibility reasons only.
            filesClone (List[str]): NOT USED! Included for compatibility reasons only.
        
        Returns:
            bool:   True, when contents of directory are verified successfully against sums.csv, else False.
        """
        if len(filesMaster) > 0:
            print("" + str(pathMaster), end=" : ", flush=True)
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")
        
            f = open(pathMaster + "/sums.csv", "r")
            sumsDict = dict() 
            for line in f.readlines():
                entry = line.replace("\n","").split(";")
                # compatibility layer for legacy sums.csv, where hash digest started with "b'" and ended with "'"
                if entry[1][:2] == "b'" and entry[1][-1] == "'":
                    entry[1] = entry[1][2:-1]
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
        """
        Verifies the contents of directory "pathMaster" against the included checksums in sums.csv.

        Parameters:
            pathMaster (str): Path to the master directory whose contents are considered valid and unchanged, serving as a baseline for comparison. .
            pathClone (str): Path to clone directory whose files shall get verified against the master copy.
            func (callable) -- Function that gets executed on the respective folder.
        
        Returns:
            bool:   True, when all executions of >>func<< returned PASS, else False.
        """
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
verify = vrfy()
sys.exit(verify.parseArgumentsAndExecute(sys.argv[1:]))

  
            
