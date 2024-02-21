#!/usr/bin/env python3
class vrfy:
    class Result:
        def __init__(self, result, path, missingMaster=[], additionalMaster=[], ChecksumMismatch=[],
                     masterChecksums=dict(), cloneChecksums=dict()):
            self.Result = result
            self.Path = path
            self.MissingInMaster = missingMaster
            self.AdditionalInMaster = additionalMaster
            self.ChecksumMismatch = ChecksumMismatch
            self.MasterChecksums = masterChecksums
            self.CloneChecksums = cloneChecksums

    import os
    import subprocess

    VERSION_STR = "0.4.0"
    HASH_ERROR = "ERROR"

    def __init__(self):
        pass

    def GetVersion(self) -> str:
        """
        Returns version string.

        Returns:
            str: Returns version string.
        """
        return self.VERSION_STR

    def VerifyFile(self, filePath: str, expectedChecksum: str = "") -> Result:
        """
        Verifies the contents of file "filePath" against the checksum provided with "expectedChecksum".

        Parameters:
            filePath (str): Path + name to the file that should be verified.
            expectedChecksum (str): Checksum value or path + file name of *.sha256-/sums.csv file.

        Returns:
            result, calculatedChecksum (bool, str): Tuple. Result of verification and calculated sum of "filePath".
        """
        masterHashDict = dict()
        expHashDict = dict()
        checksumErrors = []

        resultVerify = True
        expectation = expectedChecksum
        calcChecksum = self.__calcChecksum__(filePath)
        path, filename = self.os.path.split(filePath)
        # no hex checksum provided, read sums.csv / *.sha256sums-file
        if self.os.path.isfile(expectedChecksum):
            try:
                sumsDict = self.__getChecksumsFromFile__(expectedChecksum)
                expectation = sumsDict[filename]
            except Exception:
                resultVerify = False
        # store calculated and expected checksum
        masterHashDict[filename] = calcChecksum
        expHashDict[filename] = expectation
        if calcChecksum == expectation:
            pass
        else:
            resultVerify = False
            checksumErrors.append(filename)

        return self.Result(result=resultVerify, path=path, ChecksumMismatch=checksumErrors,
                           masterChecksums=masterHashDict, cloneChecksums=expHashDict)

    def VerifyFilesAgainstChecksums(self, pathMaster: str, filesMaster: list,
                                    pathClone: str = "", filesClone: list = None) -> Result:
        """
        Verifies the contents of directory "pathMaster" against the included checksums in sums.csv.

        Parameters:
            pathMaster (str): Path to directory whose files shall get verified.
            filesMaster (List[str]): Names of all files that are included in the directory >>pathMaster<<.
            pathClone (str): NOT USED! Included for compatibility reasons only.
            filesClone (List[str]): NOT USED! Included for compatibility reasons only.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        fileHashDict = dict()
        # check if checksum file is available, if not abort execution
        if "sums.csv" not in filesMaster and len(filesMaster) > 0:
            # calculate has values for additional files
            for file in filesMaster:
                fileHashDict[file] = self.__calcChecksum__(self.os.path.join(pathMaster, file))
            return self.Result(result=False, path=pathMaster, additionalMaster=filesMaster,
                               masterChecksums=fileHashDict)

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
                    checksumCalc = self.__calcChecksum__(self.os.path.join(pathMaster, file))
                    checksumSaved = sumsDict[file]
                    # save hashvalues for later analysis
                    fileHashDict[file] = checksumCalc
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

            # calculate has values for additional files
            for file in missingItemsInSumsCSV:
                fileHashDict[file] = self.__calcChecksum__(self.os.path.join(pathMaster, file))

            return self.Result(result=resultVerify, path=pathMaster, missingMaster=additionalItemsInSumsCSV,
                               additionalMaster=missingItemsInSumsCSV, ChecksumMismatch=checksumErrors,
                               masterChecksums=fileHashDict, cloneChecksums=sumsDict)

        # return with True, in case no files needed to be verifed
        return self.Result(result=True, path=pathMaster)

    def WriteChecksumFile(self, pathMaster: str, filesMaster: list,
                          pathClone: str = "", filesClone: list = None) -> Result:
        """
        Creates file sums.csv with checksums for files [filesMaster] in >>pathMaster<<.

        Parameters:
            pathMaster (str): Path to directory whose files shall get hashed and checksums stored in sums.csv.
            filesMaster (List[str]): Names of all files that are included in the directory >>pathMaster<<.
            pathClone (str): NOT USED! Included for compatibility reasons only.
            filesClone (List[str]): NOT USED! Included for compatibility reasons only.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        # create sums.csv, if directory contains files
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
                    hash_digest = self.__calcChecksum__(self.os.path.join(pathMaster, file))
                    # only add files without checksum errors and trigger error condition, when checksum calculation
                    # failed
                    if hash_digest != self.HASH_ERROR:
                        f.write(str(file) + ";" + str(hash_digest) + "\n")
                    else:
                        result = False
                        hashMismatch.append(str(file))
                f.close()
            except Exception:
                return self.Result(result=False, path=pathMaster, ChecksumMismatch=hashMismatch)
        return self.Result(result=result, path=pathMaster, ChecksumMismatch=hashMismatch)

    def VerifyFiles(self, pathMaster: str, filesMaster: list, pathClone: str, filesClone: list) -> Result:
        """
        Verifies the contents of directory "pathMaster" against the contents of "pathClone" based on the respective file
        checksums.

        Parameters:
            pathMaster (str): Path to the master directory whose contents are considered valid and unchanged, serving as
                                a baseline for comparison.
            filesMaster (List[str]): Names of all files that are included in the directory >>pathMaster<<.
            pathClone (str): Path to clone directory whose files shall get verified against the master copy.
            filesClone (List[str]): Names of all files that are included in the directory >>pathClone<<.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        result = True
        masterHashDict = dict()
        cloneHashDict = dict()
        missingItemsInPathClone = []
        additionalItemsInPathClone = []
        checksumErrors = []
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
                    # save hashvalues for later analysis
                    masterHashDict[fileNameMaster] = checksumMaster
                    cloneHashDict[fileNameMaster] = checksumClone
                    # verify that both match and both are NOT "HASH_ERROR"
                    if checksumClone == checksumMaster and (checksumMaster != self.HASH_ERROR):
                        pass
                    else:
                        # checksum mismatch -> trigger error condition and add file name to list of mismatched files
                        checksumErrors.append(str(fileNameMaster))
                        result = False
        return self.Result(result=result, path=pathMaster, missingMaster=additionalItemsInPathClone,
                           additionalMaster=missingItemsInPathClone, ChecksumMismatch=checksumErrors,
                           masterChecksums=masterHashDict, cloneChecksums=cloneHashDict)

    def __calcChecksum__(self, filePath: str) -> str:
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
        except Exception:
            # print("ERROR: Unable to calculate SHA256 hash.")
            return self.HASH_ERROR
        return str(sha256_hash.hexdigest())

    def __getChecksumsFromFile__(self, filePathName: str) -> dict:
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

    def __readSha256SumFile__(self, filePath: str, fileName: str) -> dict:
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
                entry = line.replace("\n", "").split("  ")
                sumsDict[entry[1]] = entry[0]
            f.close()
        except IOError:
            # except file errors, and close verification with FAIL (i.e. "False" result)
            return dict()
        return sumsDict

    def __readSumsCsvFile__(self, filePath: str) -> dict:
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
                entry = line.replace("\n", "").split(";")
                # compatibility layer for legacy sums.csv, where hash digest started with "b'" and ended with "'"
                if entry[1][:2] == "b'" and entry[1][-1] == "'":
                    entry[1] = entry[1][2:-1]
                sumsDict[entry[0]] = entry[1]
            f.close()
        except IOError:
            # except file errors, and close verification with FAIL (i.e. "False" result)
            return dict()
        return sumsDict


class vrfyCli:
    import os
    import subprocess

    # options
    GLOBAL_VERBOSITY = None
    CREATE_CSV: str = "-c"
    VERIFY_CSV: str = "-v"
    RECURSIVE: str = "-r"
    VERSION: str = "-version"
    PRINT: str = "-p"
    FILE: str = "-f"
    CHECKSUM: str = "-cs"
    MASTER_DIR: str = "-m"
    CLONE_DIR: str = "-c"
    OPTION_RECURSIVE = False
    OPTION_CREATE_CSV: bool = False
    OPTION_VERIFY_CSV: bool = False
    OPTION_VERIFY_VERSION: bool = False
    OPTION_PRINT: bool = False
    OPTION_FILE: int = -1
    OPTION_CHECKSUM: int = -1
    OPTION_MASTER_DIR: int = -1
    OPTION_CLONE_DIR: int = -1

    def __init__(self):
        pass

    def parseArgumentsAndExecute(self, arguments: list) -> int:
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
                if (len(arguments) - 2) <= index + 1:  # index + 1 shall be second to last or earlier
                    self.OPTION_CHECKSUM = index + 1
                else:
                    print("Error: Option '" + str(self.CHECKSUM) + "' provided, but '" + str(
                        self.CHECKSUM) + "' is not followed by checksum to test.")
            if arguments[index] == self.FILE:
                if self.os.path.isfile(arguments[index + 1]):
                    self.OPTION_FILE = index + 1
                else:
                    print("Error: Option '" + str(self.FILE) + "' provided, but '" + str(
                        arguments[index + 1]) + "' is no file.")
            if arguments[index] == self.MASTER_DIR:
                if self.os.path.isdir(arguments[index + 1]):
                    self.OPTION_MASTER_DIR = index + 1
                else:
                    print("Error: Option '" + str(self.MASTER_DIR) + "' provided, but '" + str(
                        arguments[index + 1]) + "' is no directory.")
            if arguments[index] == self.CLONE_DIR:
                if self.os.path.isdir(arguments[index + 1]):
                    self.OPTION_CLONE_DIR = index + 1
                else:
                    print("Error: Option '" + str(self.CLONE_DIR) + "' provided, but '" + str(
                        arguments[index + 1]) + "' is no directory.")

        # execute decoded options
        executionResult = False
        # cli option: vrfy -version
        if self.OPTION_VERIFY_VERSION:
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
        elif len(arguments) == 2 and self.os.path.isdir(arguments[0]) and self.os.path.isdir(arguments[1]):
            # only two paths are provided -> first: golden master / second: clone/copy to be verified
            print("Verifying directories:")
            print("Master: " + str(arguments[0]))
            print("Clone: " + str(arguments[1]))
            self.OPTION_RECURSIVE = True
            executionResult = self.__walker__(arguments[0], arguments[1], vf.VerifyFiles)
            self.__printOverallResult__(executionResult)

        # cli option: vrfy -m <<directory>> -c <<directory>>
        elif 0 <= self.OPTION_MASTER_DIR <= len(arguments) - 1 and 0 <= self.OPTION_CLONE_DIR <= len(arguments) - 1:
            print("Verifying directories:")
            print("Master: " + str(arguments[self.OPTION_MASTER_DIR]))
            print("Clone: " + str(arguments[self.OPTION_CLONE_DIR]))
            self.OPTION_RECURSIVE = True
            executionResult = self.__walker__(arguments[self.OPTION_MASTER_DIR], arguments[self.OPTION_CLONE_DIR],
                                              vf.VerifyFiles)
            self.__printOverallResult__(executionResult)

        # cli option: vrfy -f <<file>> -cs <<CHECKSUM>> OR vrfy -p -f <<file>> OR vrfy -p -f <<file>> -cs <<CHECKSUM>>
        elif 0 <= self.OPTION_FILE <= len(arguments) - 1:
            if 0 <= self.OPTION_CHECKSUM <= len(arguments) - 1:
                res = vf.VerifyFile(arguments[self.OPTION_FILE], arguments[self.OPTION_CHECKSUM])
            else:
                res = vf.VerifyFile(arguments[self.OPTION_FILE], "")
            executionResult = res.Result
            path, filename = self.os.path.split(arguments[self.OPTION_FILE])
            calcChecksum = res.MasterChecksums[filename]
            if self.OPTION_PRINT:
                print(calcChecksum + "  " + str(filename))
            else:
                self.__printOverallResult__(executionResult)

        # cli option: vrfy -c <<directory>>
        elif self.OPTION_CREATE_CSV:
            if len(directories) == 1:
                # create sums
                print("Creating checksums for files:")
                executionResult = self.__walker__(directories[0], directories[0], vf.WriteChecksumFile)
                self.__printOverallResult__(executionResult)
            else:
                print("Error: Option '" + str(self.VERIFY_CSV) + "' provided, but '" + str(
                    len(directories)) + "' directories are given (required: 1).")

        # cli option: vrfy -v <<directory>>
        elif self.OPTION_VERIFY_CSV:
            if len(directories) == 1:
                # verify sums
                print("Verifying files against checksums:")
                executionResult = self.__walker__(directories[0], directories[0], vf.VerifyFilesAgainstChecksums)
                self.__printOverallResult__(executionResult)
            else:
                print("Error: Option '" + str(self.VERIFY_CSV) + "' provided, but '" + str(
                    len(directories)) + "' directories are given (required: 1).")
        else:
            print("No valid argument setting found!")
            return 1
        if executionResult:
            return 0
        else:
            return 1

    def __walker__(self, pathMaster: str, pathClone: str, func) -> bool:
        """
        Verifies the contents of directory "pathMaster" against the included checksums in sums.csv.

        Parameters:
            pathMaster (str): Path to the master directory whose contents are considered valid and unchanged, serving as
                                a baseline for comparison. .
            pathClone (str): Path to clone directory whose files shall get verified against the master copy.
            func (callable) -- Function that gets executed on the respective folder.

        Returns:
            bool:   True, when all executions of >>func<< returned PASS, else False.
        """
        # check if received strings are valid paths
        import os
        if os.path.isdir(pathMaster) and os.path.isdir(pathClone):
            # create lists of files and directories that are included in current path
            filesM = [entryA for entryA in os.listdir(pathMaster) if
                      not os.path.isdir(os.path.join(pathMaster, entryA))]
            filesC = [entryB for entryB in os.listdir(pathClone) if not os.path.isdir(os.path.join(pathClone, entryB))]
            dictsM = [entryDir for entryDir in os.listdir(pathMaster) if
                      os.path.isdir(os.path.join(pathMaster, entryDir))]

            # execute requested operation
            print("" + str(pathMaster), end=" : ", flush=True)
            resultObject = func(pathMaster, filesM, pathClone, filesC)
            resultVerify = resultObject.Result
            # ResultList.append(resultObject)
            self.__printResult__(resultObject)

            # jump into child directories, if recursive operation is requested
            if self.OPTION_RECURSIVE:
                for nextFolder in dictsM:
                    resultVerify = self.__walker__(os.path.join(pathMaster, nextFolder),
                                                   os.path.join(pathClone, nextFolder), func) & resultVerify

            return resultVerify
        else:
            # terminate, since paths are not pointing to valid directories
            return False

    def __printResult__(self, result: vrfy.Result) -> None:
        if result.Result:
            print("PASS")
        else:
            print("FAILED!!!")
        for file in result.ChecksumMismatch:
            print("[MISMATCH] " + str(file))
            if self.OPTION_PRINT:
                print("- Master: " + result.MasterChecksums[file])
                print("- Clone: " + result.CloneChecksums[file])
        for file in result.AdditionalInMaster:
            print("[+] " + str(file))
            if self.OPTION_PRINT:
                print("- cs: " + result.MasterChecksums[file])
        for file in result.MissingInMaster:
            print("[-] " + str(file))
            if self.OPTION_PRINT:
                print("- cs: " + result.CloneChecksums[file])

    def __printOverallResult__(self, res: bool):
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
