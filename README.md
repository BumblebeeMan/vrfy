# Verify with VRFY: Ensure the integrity of your file copies, hash by hash!

When beginning to explore cloud storage (or other methods of remotely storing files), one may become concerned about file integrity at some point. When dealing with a large number of individual files, how can one be certain that no file becomes corrupted during the storage process, and that downloaded files remain identical to their uploaded versions? This concern is particularly relevant after undergoing multiple segmentation and encryption/decryption processes. It's impractical to manually verify all files, making file corruption a common worry, especially for those using smaller cloud providers. 

Those concerns are mitigated by using a small console application called **vrfy**. **vrfy** handles the heavy lifting and verifies the integrity of your backups for you!
With a single, easy command, you can:

1. Verify that copies are identical (i.e., all files are included in both locations, and -by using sha256 hash checksums- that not even a single bit was changed).
2. Create and store a file with sha256 hash checksums beside your data. This file can be backed up with your data and used for verification later.
3. Verify that your data is unchanged using the checksum file.

## Installation
### PIP: 
Install **vrfy** using pip:
```bash
pip install vrfy --user
```
 
## Usage
### 1. Verifing that two directories are identical
Verifing that the contents of '/path/of/clone' are identical to those of '/path/of/master'. For example, '/path/of/master' might be a local backup, whereas '/path/of/clone' might be loaded from cloud storage. 
```bash
vrfy /path/of/master /path/of/clone
```
or
```bash
vrfy -m /path/of/master -c /path/of/clone -r
```
or (checksums are printed to console)
```bash
vrfy -m /path/of/master -c /path/of/clone -r -p
```

### 2. Storing checksums for future verification
Creating a file that lists checksums for all files within a directory:
```bash
vrfy -c /path/of/data
```
Using **-r** (recursive) all in sub-directories as well:
```bash
vrfy -r -c /path/of/data
```

### 3. Verifing files against stored checksums
Verifying that all files within a directory haven't been changed (i.e., their checksums still match):
```bash
vrfy -v /path/of/data
```
Using option **-r** (recursive) all sub-directories are verified as well:
```bash
vrfy -r -v /path/of/data
```
Using option **-p** (print) all checksums are printed to console for further inspection:
```bash
vrfy -p -r -v /path/of/data
```
Verifying the current working directory and all its sub-directories:
```bash
vrfy
```
Verifying file against an expected checksum:
```bash
vrfy -f /path/of/file/filename -cs expectedChecksum
```
Where "expectedChecksum" can be one of the following:
- A string containing the expected sha256 hash digest.
- A *.sha256sum-file that includes the expected hash digest.
- A sums.csv-file created by **vrfy** that includes the expected hash digest.

### 4. Other CLI options
Display version of vrfy:
```bash
vrfy -version
```
Display checksum for given file:
```bash
vrfy -p -f /path/of/file/filename
```
