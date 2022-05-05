#!/usr/bin/env python
#title           :logs_handler.py
#description     :Handle the logs files that are contained in the folder by retrying the request
#author          :David Nogueiras Blanco & Amir Alwash
#date            :04 May 2022
#version         :0.1.0
#usage           :python3 logs_handler.py
#notes           :none
#python_version  :3.9.2

import os

def main() -> None:
    print('Starting verification of logs')
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    for file in os.listdir(__location__):
        file_splitted = file.split('.')
        if file.endswith('.txt'):
            data_file = open(os.path.join(__location__, file), 'r')
            data_file_array = data_file.read().splitlines()
            data_file.close()
            if data_file_array != []:
                print('Checking logs of {}'.format(file_splitted[0]))
                dates_to_check = list(set(data_file_array))
                script_path = os.path.join(*[__location__, '..', file_splitted[0], '{}.py'.format(file_splitted[0].lower())])
                cnt_dates_successfully_requested = 0
                for dates in dates_to_check:
                    if os.system('python3 {} {}'.format(script_path, dates)) != 0:
                        break
                    cnt_dates_successfully_requested+=1

                with open(os.path.join(__location__, file), 'w') as f:
                    for dates in dates_to_check[cnt_dates_successfully_requested:]:
                        f.write('{}\n'.format(dates))
    
    print('Ending verification of logs')


if __name__ == '__main__':
    main()
