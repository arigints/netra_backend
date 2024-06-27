import pandas as pd
from django.core.management.base import BaseCommand
from apps.models import CUConfig

class Command(BaseCommand):
    help = 'Import CU data from Excel file to Django models'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CU Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        df = pd.read_excel(file_path)

        # Print columns for debugging
        print("Columns in CUConfig file:", df.columns)

        # Rename columns to match model fields if necessary
        df.columns = ['cuId', 'cellId', 'f1InterfaceIPadd', 'f1cuPort', 'f1duPort', 'n2InterfaceIPadd', 
                      'n3InterfaceIPadd', 'mcc', 'mnc', 'tac', 'sst', 'amfhost']

        cu_objects = [
            CUConfig(
                cuId=row['cuId'],
                cellId=row['cellId'],
                f1InterfaceIPadd=row['f1InterfaceIPadd'],
                f1cuPort=row['f1cuPort'],
                f1duPort=row['f1duPort'],
                n2InterfaceIPadd=row['n2InterfaceIPadd'],
                n3InterfaceIPadd=row['n3InterfaceIPadd'],
                mcc=row['mcc'],
                mnc=row['mnc'],
                tac=row['tac'],
                sst=row['sst'],
                amfhost=row['amfhost']
            )
            for _, row in df.iterrows()
        ]

        CUConfig.objects.bulk_create(cu_objects)
        self.stdout.write(self.style.SUCCESS('Successfully imported CU data'))
