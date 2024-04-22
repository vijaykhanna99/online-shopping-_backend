from bould_backend import settings
from api.models import *
from api.serializers import *
from .productsBaseService import ProductsBaseService
from rest_framework.views import Response
from rest_framework import status
from api.utils.messages.commonMessages import *
from api.utils.messages.productsMessages import *
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import subprocess, os


class ProductsService(ProductsBaseService):

    def __init__(self):
        pass

    def get_products(self, request, format=None):
        try:
            page = request.GET.get('page')
            category = None
            if request.GET.get('category'):
                category = categories.objects.get(
                    name=request.GET.get('category'))
            if category:
                products_obj = products.objects.filter(category=category)
            else:
                products_obj = products.objects.all()

            serializer = GetProductsSerializer(products_obj, many=True)
            if len(products_obj) > 10:
                p = Paginator(serializer.data, 10)
                page_data = list(p.page(page))
                return ({"data": page_data, "code": status.HTTP_200_OK, "message": PRODUCTS_FETCHED})
            elif len(products_obj) > 0:
                return ({"data": serializer.data, "code": status.HTTP_200_OK, "message": PRODUCTS_FETCHED})
            else:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": RECORD_NOT_FOUND})
            # return ({"data": serializer.data, "code": status.HTTP_200_OK, "message": PRODUCTS_FETCHED})

        except Exception as e:
            print(e)
            return ({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def add_product(self, request, format=None):
        try:
            data = request.data
            serializer = AddUpdateProductsSerializer(data=data)
            # print(serializer)
            if serializer.is_valid():
                serializer.save()
                return ({"data": serializer.data, "code": status.HTTP_201_CREATED, "message": PRODUCT_CREATED})
            return ({"data": serializer.errors, "code": status.HTTP_400_BAD_REQUEST, "message": BAD_REQUEST})
        except Exception as e:
            print(e)
            return ({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def update_product(self, request, id, format=None):
        try:
            product_obj = products.objects.filter(id=id).first()
            if not product_obj:
                return ({"code": status.HTTP_400_BAD_REQUEST, "message": RECORD_NOT_FOUND})
            serializer = AddUpdateProductsSerializer(
                product_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ({"data": serializer.data, "code": status.HTTP_200_OK, "message": PRODUCT_UPDATED})
            return ({"data": serializer.errors, "code": status.HTTP_400_BAD_REQUEST, "message": BAD_REQUEST})
        except Exception as e:
            print(e)
            return ({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def delete_product(self, request, id, format=None):
        try:
            product_obj = products.objects.filter(id=id).first()
            if not product_obj:
                return ({"code": status.HTTP_400_BAD_REQUEST, "message": RECORD_NOT_FOUND})
            product_obj.delete()
            return ({"code": status.HTTP_200_OK, "message": PRODUCT_DELETED})
        except Exception as e:
            print(e)
            return ({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def get_product_by_Id(self, request, id, format=None):
        try:
            product_obj = products.objects.get(id=id)
            serializer = GetProductsSerializer(product_obj)
            return {"data": serializer.data, "code": status.HTTP_200_OK, "message": PRODUCTS_FETCHED}
        except products.DoesNotExist:
            return {"code": status.HTTP_400_BAD_REQUEST, "message": RECORD_NOT_FOUND}
        except Exception as e:
            print(e)
            return {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR}

    def product3dView(self, request, id, format=None):
        try:
            images = uploads.objects.filter(product=id)
            serializer = GetProductsImages(images, many=True)
            file_field_list = [instance.thumbnail.url for instance in images]

            return {"data": file_field_list, "code": status.HTTP_200_OK, "message": IMAGES_FETCHED}
        except Exception as e:
            print(e)
            return {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR}

    def getCategories(self, request, format=None):
        try:
            data = []
            for i in categories.objects.all():
                data.append({"id": i.id, "name": i.name})
            return {"data": data, "code": status.HTTP_200_OK, "message": CATEGORIES_FETCHED}
        except Exception as e:
            print(e)
            return {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR}
    

    def upload_garments(self, request, format=None):
        try:
            try:
                blender_executable = '/home/priyanka/Downloads/blender-3.6.5-linux-x64/blender'
            except:
                blender_executable = '/home/ubuntu/blender/blender/blender'
            blender_script = f'{settings.BASE_DIR}/api/services/products/garment_upload.py'
            command = [blender_executable, '--background',
                        '--python', blender_script]
            result = subprocess.run(
                command, capture_output=True, text=True, check=True)
            if "Error" in result.stdout:
                print(result.stdout)
                return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})
        
    def combinations(self, request, format=None):
        try:
            try:
                current_product = products.objects.get(id=request.GET.get('product'))
            except products.DoesNotExist:
                    return {"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Product not found"}
            genders = ['male', 'female']
            human_sizes = ['skn', 'avg', 'fat', 'obs']
            garment_sizes = ['small']
            order = ['Headwear', 'Topwear', 'Bottomwear', 'Footwear', 'One Piece', 'Accessories']
            n = 1
            all_products = products.objects.all()#.exclude(id=request.GET.get('product'))
            n = 1
            blender_executable = '/home/ubuntu/blender/blender/blender' if os.path.exists('/home/ubuntu/blender/blender/blender') else '/home/priyanka/Downloads/blender-3.6.5-linux-x64/blender'

            blender_script = f'{settings.BASE_DIR}/api/services/products/combinations.py'
            with open(blender_script, 'r') as file:
                code = file.readlines()
            current_clo  = product_clo_3d.objects.get(product=current_product)
            for gender in genders:
                for size in human_sizes:
                    base_model_path = f"{settings.BASE_DIR}/media/tryon_models/{gender}_{size}.glb"
                    for garment_size in garment_sizes:
                        file_name = f"{current_product.title}_{gender[0]}_{size}_{garment_size}"
                        print(file_name)
                        current_model_file = settings.BASE_DIR + getattr(current_clo, f'{gender[0]}_{size}_{garment_size}', None).url
                        code[6] = f"filepaths = ['{current_model_file}','{base_model_path}']\n"
                        code[14] = f"name = '{file_name}.usdz'\n"
                        with open(blender_script, "w") as file:
                            file.write("".join(code))
                        command = [blender_executable, '--background', '--python', blender_script]
                        result = subprocess.run(command, capture_output=True, text=True, check=True)
            # for product in all_products:
            #     if current_product.category.type != product.category.type:
            #         product_clo  = product_clo_3d.objects.get(product=product)
                    
            #         for gender in genders:
            #             for size in human_sizes:
            #                 for i in garment_sizes:
            #                     for j in garment_sizes:
            #                         if order.index(current_product.category.type) > order.index(product.category.type):
            #                             p = f"{product.title}_{current_product.title}"
            #                             # current_model_file = getattr(current_clo, f'{gender}_{size}_{i}', None).url
            #                             # product_model_file = getattr(product_clo, f'{gender}_{size}_{j}', None).url
            #                             print(f"{n}: {p}_{gender}_{size}_{j}_{i}")
            #                         else:
            #                             p = f"{current_product.title}_{product.title}" 
            #                             # current_model_file = getattr(current_clo, f'{gender}_{size}_{j}', None).url
            #                             # product_model_file = getattr(product_clo, f'{gender}_{size}_{i}', None).url
            #                             print(f"{n}: {p}_{gender}_{size}_{i}_{j}")
            #                         command = [blender_executable, '--background', '--python', blender_script]
            #                         result = subprocess.run(command, capture_output=True, text=True, check=True)
            #                         n += 1



        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def get_backgrounds(self, request, format=None):
        try:
            backgrounds = background.objects.all()
            data = BackgroundSerializer(backgrounds, many = True).data
            return {"data": data, "code": status.HTTP_200_OK, "message": BACKGROUNDS_FETCHED}
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})
        
    def get_brands(self, request, format=None):
        try:
            brands = brand.objects.all()
            data = BrandSerializer(brands, many = True).data
            return {"data": data, "code": status.HTTP_200_OK, "message": BRANDS_FETCHED}
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})