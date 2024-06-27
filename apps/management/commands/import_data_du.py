import pandas as pd
from django.core.management.base import BaseCommand
from apps.models import DUConfig

class Command(BaseCommand):
    help = 'Import DU data from Excel file to Django models'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the DU Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        df = pd.read_excel(file_path)

        # Print columns for debugging
        print("Columns in DUConfig file:", df.columns)

        # Rename columns to match model fields if necessary
        df.columns = ['gnbId', 'duId', 'cellId', 'f1InterfaceIPadd', 'f1cuPort', 'f1duPort', 
                      'mcc', 'mnc', 'tac', 'sst', 'usrp', 'cuHost']

        du_objects = [
            DUConfig(
                gnbId=row['gnbId'],
                duId=row['duId'],
                cellId=row['cellId'],
                f1InterfaceIPadd=row['f1InterfaceIPadd'],
                f1cuPort=row['f1cuPort'],
                f1duPort=row['f1duPort'],
                mcc=row['mcc'],
                mnc=row['mnc'],
                tac=row['tac'],
                sst=row['sst'],
                usrp=row['usrp'],
                cuHost=row['cuHost']
            )
            for _, row in df.iterrows()
        ]

        DUConfig.objects.bulk_create(du_objects)
        self.stdout.write(self.style.SUCCESS('Successfully imported DU data'))
