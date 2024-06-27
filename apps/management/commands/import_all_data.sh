#!/bin/bash

# Run the Django management command to import CU data
python ../../../manage.py import_data_cu ../data/cuconfig.xlsx
python ../../../manage.py import_data_du ../data/duconfig.xlsx
python ../../../manage.py import_data_ue ../data/ueconfig.xlsx

