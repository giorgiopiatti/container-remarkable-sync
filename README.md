# ReMarkable Sync - Container image

[![DockerHub Pulls](https://img.shields.io/docker/pulls/giorgiopiatti/remarkable-sync.svg)](https://hub.docker.com/r/giorgiopiatti/remarkable-sync) [![DockerHub Stars](https://img.shields.io/docker/stars/giorgiopiatti/remarkable-sync.svg)](https://hub.docker.com/r/giorgiopiatti/remarkable-sync) [![GitHub Stars](https://img.shields.io/github/stars/giorgiopiatti/container-remarkable-sync.svg?label=github%20stars)](https://github.com/giorgiopiatti/container-remarkable-sync/) [![GitHub Forks](https://img.shields.io/github/forks/giorgiopiatti/container-remarkable-sync.svg?label=github%20forks)](https://github.com/giorgiopiatti/container-remarkable-sync/) [![GitHub License](https://img.shields.io/github/license/giorgiopiatti/container-remarkable-sync.svg)](https://github.com/giorgiopiatti/container-remarkable-sync)

Sync your reMarkable tablet: import, export notebooks, pdf and epub to/from the local folder from/to the tablet over ssh maintaining the directory structure.

The idea is to synchronize a local folder on the PC with the ReMarkable tablet via ssh, without needing to act manually on each file and folder. A Library folder is used on the PC to save the original files, the notes and the annotated file using a normal directory structure. When the files are annotated on the ReMarkable they get converted to PDF with the suffix '.annot'. Notebooks are also converted to PDF with the suffix '.notes'.

### Example
- mybook.pdf (original file)
- myebook.epub (original file)
- mybook.annot.pdf (annotated file)
- mynotebook.notes.pdf (written notes)

## Usage

The script can be used via a container image (recommended way) or by installing the dependencies yourself.

To use the container is necessary to pass a volume to the container, which will contain your library folder, the container assumes is mapped to `/ReMarkable`. Note this folder will contain two subfolders `device` and `sync` the former contains a copy of the `xochil` and `templates` folders from the ReMarkable tabler, the latter is the synced library.

A sample usage is the following:

```
docker run -v PATH_TO_YOUR_LIBRARY:/ReMarkable --name=remarkable -it giorgiopiatti/remarkable-sync
```

The default mode is an interactive shell, but is also possible to execute it with command-line arguments:

- d: download files from the reMarkable tablet
- u: upload files to the reMarkable tablet
- e: export files to the Library folder (from the local copy of the reMarkable tablet)
- i: import files from the Library folder
- s: sync files (download)
- c: config program
- h: print program help
- q: quit the program

Before the first usage it's necessary to configure the program, please use the `c` option and follow the instructions. When using docker the configuration is saved when running multiples times.

## How it works

This script is based on the [rm2pdf](https://github.com/giorgiopiatti/rm2pdf) for converting the `.rm` files to pdf file.

It maintains a local copy of the internal user data directory located in `.local/share/remarkable/xochitl`, this is used when exporting and importing. This allows to run the program faster and not to have an incomplete structure on the ReMarkable. This script uses [rclone](https://github.com/rclone/rclone) to sync the `xochitl` folder from/to the reMarkable.

When uploading the file back on the reMarkable we need to restart the tablet, to prevent an accidental reboot the script ask your password.

## Known issues & improvements

- When syncing files to the ReMarkable they appear like they were modified 49 years ago.
- Deletion and renaming are a bit tricky, is not done automatically.
- The script could be faster. Each time it runs, it scans all files for modifications, so the runtime is <img src="https://latex.codecogs.com/gif.latex?\mathcal{O}(\text{\&hash;files})" title="\mathcal{O}(\text{\#files})" /> Further improvement could be an integration with an online could API, such that we listen to new changes.
