#!/bin/bash
# Run the Django management command to import CU data
python3 manage.py import_data_cu apps/management/data/cuconfig.xlsx
python3 manage.py import_data_du apps/management/data/duconfig.xlsx
python3 manage.py import_data_ue apps/management/data/ueconfig.xlsx