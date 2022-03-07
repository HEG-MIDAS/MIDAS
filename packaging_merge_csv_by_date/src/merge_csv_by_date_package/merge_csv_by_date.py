#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

"""Provides merge_csv_by_date function to merge two csv files by date and dealing with conflicts.

merge_csv_by_date will take two paths leading respectively to the old file and to the new file that we want to merge.
It will proceed by date and inserting new lines chronoligicaly when the data was missing or overiding data if it was modified.
"""

def my_function():
    print("Ez")


def is_string_date(date_string: str) -> bool:
    """Test if a string is a date and return a boolean

    Parameters
    ----------
    date_string : str
        string to be cast
    """
    try:
        if len(date_string) == 6:
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
        elif len(date_string) == 12:
            datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    except:
        return False
    return True


def string_to_date(date_string: str) -> datetime.datetime:
    """Convert a string to a datetime object and return it. Raises an error if it can't be casted

    Parameters
    ----------
    date_string : str
        string to be cast
    """
    try:
        if len(date_string) == 6:
            date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
        elif len(date_string) == 12:
            date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")
    return date



def merge_csv_by_date(old_data_file_path: str, new_data_file_path: str) -> None:
    """Merge two csv files by comparing the lines in each file and
    overiding the old data by the new one if the line with the same date are not identical.

    Parameters
    ----------
    old_data_file_path : str
        The path of the file containing the old data
    new_data_file_path : str
        The path of the file containing the new data
    """
    old_data_file = open(old_data_file_path, 'r')
    new_data_file = open(new_data_file_path, 'r')
    merged_data_file = open("merged_data_file_tmp.csv", 'w')


