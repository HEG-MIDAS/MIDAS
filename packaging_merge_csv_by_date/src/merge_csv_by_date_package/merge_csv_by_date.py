#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import re
import shutil

"""Provides merge_csv_by_date function to merge two csv files by date and dealing with conflicts.

merge_csv_by_date will take two paths leading respectively to the old file and to the new file that we want to merge.
It will proceed by date and inserting new lines chronoligicaly when the data was missing or overiding data if it was modified.
"""


def is_string_date(date_string: str, format_date: str) -> bool:
    """Test if a string is a date and return a boolean

    Parameters
    ----------
    date_string : str
        string to be cast
    format_date: str
        The format of the date that will be used
    
    Returns
    -------
    bool
        indicate if the string is a date or not
    """

    try:
        datetime.datetime.strptime(date_string, format_date)
    except:
        return False
    return True


def merge_csv_by_date(old_data_file_path: str, new_data_file_path: str, format_date: str) -> str:
    """Merge two csv files by comparing the lines beggining with a date in each file and
    overiding the old data by the new one if the line with the same date are not identical.
    Rewrites comments and header of the new data.
    Place the file merged at the same folder and with the same name as the old data file.

    Parameters
    ----------
    old_data_file_path : str
        The path of the file containing the old data
    new_data_file_path : str
        The path of the file containing the new data
    format_date: str
        The format of the date that will be used

    Return
    ------
    str
        a string with the path were the merged file was created, it is empty if it failed
    """

    if os.path.isfile(old_data_file_path):
        if os.path.isfile(new_data_file_path):
            # Open files and create arrays of splitted lines
            old_data_file = open(old_data_file_path, 'r')
            new_data_file = open(new_data_file_path, 'r')
            old_data_file_array = old_data_file.read().splitlines()
            new_data_file_array = new_data_file.read().splitlines()
            old_data_file.close()
            new_data_file.close()

            merged_data_file_array = []

            pos_old = 0
            pos_new = 0

            new_stopped = False
            old_stopped = False

            while pos_old != len(old_data_file_array) or pos_new != len(new_data_file_array):

                if pos_old == len(old_data_file_array):
                    old_stopped = True
                if pos_new == len(new_data_file_array):
                    new_stopped = True

                new_splitted_line = [''] if new_stopped else re.split('[,;]', new_data_file_array[pos_new])
                old_splitted_line = [''] if old_stopped else re.split('[,;]', old_data_file_array[pos_old])
                
                # Check that the first element of new or old splitted line is a date or that one has stopped and the one is a date
                if (is_string_date(new_splitted_line[0], format_date) and is_string_date(old_splitted_line[0], format_date)) or (is_string_date(new_splitted_line[0], format_date) and old_stopped) or (new_stopped and is_string_date(old_splitted_line[0], format_date)):
                    if (not old_stopped) and ((new_stopped and is_string_date(old_splitted_line[0], format_date)) or (datetime.datetime.strptime(new_splitted_line[0], format_date) > datetime.datetime.strptime(old_splitted_line[0], format_date))):
                        merged_data_file_array.append(old_data_file_array[pos_old])
                        pos_old += 1
                    elif (not new_stopped) and ((is_string_date(new_splitted_line[0], format_date) and old_stopped) or (datetime.datetime.strptime(new_splitted_line[0], format_date) < datetime.datetime.strptime(old_splitted_line[0], format_date))):
                        merged_data_file_array.append(new_data_file_array[pos_new])
                        pos_new += 1
                    elif datetime.datetime.strptime(new_splitted_line[0], format_date) == datetime.datetime.strptime(new_splitted_line[0], format_date):
                        merged_data_file_array.append(new_data_file_array[pos_new])
                        pos_new += 1
                        pos_old += 1
                else:
                    # Move indexes until it reaches the first line with a date at position 0

                    if (not is_string_date(new_splitted_line[0], format_date)) and not new_stopped:
                        # Write comments and header of the new file
                        merged_data_file_array.append(new_data_file_array[pos_new])
                        pos_new += 1
                    if (not is_string_date(old_splitted_line[0], format_date)) and not old_stopped:
                        pos_old += 1

                    
            merged_data_file = open(old_data_file_path, 'w')
            for line in merged_data_file_array:
                merged_data_file.write("{}\n".format(line))
            merged_data_file.close()
            return old_data_file_path

    elif os.path.isfile(new_data_file_path):
        shutil.copy(new_data_file_path, old_data_file_path)
        return old_data_file_path

    return ''
