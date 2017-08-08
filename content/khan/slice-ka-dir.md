## Manipulate Ka-lite Videos
#### Situation
* Khan Accademy vidoes are posted on YouTube in a verbose format that does not fit on SD cards well.
* There are resized videos available on bittorrent which conserve space.
* The tool in Ka-lite for selecting videso does not know about the resized sizes, and fetches vides that are larger than they need to be.

#### Slice-ka-dir program provides tools for selecting, and copying selected files, to a SD card.
The following help is available at the commant line:
```
root@box:~/./slice-ka-dir -h

usage: slice-ka-dir [-h] [-s SRC_DIR] [-d [DEST_DIR]] [-p FILENAME] [-v]
                    [-w WORK_DIR] [-l LANG] [-f]

Summarize or Slice Kalite Videos in a directory. List topics, and sizes for
top part of Khan topic tree, or paths listed in "path.list" file. (or copy
them)

optional arguments:
  -h, --help            show this help message and exit
  -s SRC_DIR, --src SRC_DIR
                        get video availability, and sizes from this directory
                        -(default: current working directory
  -d [DEST_DIR], --dest [DEST_DIR]
                        copy videos --requires -p, overrides -v -(default:
                        /library/ka-lite/content)
  -p FILENAME, --path_list FILENAME
                        the full, or relative, path to the text file
                        containing list of paths. Required to output youtube
                        ID list, or copy videos -(default: whole topic tree
                        starting with "khan/"
  -v, --video           Instead, output video id list (repuires -p)
  -w WORK_DIR, --work WORK_DIR
                        copy the KA database here, and update private copy
                        with current video sizes -(default: SRC_DIR)
  -l LANG, --lang LANG  language to select -(default: en)
  -f, --force           If -d, copy even if target exists. If not -d (not a
                        copy), force regeneration of local database and file
                        sizes.
```
### Recipe 
1. Copy the slice-ka-dir script to the directory containing the downloaded vides, or specify it with the -s option.
1. Without any additional options specified, the script will generate size report for the first 3 levels of the topic tree.
1. Redirect this listing to a file and edit the file by deleting the topics that are not wanted:
```
root@box:~# ./slice-ka-dir -s ~/kadownloads > kalist
root@box:~# vim kalist
root@box:~# cat kalist (after deleting the unwanted topics)

khan/math/algebra-basics/ 382.59M
khan/math/arithmetic/ 368.82M
khan/math/basic-geo/ 182.24M
khan/math/early-math/ 147.81M
khan/math/pre-algebra/ 542.86M

```
4. Verify that the size of the selected files is as you expect by using the -p option to specify the name of the file containing the edited list of paths.
```
root@box:~# ./slice-ka-dir -s ~/kadownloads -p kalist
# Name of file containing list of Topics(paths):kalist
khan/math/algebra-basics/ 392.00M 392.82M
khan/math/arithmetic/ 373.72M 374.70M
khan/math/basic-geo/ 185.83M 186.21M
khan/math/early-math/ 148.88M 149.28M
khan/math/pre-algebra/ 552.17M 553.64M
# Total file size discounting topic overlap:1.21G, including block size:1.21G
```
5. Then copy the selected subset of the ka-lite vides to the target. In my case, I usually mount the rpi SD card to /mnt:
```
root@box:~# ./slice-ka-dir -s ~/kadownloads -p kalist -d /mnt/library/ka-lite/content
 
# Name of file containing list of Topics(paths):spec
Copying videos in path: khan/math/algebra-basics/
Copying videos in path: khan/math/arithmetic/
Copying videos in path: khan/math/basic-geo/
Copying videos in path: khan/math/early-math/
Copying videos in path: khan/math/pre-algebra/
# Total file size discounting topic overlap:1.21G, including block size:1.21G
```
I've found it difficult to match exactly calculated sizes with what actually happens. du -sh of this copy yields 1.34G, rather than 1.21G (and I cannot believe that file size and size on disk, including unused parts of last blocks, can be the same. So there's more work to do to get the the bottom of it.


