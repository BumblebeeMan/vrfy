#!/usr/bin/env python3

from vrfy.vrfy import vrfy
import os

class vrfyCli:

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
        # create lists of files and directories that are included in current path
        filesM = filesC = dictsM = dictsC = []
        if os.path.isdir(pathMaster):
            filesM = [entryA for entryA in os.listdir(pathMaster) if
                      not os.path.isdir(os.path.join(pathMaster, entryA))]
            dictsM = [entryDir for entryDir in os.listdir(pathMaster) if
                      os.path.isdir(os.path.join(pathMaster, entryDir))]
        if os.path.isdir(pathClone):
            filesC = [entryB for entryB in os.listdir(pathClone) if not os.path.isdir(os.path.join(pathClone, entryB))]
            dictsC = [entryDir for entryDir in os.listdir(pathClone) if
                      os.path.isdir(os.path.join(pathClone, entryDir))]

        combinedDicts = list(set(dictsM + dictsC))

        if os.path.isdir(pathMaster) and os.path.isdir(pathClone):
            print(pathMaster, end=" : ", flush=True)
            # execute requested operation
            from inspect import signature
            numParam = len(signature(func).parameters)
            if numParam == 2:
                resultObject = func(pathMaster, pathClone)
            elif numParam == 1:
                resultObject = func(pathMaster)
            else:
                return False
        else:
            if os.path.isdir(pathMaster):
                print("[+] " + pathMaster, end=" : ", flush=True)
                resultObject = vrfy.Result(False, pathMaster, additionalMaster=filesM, missingMaster=filesC)
            if os.path.isdir(pathClone):
                print("[-] " + pathClone, end=" : ", flush=True)
                resultObject = vrfy.Result(False, pathClone, additionalMaster=filesM, missingMaster=filesC)
        resultVerify = resultObject.Result
        # ResultList.append(resultObject)
        self.__printResult__(resultObject)

        # jump into child directories, if recursive operation is requested
        if self.OPTION_RECURSIVE:
            for nextFolder in combinedDicts:
                resultVerify = self.__walker__(os.path.join(pathMaster, nextFolder),
                                               os.path.join(pathClone, nextFolder), func) & resultVerify

        return resultVerify


    def __printResult__(self, result) -> None:
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
