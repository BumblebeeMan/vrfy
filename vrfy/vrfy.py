#!/usr/bin/env python3
class vrfy:
    class Result:
        def __init__(self, result, path, missingMaster = [], missingClone = [], additionalMaster = [], additionalClone = [], ChecksumMismatch = []):
            self.Result = result
            self.Path = path
            self.MissingInMaster = missingMaster
            self.MissingInClone = missingClone
            self.AdditionalInMaster = additionalMaster
            self.AdditionalInClone = additionalClone
            self.ChecksumMismatch = ChecksumMismatch

    import os
    import subprocess

    VERSION_STR = "0.4.x"
    HASH_ERROR = "ERROR"

    def __init__(self):
        pass

    def GetVersion(self):
        return self.VERSION_STR

    def VerifyFile(self, filePath, expectedChecksum=""):
        executionResult = False
        expectation = expectedChecksum
        calcChecksum = self.__calcChecksum__(filePath)
        # no hex checksum provided, read sums.csv / *.sha256sums-file
        if self.os.path.isfile(expectedChecksum):
            try:
                path, filename = self.os.path.split(filePath)
                sumsDict = self.__getChecksumsFromFile__(expectedChecksum)
                expectation = sumsDict[filename]
            except:
                #expectation = ""
                executionResult = False
        if calcChecksum == expectation:
            return (True, calcChecksum)
        else:
            return (False, calcChecksum)

    def VerifyFilesAgainstChecksums(self, pathMaster, filesMaster, pathClone = [], filesClone = []):
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
        # check if checksum file is available, if not abort execution
        if "sums.csv" not in filesMaster and len(filesMaster) > 0:
            return self.Result(result=False, path=pathMaster, additionalMaster=filesMaster)

        if len(filesMaster) > 0:
            # do not try to verify "sums.csv" as it will not be included in "sums.csv"
            if "sums.csv" in filesMaster:
                filesMaster.remove("sums.csv")

            # read checksum file and get dictionary
            sumsDict = self.__readSumsCsvFile__(pathMaster)

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
                if file in filesMaster:
                    checksumCalc = str(self.__calcChecksum__(self.os.path.join(pathMaster, file)))
                    checksumSaved = sumsDict[file]
                    # verify calculated checksum against the one stored in sums.csv
                    if checksumCalc == checksumSaved:
                        pass
                    elif checksumCalc != checksumSaved:
                        # checksum mismatch -> trigger error condition and add file name to list of mismatched files
                        checksumErrors.append(file)
                        resultVerify = False
                else:
                    # file is included in sums.csv, but not in directory
                    resultVerify = False


            return self.Result(result=resultVerify, path=pathMaster, missingMaster=additionalItemsInSumsCSV, additionalMaster=missingItemsInSumsCSV, ChecksumMismatch=checksumErrors)

        # return with True, in case no files needed to be verifed
        return self.Result(result=True, path=pathMaster)

    def WriteChecksumFile(self, pathMaster, filesMaster, pathClone = [], filesClone = []):
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
        hashMismatch = []
        if len(filesMaster) > 0:
            try:
                f = open(self.os.path.join(pathMaster, "sums.csv"), "w")
                # do not hash "sums.csv" itself
                if "sums.csv" in filesMaster:
                    filesMaster.remove("sums.csv")
                # iterate through all files of current directory and add their names and checksums to "sums.csv"
                for file in filesMaster:
                    hash_digest = str(self.__calcChecksum__(self.os.path.join(pathMaster, file)))
                    # only add files without checksum errors and trigger error condition, when checksum calculation failed
                    if hash_digest != self.HASH_ERROR:
                        f.write(str(file) + ";" + str(hash_digest) + "\n")
                    else:
                        result = False
                        hashMismatch.append(str(file))
                f.close()
            except:
                return self.Result(result=False, path=pathMaster, ChecksumMismatch=hashMismatch)
        return self.Result(result=result, path=pathMaster, ChecksumMismatch=hashMismatch)


    def __calcChecksum__(self, filePath):
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


    def VerifyFiles(self, pathMaster, filesMaster, pathClone, filesClone):
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
                    checksumMaster = self.__calcChecksum__(masterFilePath)
                    checksumClone = self.__calcChecksum__(cloneFilePath)
                    # verify that both match and both are NOT "HASH_ERROR"
                    if checksumClone == checksumMaster and (checksumMaster != self.HASH_ERROR):
                        pass
                    else:
                        # checksum mismatch -> trigger error condition and add file name to list of mismatched files
                        checksumErrors.append(str(fileNameMaster))
                        result = False
        return self.Result(result=result, path=pathMaster, missingMaster = additionalItemsInPathClone, additionalMaster = missingItemsInPathClone, ChecksumMismatch=checksumErrors)


    def __getChecksumsFromFile__(self, filePathName):
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
            return self.__readSha256SumFile__(path, filename)
        elif filename == "sums.csv":
            return self.__readSumsCsvFile__(path)
        else:
            return dict()


    def __readSha256SumFile__(self, filePath, fileName):
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
            return dict()
        return sumsDict


    def __readSumsCsvFile__(self, filePath):
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
            return dict()
        return sumsDict



