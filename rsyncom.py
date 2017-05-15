#!/usr/bin/env python
import subprocess
import argparse
import os
import errno
import time
import sys

def quote(astr):
    mark = "\""
    return ''.join((mark, astr, mark))

def quoteall(strs):
    return (quote(astr) for astr in strs)

def genpath(pathlist):
    return "{" + ",".join((quote(path) for path in pathlist)) + "}"

def option(flag, typ):
    optmark = {"short":"-", "long":"--"}
    def genopt(*parameter):
        if typ == "short":
            return ''.join((optmark[typ],flag))
        elif typ == "long":
            return ''.join((optmark[typ], flag, "=", parameter[0]))
    return genopt

def make_folder(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def backup_path(path):
    return os.path.join(path, "backup_" + time.strftime("%Y%m%d_%H%M%S"))

def header(title, des):
    print("======", title, "======")
    print("Destination:", des)
    print("Start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

def callcmd(cmd, inpath, outpath):
    def addmoreopt(*special):
        return subprocess.call(list((cmd, inpath, outpath, *special)))
    return addmoreopt

def main():
    parser = argparse.ArgumentParser(description='Backup made easy with rsync')

    parser.add_argument('-d', dest="paths", nargs='*', default=[], required=False, help="Backup certain path to a destination. The last argument is the destination")

    parser.add_argument('-f', dest="path", nargs=1, default=None, required=False, help="Full system backup. One argument for the path to save the backup")
    args = parser.parse_args()

    # options
    general_full = option("aAX", "short")
    general_dest = option("az", "short")
    info = option("info", "long")
    exclude = option("exclude", "long")

    exclude_path = (
	"/dev/*",
	"/proc/*",
        "/sys/*",
        "/tmp/*",
        "/run/*",
        "/mnt/*",
        "/media/*",
        "/lost+found",
        "/home/.local/share/Trash/*",
        "/home/.thumbnails/*",
        "/home/.cache/chromium/*",
    )

    inpath_full = "/"
    tool = "rsync"

    def exclude_multi(*paths):
        return exclude(genpath(paths))

    backup_full = lambda path: callcmd(tool, inpath_full, path)(general_full(), info("progress2"), exclude_multi(path, *exclude_path))
    def backup_dest(inpath, outpath):
        return callcmd(tool, inpath, outpath)(general_dest(), info("progress2"), exclude_multi(outpath, *exclude_path))

    if args.path is None and args.paths:
    # not -f, but -d, backup specific paths
        outpath = backup_path(args.paths[-1])
        make_folder(outpath)
        for inpath in args.paths[:-1]:
            header("Backup " + inpath, outpath)
            backup_dest(inpath, outpath)
    elif args.path is not None and not args.paths:
    # -f, but not -d, full backup
        outpath = backup_path(args.path[0])
        make_folder(outpath)
        header("Full system backup", outpath)
        backup_full(outpath)
    elif args.path is not None and args.paths:
    # both -f and -d, conflict
        print("Conflict option: -d & -f")
main()
