# ReMarkable sync container
Synchronization script for the reMarkable e-reader

Synchronization script for the reMarkable e-reader. The idea is to have a "Library" folder on your PC which is synchronized with the reMarkable. When new files appear in this local directory this script will push them over to the rM. When files are edited, created or annotated on the rM they get converted to .pdf (from .lines) and copied back to the Library folder (with the suffix ".annot").
Nootebooks are also converted to .pdf (with the suffix ".notes").
The folder structure of the "Library" is preserved when syncing with the reMarkable and viceversa.

This project is an improved version of the work of lschwetlick (https://github.com/lschwetlick/rMsync)
This repository is includes an improved version of the script https://github.com/lschwetlick/maxio/tree/master/tools.

### Example
- mybook.annot.pdf (annotated file)
- mybook.pdf (original file)
- mynotebook.notes.pdf (written notes)

## Requirements
- imagemagick
- pdftk
- rclone

You must adjust the paths at the top of the script to your setup before running!

## Usage
Before the first usage it's necessary to configure rclone, that handles the syncing of the ReMarkable folder between the PC and the tablet.
```
- rclone config
- Select new remote
name> remarkable
Storage> 23  #sftp
Host> YOUR_REMARKABLE_IP
user> root
port> 22
y/g/n> y #Save the password
... #Skip this or configure as you wish
- save the configuration

```
usage: sync.py [-b] [-c] [-u] [-d] [-s]

```
optional arguments:
  -b, --backup                        download files from the connected rM
  -c, --convert                       convert the backup lines files to annotated pdfs and notes
  -u, --upload                        upload new files from the library directory to the rM
  -d, --dry_upload                    runs upload function but without actually pushing anything (just for debugging)
  -s, --sync                          Sync data between the ReMarkable and the library folder
```

## Note:
You can also remove the last line of the sync method and reboot the device yourself (an UI update is needed to show the new synced files).

## Known issues

- When syncing files to the ReMarkable they appears like they were modified 49 years ago.
