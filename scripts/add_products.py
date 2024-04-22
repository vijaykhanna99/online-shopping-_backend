import csv
import os
from bould_backend import settings
from api.models.ProductsModel import *

def run():
    file_path = os.path.join(settings.STATIC_ROOT , 'files/products.csv')
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            try:
                product = products(
                    title=row['title'],
                    brand=row['brand'],
                    actual_price = int(row['actual_price'].replace('₹', '').replace(',', '')) if row['actual_price'] else 0,
                    sold_price = int(row['sold_price'].replace('₹', '').replace(',', '')) if row['sold_price'] else 0,
                    img_url=row['img'],
                    currency="INR",
                    enable_product=True,
                    stock_status=row.get('stock_status', 'In stock'),
                    size_range=row.get('size_range', 'Medium')
                )
                product.save()
            except Exception as e:
                print(e)
                break