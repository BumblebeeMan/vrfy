#!/usr/bin/env python3
import os

class vrfy:
    class Result:
        def __init__(self, result, path, missingMaster=[], additionalMaster=[], ChecksumMismatch=[],
                     masterChecksums=dict(), backupChecksums=dict()):
            self.Result = result
            self.Path = path
            self.MissingInMaster = missingMaster
            self.AdditionalInMaster = additionalMaster
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
        masterHashDict = dict()
        expHashDict = dict()
        checksumErrors = []

        resultVerify = True
        expectation = expectedChecksum
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
        if calcChecksum == expectation:
            pass
        else:
            resultVerify = False
            checksumErrors.append(filename)

        return self.Result(result=resultVerify, path=path, ChecksumMismatch=checksumErrors,
                           masterChecksums=masterHashDict, backupChecksums=expHashDict)

    def VerifyFilesAgainstChecksums(self, pathMaster: str) -> Result:
        """
        Verifies the contents of directory "pathMaster" against the included checksums in sums.csv.

        Parameters:
            pathMaster (str): Path to directory whose files shall get verified.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        filesMaster = [entryB for entryB in os.listdir(pathMaster) if
                       not os.path.isdir(os.path.join(pathMaster, entryB))]
        fileHashDict = dict()
        # check if checksum file is available, if not abort execution
        if "sums.csv" not in filesMaster and len(filesMaster) > 0:
            # calculate has values for additional files
            for file in filesMaster:
                fileHashDict[file] = self.__calcChecksum__(os.path.join(pathMaster, file))
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
                    checksumCalc = self.__calcChecksum__(os.path.join(pathMaster, file))
                    checksumSaved = sumsDict[file]
                    # save hashvalues for later analysis
                    fileHashDict[file] = checksumCalc
                    # verify calculated checksum against the one stored in sums.csv
                    if checksumCalc == checksumSaved:
                        pass
                    else:
                        # checksum mismatch -> trigger error condition and add file name to list of mismatched files
                        checksumErrors.append(file)
                        resultVerify = False
                else:
                    # file is included in sums.csv, but not in directory
                    resultVerify = False

            # calculate has values for additional files
            for file in missingItemsInSumsCSV:
                fileHashDict[file] = self.__calcChecksum__(os.path.join(pathMaster, file))

            return self.Result(result=resultVerify, path=pathMaster, missingMaster=additionalItemsInSumsCSV,
                               additionalMaster=missingItemsInSumsCSV, ChecksumMismatch=checksumErrors,
                               masterChecksums=fileHashDict, backupChecksums=sumsDict)

        # return with True, in case no files needed to be verifed
        return self.Result(result=True, path=pathMaster)

    def WriteChecksumFile(self, pathMaster: str) -> Result:
        """
        Creates file sums.csv with checksums for files [filesMaster] in >>pathMaster<<.

        Parameters:
            pathMaster (str): Path to directory whose files shall get hashed and checksums stored in sums.csv.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        filesMaster = [entryB for entryB in os.listdir(pathMaster) if
                       not os.path.isdir(os.path.join(pathMaster, entryB))]
        # create sums.csv, if directory contains files
        result = True
        hashMismatch = []
        if len(filesMaster) > 0:
            try:
                f = open(os.path.join(pathMaster, "sums.csv"), "w")
                # do not hash "sums.csv" itself
                if "sums.csv" in filesMaster:
                    filesMaster.remove("sums.csv")
                # iterate through all files of current directory and add their names and checksums to "sums.csv"
                for file in filesMaster:
                    hash_digest = self.__calcChecksum__(os.path.join(pathMaster, file))
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

    def VerifyFiles(self, pathMaster: str, pathBackup: str) -> Result:
        """
        Verifies the contents of directory "pathMaster" against the contents of "pathBackup" based on the respective file
        checksums.

        Parameters:
            pathMaster (str): Path to the master directory whose contents are considered valid and unchanged, serving as
                                a baseline for comparison.
            pathBackup (str): Path to backup directory whose files shall get verified against the master copy.

        Returns:
            vrfy.Result: Results result object of type vrfy.Result.
        """
        filesMaster = [entryB for entryB in os.listdir(pathMaster) if not os.path.isdir(os.path.join(pathMaster, entryB))]
        filesBackup = [entryB for entryB in os.listdir(pathBackup) if not os.path.isdir(os.path.join(pathBackup, entryB))]
        result = True
        masterHashDict = dict()
        backupHashDict = dict()
        missingItemsInPathBackup = []
        additionalItemsInPathBackup = []
        checksumErrors = []
        # start file verification, when files are included in directory
        if len(filesMaster) > 0:
            # search for missing or additional files in master and backup, and trigger error condition
            missingItemsInPathBackup = [i for i in filesMaster if i not in filesBackup]
            additionalItemsInPathBackup = [i for i in filesBackup if i not in filesMaster]
            if len(missingItemsInPathBackup) != 0:
                result = False
            if len(additionalItemsInPathBackup) != 0:
                result = False

            # iterate through all files of master directory and verify their checksums to those of the backup directory
            for fileNameMaster in filesMaster:
                # master file is not included on backup directory -> trigger error condition
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
                        # checksum mismatch -> trigger error condition and add file name to list of mismatched files
                        checksumErrors.append(str(fileNameMaster))
                        result = False
        return self.Result(result=result, path=pathMaster, missingMaster=additionalItemsInPathBackup,
                           additionalMaster=missingItemsInPathBackup, ChecksumMismatch=checksumErrors,
                           masterChecksums=masterHashDict, backupChecksums=backupHashDict)

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
            f = open(os.path.join(filePath, fileName), "r")
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
            f = open(os.path.join(filePath, "sums.csv"), "r")
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
