#! -*- encoding: utf-8 -*-

__author__ = 'wgx'

import os
import re
import sys
from xml.dom import minidom, Node


def delete_element(source_url, tag_names, back_dirs):
    """
        remove resources from file with tag_names, origin file will be saved in back_dirs
    """
    target_document = minidom.Document()
    xml_file = minidom.parse(source_url)
    root = xml_file.documentElement
    target_root = target_document.createElement('resources')

    for child in root.childNodes:
        child_str = child.toxml()

        # if element with the target tag and name then pass
        if child.nodeType == Node.ELEMENT_NODE and (child.tagName, child.getAttribute('name')) in tag_names:
            continue

        # if comment node then build the node
        if child.nodeType == Node.COMMENT_NODE:
            t_node = target_document.createComment(child.data)
            target_root.appendChild(t_node)
            continue

        # save any other things, blank text node probably
        try:
            if child_str.strip():
                t_node = minidom.parseString(child_str.strip().encode('utf-8'))
                target_root.appendChild(t_node.documentElement)
        except Exception as e:
            print e

    target_document.appendChild(target_root)

    target_string = target_document.toprettyxml(encoding='utf-8', indent='  ').decode('utf-8').encode('utf-8')

    # write to a temp file
    temp_file_path = './tmpfile'
    temp_file = open(temp_file_path, 'w')
    temp_file.write(target_string)

    # backup origin file, and save new file
    if not os.path.exists(back_dirs):
        os.system('mkdir -p ' + back_dirs)

    # save origin file
    target_backup_path = os.path.join(back_dirs, source_url.replace('/', '_'))

    # if never backup, then backup, else just backup the oldest ones
    if not os.path.exists(target_backup_path):
        os.system('mv ' + source_url + ' ' + target_backup_path)

    # replace origin file
    os.system('mv ' + temp_file_path + ' ' + source_url)


def delete_unused_values(p_source_path, p_force):
    """
        Run lint, find unused value, remove
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

    # File pattern
    file_pattern = re.compile('([A-Za-z0-9/_-]*res/values.*\.xml)')

    # XML node pattern
    xml_node_pattern = re.compile('(.*)<(?P<tag>[a-zA-Z|-]*)(.*)name="(?P<name>[a-zA-Z0-9|_]*)"(.*)')

    item_count = 0
    del_count = 0
    line = out_put_file.readline()
    last_file_path = ''
    node_tag_names = []
    backup_path = './backup_folder'
    while line:
        t_m_file = file_pattern.match(line)
        if t_m_file:
            print '------------------------------------------------'
            item_count += 1
            t_cur_file_path = t_m_file.group()
            print 'Value file path : ' + t_cur_file_path
            if t_cur_file_path != last_file_path:
                if last_file_path.strip():
                    delete_element(last_file_path, node_tag_names, backup_path)
                node_tag_names = []
                last_file_path = t_cur_file_path

            # Find file that contains unused item, then read the next line to get the xml element
            line = out_put_file.readline()
            print 'Unused item is : ' + line[:-1]
            t_m_node = xml_node_pattern.match(line)
            if t_m_node:
                t_node_dic = t_m_node.groupdict()
                t_node_dic_node = t_node_dic.get('tag', 'node cant read')
                t_node_dic_name = t_node_dic.get('name', 'name cant read')
                print 'Unused tag : ' + t_node_dic_node
                print 'Unused name : ' + t_node_dic_name

                if p_force:
                    del_count += 1
                    node_tag_names.append((t_node_dic_node, t_node_dic_name))
                else:
                    key = raw_input('delete ?, y or n:')
                    if key == 'y':
                        del_count += 1
                        print 'Remove unused node ' + t_node_dic_name
                        node_tag_names.append((t_node_dic_node, t_node_dic_name))
                    else:
                        print 'Skip unused node ' + t_node_dic_name
            print '-------------------------------------------------\n'

        line = out_put_file.readline()
    if last_file_path.strip():
        delete_element(last_file_path, node_tag_names, backup_path)

    print 'Total unused items : ' + str(item_count)
    print 'Deleted : ' + str(del_count)

    out_put_file.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Cmd should be like value_cleaner project_path [force], " \
              "if force the value will deleted without confirmation"
    else:
        force = False
        if len(sys.argv) >= 3 and sys.argv[2] == 'force':
            force = True
        delete_unused_values(sys.argv[1], force)

