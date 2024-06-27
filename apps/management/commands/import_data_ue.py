import pandas as pd
from django.core.management.base import BaseCommand
from apps.models import UEConfig

class Command(BaseCommand):
    help = 'Import UE data from Excel file to Django models'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the UE Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        df = pd.read_excel(file_path)

        # Print columns for debugging
        print("Columns in UEConfig file:", df.columns)

        # Rename columns to match model fields if necessary
        df.columns = ['multusIPadd', 'rfSimServer', 'fullImsi', 'fullKey', 'opc', 'dnn', 'sst', 'sd', 'usrp']

        ue_objects = [
            UEConfig(
                multusIPadd=row['multusIPadd'],
                rfSimServer=row['rfSimServer'],
                fullImsi=row['fullImsi'],
                fullKey=row['fullKey'],
                opc=row['opc'],
                dnn=row['dnn'],
                sst=row['sst'],
                sd=row['sd'],
                usrp=row['usrp']
            )
            for _, row in df.iterrows()
        ]

        UEConfig.objects.bulk_create(ue_objects)
        self.stdout.write(self.style.SUCCESS('Successfully imported UE data'))
