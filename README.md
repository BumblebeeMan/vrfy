# Verify with VRFY: Ensure the integrity of your file copies, hash by hash!

**UNDER CONSTRUCTION!!!** 


## Installation
Download the latest release from github and run the appropriate command:
### DNF (Fedora, RHEL, CentOS):
```bash
sudo dnf install vrfy-++version++.noarch.rpm
```
### Zypper (openSUSE):
```bash
sudo zypper install vrfy-++version++.noarch.rpm
```
 
## Usage
### Verifing that two directories are identical
Verifing that the contents of '/path/of/clone' are identical to those of '/path/of/master'. For example, '/path/of/master' might be a local backup, whereas '/path/of/clone' might be loaded from cloud storage. 
```bash
vrfy /path/of/master /path/of/clone
```
### Storing checksums for future verification
Creating a file that lists checksums for all files within a directory:
```bash
vrfy -c /path/of/data
```
Using **-r** (recursive) all in sub-directories as well:
```bash
vrfy -r -c /path/of/data
```
### Verifing files against stored checksums
Verifing that all files within a directory haven't been changed (i.e. their checksum still match):
```bash
vrfy -v /path/of/data
```
Using **-r** (recursive) all sub-directories are verified as well:
```bash
vrfy -r -v /path/of/data
```
