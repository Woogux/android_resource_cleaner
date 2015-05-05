#! -*- encoding: utf-8 -*-

__author__ = 'wgx'

import re
import os
import sys


def delete_unused_files(file_paths, backup_path, force):
    """
        remove the files and backup in backup_path
    """
    del_count = 0
    if not os.path.exists(backup_path):
        os.system('mkdir -p ' + backup_path)
    for file_path in file_paths:
        try:
            if force:
                os.system('cp ' + file_path + ' ' + backup_path + '/' + file_path.replace('/', '_'))
                os.remove(file_path)
                del_count += 1
                print file_path + ' removed'
            else:
                key = raw_input('File to remove : ' + file_path + ' (y or n) ?')
                if key == 'y':
                    os.system('cp ' + file_path + ' ' + backup_path + '/' + file_path.replace('/', '_'))
                    os.remove(file_path)
                    print file_path + ' removed'
                    del_count += 1
                elif key == 'n':
                    print file_path + ' skipped'
        except KeyboardInterrupt:
            exit(1)

        except:
            print file_path + " didn't find"
    print 'Total   : ' + str(len(file_paths))
    print 'Removed : ' + str(del_count)


def find_unused_files(p_source_path, force):
    """
        Run lint, find unused files, remove
    """
    t_lint_log_name = 'outfile.lintlog'
    out_put_file_path = os.path.join(p_source_path, t_lint_log_name)

    if os.path.exists(out_put_file_path):
        os.remove(out_put_file_path)

    # Run lint cmd
    print 'Lint start...'
    os.system('lint --check UnusedResources ' + p_source_path + ' > ' + out_put_file_path)
    print 'Lint finished...'

    # Read lint output file
    print 'Reading lint logs..'
    out_put_file = open(out_put_file_path, 'r')

    file_pattern = re.compile('(.*)res/(drawable-?|layout-?)(.*)/([a-zA-Z0-9_]*\.xml)', re.IGNORECASE)
    line = out_put_file.readline()
    backup_path = './backup_folder'
    file_paths = []
    while line:
        t_m = file_pattern.match(line)
        if t_m:
            file_paths.append(os.path.join(p_source_path, t_m.group()))
        line = out_put_file.readline()
    delete_unused_files(file_paths, backup_path, force)
    out_put_file.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Cmd should be like file_cleaner project_path [force], " \
              "if force the value will deleted without confirmation"
    else:
        force = False
        if len(sys.argv) >= 3 and sys.argv[2] == 'force':
            force = True
        find_unused_files(sys.argv[1], force)
