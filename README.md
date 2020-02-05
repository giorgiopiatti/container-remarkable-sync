# ReMarkable sync container

This project features a sync system for the ReMarkable tablet.

The idea is to synchronize a local folder on the PC with the ReMarkable tablet via USB using ssh, without needing to act manually on each file and folder.

A Library folder is used on the PC to save the original files, the notes and the annotated file using a normal directory structure.

When the files are annotated on the ReMarkable they get converted to PDF with the suffix '.annot'. Notebooks are also converted to PDF with the suffix '.notes'.

### Example

- mybook.pdf (original file)
- mybook.annot.pdf (annotated file)
- mynotebook.notes.pdf (written notes)

## Usage

The script can be used via the containers (recommended way) or by installing the dependencies yourself.
The default mode is as interactive shell, but is also possible to execute it with command line arguments:

- d: download files from the ReMarkable tablet
- u: upload files to the ReMarkable tablet
- e: export files to the Library folder (from the local copy of the ReMarkable tablet)
- i: import files from the Library folder
- s: sync files (download)
- c: config program
- h: print program help
- q: quit program

Before the first usage it's necessary to configure the program, please use the c option and follow the instructions. When using docker the configuration is saved when running multiples times.

## How it works

This script is based on the rM2svg script by @peerdavid (https://github.com/peerdavid/rmapi/blob/master/tools/rM2svg) for converting the '.rm' files to svg vector.

It maintains a local copy of the internal user data directory located in '.local/share/remarkable/xochitl', this is used when exporting and importing. This allows to run the program faster and not to have an incomplete structure on the ReMarkable.

## Known issues & improvements

- When syncing files to the ReMarkable they appear like they were modified 49 years ago.
- Deletion and renaming is a bit tricky, is not done automatically.
- The script could be faster. Each time it runs, it scans all files for modifications, so the runtime is $\mathcal{O}(#files)$.
