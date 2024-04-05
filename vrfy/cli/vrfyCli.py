#!/usr/bin/env python3
from vrfy.vrfy import vrfy
import sys
import os
import argparse
from argparse import RawTextHelpFormatter
import pathlib
from inspect import signature


class vrfyCli:
    def __init__(self):
        pass

    def parseArgumentsAndExecute(self, arguments: list) -> int:
        """
        Decodes program arguments and executes required methods.

        Parameters:
            arguments (List[str]): List of arguments provided by user.

        Returns:
            int:    0, when all execution steps resulted in PASS, else 1.
        """
        # decode options from argument list
        parser = argparse.ArgumentParser(
            description="Verify with VRFY: Ensure the integrity of your file copies, hash by hash!",
            formatter_class=RawTextHelpFormatter)
        parser.add_argument("-ver", "--version", action="store_true", help="Print version string")
        parser.add_argument("-r", "--recursive", action="store_true", help="Recursive operation")
        parser.add_argument("-p", "--print", action="store_true", help="Print mismatched checksums")

        filevrfy = parser.add_argument_group('File verification',
                                             'Verify a single file against an expected')
        filevrfy.add_argument("-f", "--file", type=argparse.FileType('rb'), help="File to verify")
        filevrfy.add_argument("-cs", "--checksum", type=str,
                              help="Checksum string or sums.csv/*.sha256-file")

        csvrfy = parser.add_argument_group('Checksum verification', 'Verify files against stored checksums.'
                                            '\nError indicators:'
                                            '\n\t[+]: Additional files in directory that are missing in checksum list.'
                                            '\n\t[-]: Files that are included in checksum list, but missing in directory.'
                                            '\n\t[MISMATCH]: Checksums mismatch.')
        mcsvrfy = csvrfy.add_mutually_exclusive_group()  # required=True)
        mcsvrfy.add_argument("-v", "--verify", type=pathlib.Path, dest='VERIFY_PATH',
                               help="Path to files for verification")
        mcsvrfy.add_argument("-c", "--create", type=pathlib.Path, dest='CREATE_PATH',
                               help="Path to files to create checksums for")

        dirvrfy = parser.add_argument_group('Directory verification', 'Verify files against a known good master copy.'
                                            '\nError indicators:'
                                            '\n\t[+]: Additional files/directories in backup that are missing in master. '
                                            '\n\t[-]: Files/directories that are included in master, but missing in backup.'
                                            '\n\t[MISMATCH]: Checksums mismatch.')
        dirvrfy.add_argument("-m", "--master", type=pathlib.Path, dest='MASTER_PATH', help="Path to master directory")
        dirvrfy.add_argument("-b", "--backup", type=pathlib.Path, dest='BACKUP_PATH', 
                             help="Path to backup directory")

        args = parser.parse_args()

        # mutually exclude directory and file verification mode
        f = (args.file is not None or args.checksum is not None)
        d = (args.MASTER_PATH is not None or args.BACKUP_PATH is not None)
        vp = (args.VERIFY_PATH is not None)
        if (f + d + vp) > 1:
            print("ERROR: Verification modes can NOT be mixed.")
            return 1

        # check parameters for file verification mode
        if (args.MASTER_PATH is not None and args.BACKUP_PATH is None) or (
                args.MASTER_PATH is None and args.BACKUP_PATH is not None):
            print("ERROR: Parameter missing for 'directory verification'.")
            return 1

        self.OPTION_RECURSIVE = args.recursive
        self.OPTION_PRINT = args.print

        vf = vrfy()
        # execute decoded options
        executionResult = False

        # cli option: vrfy -version
        if args.version:
            print("vrfy version: " + str(vf.GetVersion()))

        # cli option: vrfy
        elif len(arguments) == 0:
            # no arguments are provided -> verify checksums of files within current working directory
            self.OPTION_VERIFY_CSV = True
            self.OPTION_RECURSIVE = True
            # verify sums
            print("Verifying current working directory against checksums:")
            executionResult = self.__walker__(os.getcwd(), os.getcwd(), vf.VerifyFilesAgainstChecksums)
            self.__printOverallResult__(executionResult)

        # cli option: vrfy -m <<directory>> -c <<directory>>
        elif args.MASTER_PATH is not None and args.BACKUP_PATH is not None:
            if os.path.isdir(args.MASTER_PATH) and os.path.isdir(args.BACKUP_PATH):
                print("Verifying directories:")
                print("Master: " + str(args.MASTER_PATH))
                print("Backup: " + str(args.BACKUP_PATH))
                self.OPTION_RECURSIVE = True
                executionResult = self.__walker__(str(args.MASTER_PATH), str(args.BACKUP_PATH), vf.VerifyFiles)
                self.__printOverallResult__(executionResult)
            else:
                print("ERROR: Unvalid argument " + str(args.MASTER_PATH) + " or " + str(args.BACKUP_PATH))

        # cli option: vrfy -f <<file>> -cs <<CHECKSUM>> OR vrfy -p -f <<file>> OR vrfy -p -f <<file>> -cs <<CHECKSUM>>
        elif args.file is not None:
            if os.path.isfile(args.file):
                if args.checksum is not None:
                    res = vf.VerifyFile(args.file.name, args.checksum)
                else:
                    res = vf.VerifyFile(args.file.name, "")
                executionResult = res.Result
                path, filename = os.path.split(args.file.name)
                calcChecksum = res.MasterChecksums[filename]
                if self.OPTION_PRINT:
                    print(calcChecksum + "  " + str(filename))
                else:
                    self.__printOverallResult__(executionResult)
            else:
                print("ERROR: Unvalid argument " + str(args.file))

        # cli option: vrfy -c <<directory>>
        elif args.CREATE_PATH is not None:
            if os.path.isdir(args.CREATE_PATH):
                # create sums
                print("Creating checksums for files:")
                executionResult = self.__walker__(str(args.CREATE_PATH), str(args.CREATE_PATH), vf.WriteChecksumFile)
                self.__printOverallResult__(executionResult)
            else:
                print("ERROR: Unvalid argument " + str(args.CREATE_PATH))

        # cli option: vrfy -v <<directory>>
        elif args.VERIFY_PATH is not None:
            if os.path.isdir(args.VERIFY_PATH):
                # verify sums
                print("Verifying files against checksums:")
                executionResult = self.__walker__(str(args.VERIFY_PATH), str(args.VERIFY_PATH),
                                                vf.VerifyFilesAgainstChecksums)
                self.__printOverallResult__(executionResult)
            else:
                print("ERROR: Unvalid argument " + str(args.VERIFY_PATH))

        else:
            print("No valid argument setting found!")
            return 1
        if executionResult:
            return 0
        else:
            return 1

    def __walker__(self, pathMaster: str, pathBackup: str, func) -> bool:
        """
        Verifies the contents of directory "pathMaster" against the included checksums in sums.csv.

        Parameters:
            pathMaster (str): Path to the master directory whose contents are considered valid and unchanged, serving as
                                a baseline for comparison. .
            pathBackup (str): Path to backup directory whose files shall get verified against the master copy.
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
        if os.path.isdir(pathBackup):
            filesC = [entryB for entryB in os.listdir(pathBackup) if not os.path.isdir(os.path.join(pathBackup, entryB))]
            dictsC = [entryDir for entryDir in os.listdir(pathBackup) if
                      os.path.isdir(os.path.join(pathBackup, entryDir))]

        combinedDicts = list(set(dictsM + dictsC))

        if os.path.isdir(pathMaster) and os.path.isdir(pathBackup):
            print(pathMaster, end=" : ", flush=True)
            # execute requested operation
            numParam = len(signature(func).parameters)
            if numParam == 2:
                resultObject = func(pathMaster, pathBackup)
            elif numParam == 1:
                resultObject = func(pathBackup)
            else:
                return False
        else:
            if os.path.isdir(pathMaster):
                print("[-] " + pathMaster, end=" : ", flush=True)
                #resultObject = vrfy.Result(False, pathMaster, additionalMaster=filesM, missingMaster=filesC)
                resultObject = func(pathMaster, pathBackup)
            if os.path.isdir(pathBackup):
                print("[+] " + pathBackup, end=" : ", flush=True)
                #resultObject = vrfy.Result(False, pathBackup, additionalMaster=filesM, missingMaster=filesC)
                resultObject = func(pathMaster, pathBackup)
        resultVerify = resultObject.Result
        # ResultList.append(resultObject)
        self.__printResult__(resultObject)

        # jump into child directories, if recursive operation is requested
        if self.OPTION_RECURSIVE:
            for nextFolder in combinedDicts:
                resultVerify = self.__walker__(os.path.join(pathMaster, nextFolder),
                                               os.path.join(pathBackup, nextFolder), func) & resultVerify

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
                print("- Backup: " + result.BackupChecksums[file])
        for file in result.AdditionalFiles:
            print("[+] " + str(file))
            if self.OPTION_PRINT:
                print("- cs: " + result.BackupChecksums[file])
        for file in result.MissingFiles:
            print("[-] " + str(file))
            if self.OPTION_PRINT:
                print("- cs: " + result.MasterChecksums[file])

    def __printOverallResult__(self, res: bool):
        if res:
            print("Overall: PASS")
        else:
            print("Overall: FAIL")


def main():
    verify = vrfyCli()
    sys.exit(verify.parseArgumentsAndExecute(sys.argv[1:]))


if __name__ == "__main__":
    main()
