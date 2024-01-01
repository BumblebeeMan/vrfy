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
                self.OPTION_CHECKSUM = index + 1
            if arguments[index] == self.FILE:
                self.OPTION_FILE = index + 1
            if arguments[index] == self.MASTER_DIR:
                self.OPTION_MASTER_DIR = index + 1
            if arguments[index] == self.CLONE_DIR:
                self.OPTION_CLONE_DIR = index + 1
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
        # cli option: vrfy -p <<file>>
        elif (len(arguments) == 2 and self.OPTION_PRINT == True and (self.os.path.isfile(arguments[0]) or self.os.path.isfile(arguments[1]))) or (len(arguments) == 1 and self.os.path.isfile(arguments[0])):
            if self.os.path.isfile(arguments[0]):
                print(self.calcChecksum(arguments[0]))
            else:
                print(self.calcChecksum(arguments[1]))
        # cli option: vrfy <<directory>> <<directory>>
        elif len(arguments) == 2 and self.os.path.isdir(arguments[0]) and self.os.path.isdir(arguments[1]):
            # only two paths are provided -> first: golden master / second: clone/copy to be verified
            print("Validating directories:")
            print("Master: " + str(arguments[0]))
            print("Clone: " + str(arguments[1]))
            self.OPTION_RECURSIVE = True
            executionResult = self.walker(arguments[0], arguments[1], self.verifyFiles)
            self.__printResults__(executionResult)
        # cli option: vrfy -f <<file>> -cs <<CHECKSUM>>
        elif len(arguments) == 4 and (self.OPTION_CHECKSUM > -1 and self.OPTION_CHECKSUM <= 4) and (self.OPTION_FILE > -1 and self.OPTION_FILE <= 4):
            if self.os.path.isfile(arguments[self.OPTION_FILE]):
                calcChecksum = self.calcChecksum(arguments[self.OPTION_FILE])
                if calcChecksum == arguments[self.OPTION_CHECKSUM]:
                    executionResult = True
                else:
                    executionResult = False
            self.__printResults__(executionResult)
        # cli option: vrfy -c <<directory>>
        elif self.OPTION_CREATE_CSV == True and len(directories) == 1:
            # create sums
            print("Creating checksums for files:")
            executionResult = self.walker(directories[0], directories[0], self.createSums)
            self.__printResults__(executionResult)
        # cli option: vrfy -v <<directory>>
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
        if len(filesMaster) > 0:
            print("" + str(pathMaster), end=" : ", flush=True)
            checksumErrors = []
            missingItemsInPathClone = [i for i in filesMaster if i not in filesClone]
            additionalItemsInPathClone = [i for i in filesClone if i not in filesMaster]
            for fileNameMaster in filesMaster:
                if fileNameMaster not in filesClone:
                    result = False
                else:
                    checksumMaster = self.calcChecksum(str(pathMaster) + "/" + str(fileNameMaster))
                    checksumClone = self.calcChecksum(str(pathClone) + "/" + str(fileNameMaster))
                    if checksumClone == checksumMaster and (checksumMaster != self.HASH_ERROR):
                        pass
                    else:
                        checksumErrors.append(str(fileNameMaster))
                        result = False
            if result == True:
                print("PASS")
            else:
                print("FAILED!!!")
            # print results
            for file in checksumErrors:
                print("[MISMATCH] " + str(file))
            for file in missingItemsInPathClone:
                print("[+] " + str(file))
            for file in additionalItemsInPathClone:
                print("[-] " + str(file))
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
            print("" + str(pathMaster), end=" : ", flush=True)
            try:
                f = open(pathMaster + "/sums.csv", "w")
                if "sums.csv" in filesMaster:
                    filesMaster.remove("sums.csv")
                for file in filesMaster:
                    hash_digest = str(self.calcChecksum(str(pathMaster) + "/" + str(file)))
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
            print("" + str(pathMaster), end=" : ", flush=True)
            
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")
            
            # read and decode sums.csv into dictionary sumsDict[<<fileName>>] = <<hash digest>>
            try:
                f = open(pathMaster + "/sums.csv", "r")
                sumsDict = dict() 
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
            
            resultVerify = True
            
            # verify that all files in directory are included in sums.csv,and vice versa
            checksumErrors = []
            missingItemsInSumsCSV = [i for i in filesMaster if i not in sumsDict.keys()]
            additionalItemsInSumsCSV = [i for i in sumsDict.keys() if i not in filesMaster]
            if len(missingItemsInSumsCSV) != 0:
                resultVerify = False
            if len(additionalItemsInSumsCSV) != 0:
                resultVerify = False
                
            # iterate through all files and compare their checksum with those stored in sums.csv
            for file in sumsDict.keys():
                checksumCalc = str(self.calcChecksum(str(pathMaster) + "/" + str(file)))
                checksumSaved = sumsDict[file]
                if checksumCalc != checksumSaved:
                    checksumErrors.append(file)
                    resultVerify = False
                    #print("\n>>> File mismatch: " + file + " == Saved: " + checksumSaved + " / Calc: " + checksumCalc, end=" ", flush=True)
                elif checksumCalc == checksumSaved:
                    pass
                else:
                    # shall never be executed
                    resultVerify = False
                    print("EXECUTION ERROR")
                    import sys
                    sys.exit(1)
            
            # append result to printed working directory
            if resultVerify == True:
                print("PASS")
            else:
                print("FAILED!!!")
                
            # print results
            for file in checksumErrors:
                print("[MISMATCH] " + str(file))
            for file in missingItemsInSumsCSV:
                print("[+] " + str(file))
            for file in additionalItemsInSumsCSV:
                print("[-] " + str(file))
                
            return resultVerify
        
        # return with True, in case no files are needed to be verifed
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
            
            # jump into child directories, if recursive operation is requested
            if self.OPTION_RECURSIVE == True:
                for nextFolder in dictsM:
                    resultVerify = self.walker(pathMaster + "/" + nextFolder, pathClone + "/" + nextFolder, func) & resultVerify
            
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
  
            
