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
