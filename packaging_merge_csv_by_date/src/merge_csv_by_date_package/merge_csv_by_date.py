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


def is_string_date(date_string: str) -> bool:
    """Test if a string is a date and return a boolean

    Parameters
    ----------
    date_string : str
        string to be cast
    
    Returns
    -------
    bool
        indicate if the string is a date or not
    """

    try:
        if len(date_string) == 10:
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
        elif len(date_string) == 16:
            datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        elif len(date_string) == 19:
            datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        else:
            raise ValueError
    except:
        return False
    return True


def string_to_date(date_string: str) -> datetime.datetime:
    """Convert a string to a datetime object and return it. Raises an error if it can't be casted.

    Parameters
    ----------
    date_string : str
        string to be cast

    Returns
    -------
    datetime.datetime
        the date contained in the string passed in argument

    Raises
    ------
    ValueError
        if the string doesn't match any pattern of date convertion
    """

    try:
        if len(date_string) == 10:
            return datetime.datetime.strptime(date_string, '%Y-%m-%d')
        elif len(date_string) == 16:
            return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        elif len(date_string) == 19:
            return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        
        raise ValueError

    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")



def merge_csv_by_date(old_data_file_path: str, new_data_file_path: str) -> str:
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

            while pos_old != len(old_data_file_array) and pos_new != len(new_data_file_array):
                new_splitted_line = re.split('[,;]', new_data_file_array[pos_new])
                old_splitted_line = re.split('[,;]', old_data_file_array[pos_old])

                if is_string_date(new_splitted_line[0]) and is_string_date(old_splitted_line[0]):
                    if string_to_date(new_splitted_line[0]) > string_to_date(old_splitted_line[0]):
                        merged_data_file_array.append(old_data_file_array[pos_old])
                        pos_old += 1
                    elif string_to_date(new_splitted_line[0]) == string_to_date(old_splitted_line[0]):
                        merged_data_file_array.append(new_data_file_array[pos_new])
                        pos_new += 1
                        pos_old += 1
                    else:
                        merged_data_file_array.append(new_data_file_array[pos_new])
                        pos_new += 1
                else:
                    # Move index until it reaches the first line with a date at position 0
                    if not is_string_date(new_splitted_line[0]):
                        # Write comments and header of the new file
                        merged_data_file_array.append(new_data_file_array[pos_new])
                        pos_new += 1
                    # Move index until it reaches the first line with a date at position 0
                    if not is_string_date(old_splitted_line[0]):
                        pos_old += 1
                    

            merged_data_file = open(old_data_file_path, 'w')
            for line in merged_data_file_array:
                merged_data_file.write("{}\n".format(line))
            merged_data_file.close()
            #os.remove(new_data_file_path)
            return old_data_file_path

    elif os.path.isfile(new_data_file_path):
        shutil.copy(new_data_file_path, old_data_file_path)
        return old_data_file_path

    return ''
