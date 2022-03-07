#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides merge_csv_by_date function to merge two csv files by date and dealing with conflicts.

merge_csv_by_date will take two paths leading respectively to the old file and to the new file that we want to merge.
It will proceed by date and inserting new lines chronoligicaly when the data was missing or overiding data if it was modified.
"""

def my_function():
    print("Ez")


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
    
