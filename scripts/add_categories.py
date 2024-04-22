import csv
import os
from bould_backend import settings
from api.models.ProductsModel import *

def run():
    file_path = os.path.join(settings.STATIC_ROOT , 'files/categories.csv')
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            try:
                category = categories(name = row['class_name'])
                category.save()
            except Exception as e:
                print(e)
                break