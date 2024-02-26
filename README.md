# Console Script for File Organiser

The repository contains a command-line utility designed to organise and clean up specified directories by sorting files into categorised folders.

The script is particularly efficient in handling:

- Image Files: JPEG, PNG, JPG, SVG
- Video Files: AVI, MP4, MOV, MKV
- Documents: DOC, DOCX, TXT, PDF, XLSX, PPTX
- Audio Files: MP3, OGG, WAV, AMR
- Archives: ZIP, GZ, TAR
- Unknown Extensions: files with unrecognisable extensions

A key feature of this script is its file renaming capability. The normalize function is designed to transliterate Cyrillic characters to their Latin equivalents and to sanitise file names by replacing non-standard characters with underscores ('_'). This ensures compatibility across different operating systems and environments.
