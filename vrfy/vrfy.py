#!/usr/bin/env python3 
class vrfy:
    import os
    import subprocess
    
    VERSION_STR = "0.3.0"
    
    #options
    GLOBAL_VERBOSITY = None
    CREATE_CSV = "-c"
    VERIFY_CSV = "-v"
    RECURSIVE = "-r"
    VERSION = "-version"
    PRINT = "-p"
    FILE = "-f"
    CHECKSUM = "-cs"
    MERGE = "-merge"
    MASTER_DIR = "-m"
    CLONE_DIR = "-c"
    MERGE_MASTER_TO_CLONE = "-MergeMasterToClone"
    MERGE_CLONE_TO_MASTER = "-MergeCloneToMaster"
    MERGE_MIRRORED = "-MergeMirrored"
    OPTION_RECURSIVE = False
    OPTION_CREATE_CSV = False
    OPTION_VERIFY_CSV = False
    OPTION_VERIFY_VERSION = False
    OPTION_PRINT = False
    OPTION_FILE = -1
    OPTION_CHECKSUM = -1
    OPTION_MASTER_DIR = -1
    OPTION_CLONE_DIR = -1
    OPTION_MERGE = ""
    
    HASH_ERROR = "ERROR"
    LINE_BREAK = "-----------------------------------------"
    CHAPTER_BREAK = "========================================="
    
    
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
            if arguments[index] == self.VERSION:
                self.OPTION_VERIFY_VERSION = True
            if arguments[index] == self.PRINT:
                self.OPTION_PRINT = True
            if arguments[index] == self.CHECKSUM:
                if (len(arguments)-2) <= index + 1: # index + 1 shall be second to last or earlier
                    self.OPTION_CHECKSUM = index + 1
                else:
                    print("Error: Option '" + str(self.CHECKSUM) + "' provided, but '" + str(self.CHECKSUM)+ "' is not followed by checksum to test.")
            if arguments[index] == self.FILE:
                if self.os.path.isfile(arguments[index + 1]):
                    self.OPTION_FILE = index + 1
                else:
                    print("Error: Option '" + str(self.FILE) + "' provided, but '" + str(arguments[index + 1]) + "' is no file.")
            if arguments[index] == self.MASTER_DIR:
                if self.os.path.isdir(arguments[index + 1]):
                    self.OPTION_MASTER_DIR = index + 1
                else:
                    print("Error: Option '" + str(self.MASTER_DIR) + "' provided, but '" + str(arguments[index + 1]) + "' is no directory.")
            if arguments[index] == self.CLONE_DIR:
                if self.os.path.isdir(arguments[index + 1]):
                    self.OPTION_CLONE_DIR = index + 1
                else:
                    print("Error: Option '" + str(self.CLONE_DIR) + "' provided, but '" + str(arguments[index + 1]) + "' is no directory.")
            if arguments[index] == self.MERGE_MASTER_TO_CLONE or arguments[index] == self.MERGE_CLONE_TO_MASTER or arguments[index] == self.MERGE_MIRRORED:
                self.OPTION_MERGE = arguments[index]
        
        executionResult = False
        # cli option: vrfy -version
        if self.OPTION_VERIFY_VERSION == True:
            print("vrfy version: " + str(self.VERSION_STR))
        # cli option: vrfy
        elif len(arguments) == 0:
            # no arguments are provided -> verify checksums of files within current working directory
            import os
            directories.append(os.getcwd())
            self.OPTION_VERIFY_CSV = True
            self.OPTION_RECURSIVE = True
            # verify sums
            print("Verifying current working directory against checksums:")
            executionResult = self.walker(directories[0], directories[0], self.verifySums)
            self.__printResults__(executionResult)
        # cli option: vrfy <<directory>> <<directory>>
        elif (len(arguments) == 2 and self.os.path.isdir(arguments[0]) and self.os.path.isdir(arguments[1])):
            # only two paths are provided -> first: golden master / second: clone/copy to be verified
            print("Verifying directories:")
            print("Master: " + str(arguments[0]))
            print("Clone: " + str(arguments[1]))
            self.OPTION_RECURSIVE = True
            executionResult = self.walker(arguments[0], arguments[1], self.verifyFiles)
            self.__printResults__(executionResult)
        # cli option: vrfy -m <<directory>> -c <<directory>>
        elif self.OPTION_MASTER_DIR >= 0 and self.OPTION_MASTER_DIR <= len(arguments) - 1 and self.OPTION_CLONE_DIR >= 0 and self.OPTION_CLONE_DIR <= len(arguments) - 1:
            print("Verifying directories:")
            print("Master: " + str(arguments[self.OPTION_MASTER_DIR]))
            print("Clone: " + str(arguments[self.OPTION_CLONE_DIR]))
            self.OPTION_RECURSIVE = True
            executionResult = self.walker(arguments[self.OPTION_MASTER_DIR], arguments[self.OPTION_CLONE_DIR], self.verifyFiles)
            self.__printResults__(executionResult)
        # cli option: vrfy -f <<file>> -cs <<CHECKSUM>> OR vrfy -p -f <<file>> OR vrfy -p -f <<file>> -cs <<CHECKSUM>> 
        elif self.OPTION_FILE >= 0 and self.OPTION_FILE <= len(arguments) - 1:
            calcChecksum = self.calcChecksum(arguments[self.OPTION_FILE])
            if self.OPTION_PRINT == True:
                name, extension = self.os.path.splitext(self.os.path.basename(arguments[self.OPTION_FILE]))
                print(str(calcChecksum) + "  " + str(name) + str(extension))
                executionResult = True
            if self.OPTION_CHECKSUM >= 0 and self.OPTION_CHECKSUM <= len(arguments) - 1:
                givenChecksum = arguments[self.OPTION_CHECKSUM]
                if self.os.path.isfile(arguments[self.OPTION_CHECKSUM]):
                    try:
                        path, filename = self.os.path.split(arguments[self.OPTION_FILE])
                        sumsDict = self.getChecksumsFromFile(arguments[self.OPTION_CHECKSUM])
                        givenChecksum = sumsDict[filename]
                    except:
                        givenChecksum = ""
                        executionResult = False
                        print("Error: Option '" + str(self.CHECKSUM) + "' provided, but no checksum found in file" + str(arguments[self.OPTION_CHECKSUM]) + ".")
                if calcChecksum == givenChecksum:
                    executionResult = True
                else:
                    executionResult = False
                self.__printResults__(executionResult)
        # cli option: vrfy -c <<directory>>
        elif self.OPTION_CREATE_CSV == True:
            if len(directories) == 1:
                # create sums
                print("Creating checksums for files:")
                executionResult = self.walker(directories[0], directories[0], self.createSums)
                self.__printResults__(executionResult)
            else:
                print("Error: Option '" + str(self.VERIFY_CSV) + "' provided, but '" + str(len(directories)) + "' directories are given (required: 1).")
        # cli option: vrfy -v <<directory>>
        elif self.OPTION_VERIFY_CSV == True:
            if len(directories) == 1:
                # verify sums
                print("Verifying files against checksums:")
                executionResult = self.walker(directories[0], directories[0], self.verifySums)
                self.__printResults__(executionResult)
            else:
                print("Error: Option '" + str(self.VERIFY_CSV) + "' provided, but '" + str(len(directories)) + "' directories are given (required: 1).")
        else:
            print("No valid argument setting found!")
            return 1
        if executionResult == True:
            return 0
        else:
            return 1
    
    def __printResults__(self, res):
        if res:
            print("Overall: PASS")
        else:
            print("Overall: FAIL")
    
    
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
        try:
            with open(filePath, 'rb') as file:
                while True:
                    block = file.read(8192)
                    if not block:
                        break
                    sha256_hash.update(block)
        except:
            #print("ERROR: Unable to calculate SHA256 hash.")
            return self.HASH_ERROR
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
        # start file verification, when files are included in directory
        if len(filesMaster) > 0:
            # print current working directory
            if self.OPTION_PRINT == True:
                print(str(pathMaster) + " : ")
            else:
                print(str(pathMaster), end=" : ", flush=True)
                
            # search for missing or additional files in master and clone, and trigger error condition
            missingItemsInPathClone = [i for i in filesMaster if i not in filesClone]
            additionalItemsInPathClone = [i for i in filesClone if i not in filesMaster]
            if len(missingItemsInPathClone) != 0:
                result = False
            if len(additionalItemsInPathClone) != 0:
                result = False
                
            # iterate through all files of master directory and verify their checksums to those of the clone directory 
            checksumErrors = []
            for fileNameMaster in filesMaster:
                # master file is not included on clone directory -> trigger error condition
                if fileNameMaster not in filesClone:
                    result = False
                else:
                    # calculate checksums for master and clone file
                    masterFilePath = self.os.path.join(pathMaster, fileNameMaster)
                    cloneFilePath = self.os.path.join(pathClone, fileNameMaster)
                    checksumMaster = self.calcChecksum(masterFilePath)
                    checksumClone = self.calcChecksum(cloneFilePath)
                    # print checksums if requested by user
                    if self.OPTION_PRINT == True:
                        print("File: " + fileNameMaster)
                        print("Master: " + checksumMaster)
                        print("Clone: " + checksumClone)
                    # verify that both match and both are NOT "HASH_ERROR"
                    if checksumClone == checksumMaster and (checksumMaster != self.HASH_ERROR):
                        if self.OPTION_PRINT == True:
                            print("Check: PASS")
                            print(self.LINE_BREAK)
                    else:
                        # checksum mismatch -> trigger error condition and add file name to list of mismatched files
                        if self.OPTION_PRINT == True:
                            print("Check: FAIL")
                            print(self.LINE_BREAK)
                        checksumErrors.append(str(fileNameMaster))
                        result = False
            
            if self.OPTION_PRINT == True:
                print("" + str(pathMaster), end=" : ", flush=True)
            # append result to printed working directory
            if result == True:
                print("PASS")
            else:
                print("FAILED!!!")
            # print failed items
            for file in checksumErrors:
                print("[MISMATCH] " + str(file))
            for file in missingItemsInPathClone:
                print("[+] " + str(file))
            for file in additionalItemsInPathClone:
                print("[-] " + str(file))
            if self.OPTION_PRINT == True:
                print(self.CHAPTER_BREAK)
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
        result = True
        if len(filesMaster) > 0:
            # print current working directory
            print("" + str(pathMaster), end=" : ", flush=True)
            try:
                f = open(self.os.path.join(pathMaster, "sums.csv"), "w")
                # do not hash "sums.csv" itself
                if "sums.csv" in filesMaster:
                    filesMaster.remove("sums.csv")
                # iterate through all files of current directory and add their names and checksums to "sums.csv"
                for file in filesMaster:
                    hash_digest = str(self.calcChecksum(self.os.path.join(pathMaster, file)))
                    # only add files without checksum errors and trigger error condition, when checksum calculation failed
                    if hash_digest != self.HASH_ERROR: 
                        f.write(str(file) + ";" + str(hash_digest) + "\n")
                    else:
                        result = False
                f.close()
                print("PASS")
            except:
                print("FAILED!!!")
                return False 
        return result


    def getChecksumsFromFile(self, filePathName):
        """
        Reads and decodes checksums from file and returns a filename / hash digest dictionary.
        Note: To be used, when undefined whether *.sha256sum or sums.csv was provided by user.

        Parameters:
            filePathName (str): Path + file name to directory where *.sha256sum/sums.csv-file is located.
        
        Returns:
            dict:   dict[filename] = hash digest.
        """
        path, filename = self.os.path.split(filePathName)
        name, extension = self.os.path.splitext(self.os.path.basename(filePathName))
        if extension == ".sha256sum":
            return self.readSha256SumFile(path, filename)
        elif filename == "sums.csv":
            return self.readSumsCsvFile(path)
        else:
            return dict()
    
    
    def readSha256SumFile(self, filePath, fileName):
        """
        Reads and decodes *.sha256sum-files and returns a filename / hash digest dictionary.

        Parameters:
            filePath (str): Path to directory where *.sha256sum-file is located.
            fileName (str): Name of *.sha256sum-file with file extension.
        
        Returns:
            dict:   dict[filename] = hash digest.
        """
        sumsDict = dict()
        # read and decode sums.csv into dictionary sumsDict[<<fileName>>] = <<hash digest>>
        try:
            f = open(self.os.path.join(filePath, fileName), "r")
            for line in f.readlines():
                entry = line.replace("\n","").split("  ")
                sumsDict[entry[1]] = entry[0] 
            f.close()
        except:
            # except file errors, and close verification with FAIL (i.e. "False" result)
            print("\n>>> ERROR: No *.sha256sum-file found!")
        return sumsDict 
    
    
    def readSumsCsvFile(self, filePath):
        """
        Reads and decodes sums.csv-files and returns a filename / hash digest dictionary.

        Parameters:
            filePath (str): Path to directory where sums.csv-file is located.
        
        Returns:
            dict:   dict[filename] = hash digest.
        """
        # read and decode sums.csv into dictionary sumsDict[<<fileName>>] = <<hash digest>>
        sumsDict = dict()
        try:
            f = open(self.os.path.join(filePath, "sums.csv"), "r") 
            for line in f.readlines():
                entry = line.replace("\n","").split(";")
                # compatibility layer for legacy sums.csv, where hash digest started with "b'" and ended with "'"
                if entry[1][:2] == "b'" and entry[1][-1] == "'":
                    entry[1] = entry[1][2:-1]
                sumsDict[entry[0]] = entry[1] 
            f.close()
        except:
            # except file errors, and close verification with FAIL (i.e. "False" result)
            print("\n>>> ERROR: No sums.csv found!")
            return False
        return sumsDict
        
        
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
            # print current working directory without line ending
            if self.OPTION_PRINT == True:
                print(str(pathMaster) + " : ")
            else:
                print(str(pathMaster), end=" : ", flush=True)
            
            # do not try to verify "sums.csv" as it will not be included in "sums.csv"
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")
            
            # read checksum file and get dictionary
            sumsDict = self.readSumsCsvFile(pathMaster) 
            
            resultVerify = True
            
            # verify that all files in current working directory are included in sums.csv, and vice versa
            # trigger error condition if check failed
            missingItemsInSumsCSV = [i for i in filesMaster if i not in sumsDict.keys()]
            additionalItemsInSumsCSV = [i for i in sumsDict.keys() if i not in filesMaster]
            if len(missingItemsInSumsCSV) != 0:
                resultVerify = False
            if len(additionalItemsInSumsCSV) != 0:
                resultVerify = False
                
            checksumErrors = []
            # iterate through all files and compare their checksum with those stored in sums.csv
            for file in sumsDict.keys():
                checksumCalc = str(self.calcChecksum(self.os.path.join(pathMaster, file)))
                checksumSaved = sumsDict[file]
                # print checksums if requested by user
                if self.OPTION_PRINT == True:
                    print("File: " + file)
                    print("Calculated: " + checksumCalc)
                    print("Saved: " + checksumSaved)
                # verify calculated checksum against the one stored in sums.csv
                if checksumCalc != checksumSaved:
                    # checksum mismatch -> trigger error condition and add file name to list of mismatched files
                    checksumErrors.append(file)
                    resultVerify = False
                    if self.OPTION_PRINT == True:
                        print("Check: FAIL")
                        print(self.LINE_BREAK)
                elif checksumCalc == checksumSaved:
                    if self.OPTION_PRINT == True:
                        print("Check: PASS")
                        print(self.LINE_BREAK)
                else:
                    # shall never be executed
                    resultVerify = False
                    print("EXECUTION ERROR")
                    import sys
                    sys.exit(1)
             
            if self.OPTION_PRINT == True:
                print("" + str(pathMaster), end=" : ", flush=True)
            # append result to printed working directory
            if resultVerify == True:
                print("PASS")
            else:
                print("FAILED!!!")    
            # print failed items
            for file in checksumErrors:
                print("[MISMATCH] " + str(file))
            for file in missingItemsInSumsCSV:
                print("[+] " + str(file))
            for file in additionalItemsInSumsCSV:
                print("[-] " + str(file))
            
            if self.OPTION_PRINT == True:
                print(self.CHAPTER_BREAK)
                
            return resultVerify
        
        # return with True, in case no files needed to be verifed
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
            filesM = [entryA for entryA in self.os.listdir(pathMaster) if not self.os.path.isdir(self.os.path.join(pathMaster, entryA))]
            filesC = [entryB for entryB in self.os.listdir(pathClone) if not self.os.path.isdir(self.os.path.join(pathClone, entryB))]
            dictsM = [entryDir for entryDir in self.os.listdir(pathMaster) if self.os.path.isdir(self.os.path.join(pathMaster, entryDir))]
            
            # execute requested operation
            resultVerify = func(pathMaster, filesM, pathClone, filesC)  
            
            # jump into child directories, if recursive operation is requested
            if self.OPTION_RECURSIVE == True:
                for nextFolder in dictsM:
                    resultVerify = self.walker(self.os.path.join(pathMaster, nextFolder), self.os.path.join(pathClone, nextFolder), func) & resultVerify
            
            return resultVerify
        else:
            # terminate, since paths are not pointing to valid directories
            return False


def main():
    import sys
    verify = vrfy()
    sys.exit(verify.parseArgumentsAndExecute(sys.argv[1:]))

if __name__ == "__main__":
    main()
  
            
