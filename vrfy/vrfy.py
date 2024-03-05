#!/usr/bin/env python3
import os
import hashlib


class vrfy:
    class Result:
        def __init__(self, result, path, pathError = False, missingFiles=[], additionalFiles=[], ChecksumMismatch=[],
                     masterChecksums=dict(), backupChecksums=dict()):
            self.Result = result
            self.Path = path
            self.PathError = pathError
            self.MissingFiles = missingFiles
            self.AdditionalFiles = additionalFiles
            self.ChecksumMismatch = ChecksumMismatch
            self.MasterChecksums = masterChecksums
            self.BackupChecksums = backupChecksums


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
        # start file verification, when filepath is valid
        if os.path.isfile(filePath):
            masterHashDict = dict()
            expHashDict = dict()
            checksumErrors = []

            resultVerify = True
            expectation = str(expectedChecksum)
            calcChecksum = self.__calcChecksum__(filePath)
            path, filename = os.path.split(filePath)
            # no hex checksum provided, read sums.csv / *.sha256sums-file
            if os.path.isfile(expectedChecksum):
                try:
                    sumsDict = self.__getChecksumsFromFile__(expectedChecksum)
                    expectation = sumsDict[filename]
                except Exception:
                    resultVerify = False
            # store calculated and expected checksum
            masterHashDict[filename] = calcChecksum
            expHashDict[filename] = expectation
            # verify file checksum
            if calcChecksum == expectation:
                pass
            else:
                resultVerify = False
                checksumErrors.append(filename)

            return self.Result(result=resultVerify, path=path, ChecksumMismatch=checksumErrors,
                               masterChecksums=masterHashDict, backupChecksums=expHashDict)
        else:
            # stop execution, since filepath is NOT valid
            return self.Result(result=False, path=filePath, pathError=True)

    def VerifyFilesAgainstChecksums(self, path: str) -> Result:
        """
        Verifies the contents of directory >>path<< against the included checksums in sums.csv.

        Parameters:
            path (str): Path to directory whose files shall get verified.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        # start file verification, when path is valid
        if os.path.isdir(path):
            # determine available files in path -> list of file names
            files = [entryB for entryB in os.listdir(path) if
                    not os.path.isdir(os.path.join(path, entryB))]

            resultVerify = True
            fileHashDict = dict()

            # check if checksum file is available, if not abort execution
            if "sums.csv" not in files and len(files) > 0:
                # calculate has values for additional files
                for file in files:
                    fileHashDict[file] = self.__calcChecksum__(os.path.join(path, file))
                return self.Result(result=False, path=path, additionalFiles=files,
                                   masterChecksums=fileHashDict)

            if len(files) > 0:
                # do not try to verify "sums.csv" as it will not be included in "sums.csv"
                if "sums.csv" in files:
                    # save hashvalues for later analysis
                    fileHashDict["sums.csv"] = self.__calcChecksum__(os.path.join(path, "sums.csv"))
                    files.remove("sums.csv")

                # read checksum file and get dictionary
                sumsDict = self.__readSumsCsvFile__(path)

                checksumErrors = []
                # iterate through all files and compare their checksum with those stored in sums.csv
                for file in sumsDict.keys():
                    if file in files:
                        checksumCalc = self.__calcChecksum__(os.path.join(path, file))
                        checksumSaved = sumsDict[file]
                        # save hashvalues for later analysis
                        fileHashDict[file] = checksumCalc
                        # verify calculated checksum against the one stored in sums.csv
                        if checksumCalc == checksumSaved:
                            pass
                        else:
                            # checksum mismatch -> set error flag and add file name to list of mismatched files
                            checksumErrors.append(file)
                            resultVerify = False
                    else:
                        # file is included in sums.csv, but not in directory
                        resultVerify = False

                # verify that all files in current working directory are included in sums.csv, and vice versa
                # set error flag if check failed
                missingItemsInSumsCSV = [i for i in files if i not in sumsDict.keys()]
                additionalItemsInSumsCSV = [i for i in sumsDict.keys() if i not in files]
                if len(missingItemsInSumsCSV) != 0 or len(additionalItemsInSumsCSV) != 0:
                    resultVerify = False

                # calculate has values for additional files
                for file in missingItemsInSumsCSV:
                    fileHashDict[file] = self.__calcChecksum__(os.path.join(path, file))

                return self.Result(result=resultVerify, path=path, missingFiles=additionalItemsInSumsCSV,
                                   additionalFiles=missingItemsInSumsCSV, ChecksumMismatch=checksumErrors,
                                   masterChecksums=fileHashDict, backupChecksums=sumsDict)
            else:
                # return with True, in case no files needed to be verifed
                return self.Result(result=True, path=path)
        else:
            # stop execution, since path is NOT valid
            return self.Result(result=True, path=path, pathError=True)

    def WriteChecksumFile(self, path: str) -> Result:
        """
        Creates file sums.csv with checksums for files in >>path<<.

        Parameters:
            path (str): Path to directory whose files shall get hashed and checksums stored in sums.csv.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        # start checksum creation, when path is valid
        if os.path.isdir(path):
            # determine available files in path -> list of file names
            files = [entryB for entryB in os.listdir(path) if
                           not os.path.isdir(os.path.join(path, entryB))]
            # create sums.csv, if directory contains files
            result = True
            hashErrors = []
            if len(files) > 0:
                try:
                    with open(os.path.join(path, "sums.csv"), "w") as f:
                        # do not hash "sums.csv" itself
                        if "sums.csv" in files:
                            files.remove("sums.csv")
                        # iterate through all files of current directory and add their names and checksums to "sums.csv"
                        for file in files:
                            hash_digest = self.__calcChecksum__(os.path.join(path, file))
                            # only add files without checksum errors or set error flag, when checksum calculation
                            # failed
                            if hash_digest != self.HASH_ERROR:
                                f.write(str(file) + ";" + str(hash_digest) + "\n")
                            else:
                                result = False
                                hashErrors.append(str(file))
                except OSError:
                    return self.Result(result=False, path=path, ChecksumMismatch=hashErrors)
            return self.Result(result=result, path=path, ChecksumMismatch=hashErrors)
        else:
            # stop execution, since path is NOT valid
            return self.Result(result=False, path=path, pathError=True)

    def VerifyFiles(self, pathMaster: str, pathBackup: str) -> Result:
        """
        Verifies the contents of directory "pathMaster" against the contents of "pathBackup" based on the respective 
        file checksums.

        Parameters:
            pathMaster (str): Path to the master directory whose contents are considered valid and unchanged, serving as
                                a baseline for comparison.
            pathBackup (str): Path to backup directory whose files shall get verified against the master copy.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        # stop execution if both path are invalid
        if not os.path.isdir(pathMaster) and not os.path.isdir(pathBackup):
            return self.Result(result=False, path=pathMaster, pathError=True)

        result = True
        masterHashDict = dict()
        backupHashDict = dict()
        missingItemsInPathBackup = []
        additionalItemsInPathBackup = []
        checksumErrors = []

        # stop execution, if backup path is invalid
        if os.path.isdir(pathMaster) and not os.path.isdir(pathBackup):
            filesMaster = [entryB for entryB in os.listdir(pathMaster) if
                           not os.path.isdir(os.path.join(pathMaster, entryB))]
            for file in filesMaster:
                masterFilePath = os.path.join(pathMaster, file)
                checksumMaster = self.__calcChecksum__(masterFilePath)
                masterHashDict[file] = checksumMaster
            return self.Result(result=False, path=pathMaster, pathError=True, missingFiles=filesMaster,
                               additionalFiles=[], ChecksumMismatch=[],
                               masterChecksums=masterHashDict, backupChecksums=dict())

        # stop execution, if master path is invalid
        if os.path.isdir(pathBackup) and not os.path.isdir(pathMaster):
            filesBackup = [entryB for entryB in os.listdir(pathBackup) if
                           not os.path.isdir(os.path.join(pathBackup, entryB))]
            for file in filesBackup:
                backupFilePath = os.path.join(pathBackup, file)
                checksumBackup = self.__calcChecksum__(backupFilePath)
                backupHashDict[file] = checksumBackup
            return self.Result(result=False, path=pathMaster, pathError=True, missingFiles=[],
                               additionalFiles=filesBackup, ChecksumMismatch=[],
                               masterChecksums=dict(), backupChecksums=backupHashDict)

        # below: both paths are valid
        # determine available files in master and backup paths -> lists of file names
        filesMaster = [entryB for entryB in os.listdir(pathMaster) if
                       not os.path.isdir(os.path.join(pathMaster, entryB))]
        filesBackup = [entryB for entryB in os.listdir(pathBackup) if
                       not os.path.isdir(os.path.join(pathBackup, entryB))]

        # start file verification, when files are included in master directory
        # iterate through all files of master directory and verify their checksums to those of the backup directory
        # not executed, when no entires in filesMaster list
        for fileNameMaster in filesMaster:
            # master file is not included on backup directory -> set error flag
            if fileNameMaster not in filesBackup:
                result = False
            else:
                # calculate checksums for master and backup file
                masterFilePath = os.path.join(pathMaster, fileNameMaster)
                backupFilePath = os.path.join(pathBackup, fileNameMaster)
                checksumMaster = self.__calcChecksum__(masterFilePath)
                checksumBackup = self.__calcChecksum__(backupFilePath)
                # save hashvalues for later analysis
                masterHashDict[fileNameMaster] = checksumMaster
                backupHashDict[fileNameMaster] = checksumBackup
                # verify that both match and both are NOT "HASH_ERROR"
                if checksumBackup == checksumMaster and (checksumMaster != self.HASH_ERROR):
                    pass
                else:
                    # checksum mismatch -> set error flag and add file name to list of mismatched files
                    checksumErrors.append(str(fileNameMaster))
                    result = False

        # search for missing or additional files in master and backup, and set error flag
        missingItemsInPathBackup = [i for i in filesMaster if i not in filesBackup]
        additionalItemsInPathBackup = [i for i in filesBackup if i not in filesMaster]
        if len(missingItemsInPathBackup) != 0 or len(additionalItemsInPathBackup) != 0:
            result = False

        # calculate checksums for additional and missing files
        for missingBackup in missingItemsInPathBackup:
            masterFilePath = os.path.join(pathMaster, missingBackup)
            checksumMaster = self.__calcChecksum__(masterFilePath)
            masterHashDict[missingBackup] = checksumMaster
        for additionalBackup in additionalItemsInPathBackup:
            backupFilePath = os.path.join(pathBackup, additionalBackup)
            checksumBackup = self.__calcChecksum__(backupFilePath)
            backupHashDict[additionalBackup] = checksumBackup

        return self.Result(result=result, path=pathMaster, missingFiles=missingItemsInPathBackup,
                           additionalFiles=additionalItemsInPathBackup, ChecksumMismatch=checksumErrors,
                           masterChecksums=masterHashDict, backupChecksums=backupHashDict)

    def __calcChecksum__(self, filePath: str) -> str:
        """
        Calculates and returns file hash for >>filePath<<.

        Parameters:
            filePath (str): Path and name of the file that shall get hashed.

        Returns:
            str: Hash digest.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(filePath, 'rb') as f:
                while True:
                    block = f.read(8192)
                    if not block:
                        break
                    sha256_hash.update(block)
        except OSError:
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
        path, filename = os.path.split(filePathName)
        name, extension = os.path.splitext(os.path.basename(filePathName))
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
            with open(os.path.join(filePath, fileName), "r") as f:
                for line in f.readlines():
                    entry = line.replace("\n", "").split("  ")
                    sumsDict[entry[1]] = entry[0]
        except OSError:
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
            with open(os.path.join(filePath, "sums.csv"), "r") as f:
                for line in f.readlines():
                    entry = line.replace("\n", "").split(";")
                    # compatibility layer for legacy sums.csv, where hash digest started with "b'" and ended with "'"
                    if entry[1][:2] == "b'" and entry[1][-1] == "'":
                        entry[1] = entry[1][2:-1]
                    sumsDict[entry[0]] = entry[1]
        except OSError:
            # except file errors, and close verification with FAIL (i.e. "False" result)
            return dict()
        return sumsDict