class vrfyCli:
    import os
    import subprocess

    #options
    GLOBAL_VERBOSITY = None
    CREATE_CSV = "-c"
    VERIFY_CSV = "-v"
    RECURSIVE = "-r"
    VERSION = "-version"
    PRINT = "-p"
    FILE = "-f"
    CHECKSUM = "-cs"
    MASTER_DIR = "-m"
    CLONE_DIR = "-c"
    OPTION_RECURSIVE = False
    OPTION_CREATE_CSV = False
    OPTION_VERIFY_CSV = False
    OPTION_VERIFY_VERSION = False
    OPTION_PRINT = False
    OPTION_FILE = -1
    OPTION_CHECKSUM = -1
    OPTION_MASTER_DIR = -1
    OPTION_CLONE_DIR = -1


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
        # decode options from argument list
        directories = []
        vf = vrfy()
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

        # execute decoded options
        executionResult = False
        # cli option: vrfy -version
        if self.OPTION_VERIFY_VERSION == True:
            print("vrfy version: " + str(vf.GetVersion()))
        # cli option: vrfy
        elif len(arguments) == 0:
            # no arguments are provided -> verify checksums of files within current working directory
            import os
            directories.append(os.getcwd())
            self.OPTION_VERIFY_CSV = True
            self.OPTION_RECURSIVE = True
            # verify sums
            print("Verifying current working directory against checksums:")
            executionResult = self.__walker__(directories[0], directories[0], vf.VerifyFilesAgainstChecksums)
            self.__printOverallResult__(executionResult)
        # cli option: vrfy <<directory>> <<directory>>
        elif (len(arguments) == 2 and self.os.path.isdir(arguments[0]) and self.os.path.isdir(arguments[1])):
            # only two paths are provided -> first: golden master / second: clone/copy to be verified
            print("Verifying directories:")
            print("Master: " + str(arguments[0]))
            print("Clone: " + str(arguments[1]))
            self.OPTION_RECURSIVE = True
            executionResult = self.__walker__(arguments[0], arguments[1], vf.VerifyFiles)
            self.__printOverallResult__(executionResult)
        # cli option: vrfy -m <<directory>> -c <<directory>>
        elif self.OPTION_MASTER_DIR >= 0 and self.OPTION_MASTER_DIR <= len(arguments) - 1 and self.OPTION_CLONE_DIR >= 0 and self.OPTION_CLONE_DIR <= len(arguments) - 1:
            print("Verifying directories:")
            print("Master: " + str(arguments[self.OPTION_MASTER_DIR]))
            print("Clone: " + str(arguments[self.OPTION_CLONE_DIR]))
            self.OPTION_RECURSIVE = True
            executionResult = self.__walker__(arguments[self.OPTION_MASTER_DIR], arguments[self.OPTION_CLONE_DIR], vf.VerifyFiles)
            self.__printOverallResult__(executionResult)
        # cli option: vrfy -f <<file>> -cs <<CHECKSUM>> OR vrfy -p -f <<file>> OR vrfy -p -f <<file>> -cs <<CHECKSUM>>
        elif self.OPTION_FILE >= 0 and self.OPTION_FILE <= len(arguments) - 1:
            if self.OPTION_CHECKSUM >= 0 and self.OPTION_CHECKSUM <= len(arguments) - 1:
                executionResult, calcChecksum = vf.VerifyFile(arguments[self.OPTION_FILE], arguments[self.OPTION_CHECKSUM])
            else:
                executionResult, calcChecksum = vf.VerifyFile(arguments[self.OPTION_FILE], "")
            if self.OPTION_PRINT:
                path, filename = self.os.path.split(arguments[self.OPTION_FILE])
                print(calcChecksum + "  " + str(filename))
            else:
                self.__printOverallResult__(executionResult)

        # cli option: vrfy -c <<directory>>
        elif self.OPTION_CREATE_CSV == True:
            if len(directories) == 1:
                # create sums
                print("Creating checksums for files:")
                executionResult = self.__walker__(directories[0], directories[0], vf.WriteChecksumFile)
                self.__printOverallResult__(executionResult)
            else:
                print("Error: Option '" + str(self.VERIFY_CSV) + "' provided, but '" + str(len(directories)) + "' directories are given (required: 1).")
        # cli option: vrfy -v <<directory>>
        elif self.OPTION_VERIFY_CSV == True:
            if len(directories) == 1:
                # verify sums
                print("Verifying files against checksums:")
                executionResult = self.__walker__(directories[0], directories[0], vf.VerifyFilesAgainstChecksums)
                self.__printOverallResult__(executionResult)
            else:
                print("Error: Option '" + str(self.VERIFY_CSV) + "' provided, but '" + str(len(directories)) + "' directories are given (required: 1).")
        else:
            print("No valid argument setting found!")
            return 1
        if executionResult == True:
            return 0
        else:
            return 1

    def __walker__(self, pathMaster, pathClone, func):
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
        import os
        if os.path.isdir(pathMaster) and os.path.isdir(pathClone):
            # create lists of files and directories that are included in current path
            filesM = [entryA for entryA in os.listdir(pathMaster) if not os.path.isdir(os.path.join(pathMaster, entryA))]
            filesC = [entryB for entryB in os.listdir(pathClone) if not os.path.isdir(os.path.join(pathClone, entryB))]
            dictsM = [entryDir for entryDir in os.listdir(pathMaster) if os.path.isdir(os.path.join(pathMaster, entryDir))]

            # execute requested operation
            print("" + str(pathMaster), end=" : ", flush=True)
            resultObject = func(pathMaster, filesM, pathClone, filesC)
            resultVerify = resultObject.Result
            #ResultList.append(resultObject)
            self.__printResult__(resultObject)

            # jump into child directories, if recursive operation is requested
            if self.OPTION_RECURSIVE == True:
                for nextFolder in dictsM:
                    resultVerify = self.__walker__(os.path.join(pathMaster, nextFolder), os.path.join(pathClone, nextFolder), func) & resultVerify

            return resultVerify
        else:
            # terminate, since paths are not pointing to valid directories
            return False

    def __printResult__(self, result: vrfy.Result):
        if result.Result == True:
            print("PASS")
        else:
            print("FAILED!!!")
        for file in result.ChecksumMismatch:
            print("[MISMATCH] " + str(file))
        for file in result.AdditionalInMaster:
            print("[+] " + str(file))
        for file in result.MissingInMaster:
            print("[-] " + str(file))

    def __printOverallResult__(self, res):
        if res:
            print("Overall: PASS")
        else:
            print("Overall: FAIL")

def main():
    import sys
    verify = vrfyCli()
    sys.exit(verify.parseArgumentsAndExecute(sys.argv[1:]))

if __name__ == "__main__":
    main()
