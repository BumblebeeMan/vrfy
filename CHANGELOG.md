# Changelog

All important changes to vrfy will be documented here.

## [0.4.x]

### Added
- Added command line help menu "vrfy -h".

### Changed
- Code refactor: Separate CLI and core functionality, introduce data type for result post-processing, and code simplification.
- Moved cli from vrfy into own class.
- Cli option: vrfy /path/of/master /path/of/backup no longer supported.
- Renamed "clone" to "backup" for improved clarity.
- Changed direction verification option -c to -b.

### Fixed
- Fixed bug where directories may be dropped in directory verification.

## [0.3.1]

### Added
- n/a

### Changed
- n/a

### Fixed
- Fix crash when option -v is used on directory without checksum file. 

## [0.3.0]

### Added
- OS independence: Removed linux specific file operation.
- Added option -p to print checksums during verification.
- Added option -cs to verify single file (-f) against (a) checksum string, (b) checksum within sums.csv, or (c) checksum within *.sha256sum-file.

### Changed
- Changed output messages.
- Improved comments.

### Fixed
- Bugfixes / improved stability.
