from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.services.products import ProductsService

productsService = ProductsService()


class ProductsView(APIView):

    def get(self, request, format=None):
        """
        Get All Products
        """
        result = productsService.get_products(request, format=None)
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        Add Product
        """
        result = productsService.add_product(request, format=None)
        return Response(result, status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        """
        Update Product
        """
        result = productsService.update_product(request, id, format=None)
        return Response(result, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        """
        Delete Product 
        """
        result = productsService.delete_product(request, id, format=None)
        return Response(result, status=status.HTTP_200_OK)


class ProductByIDView(APIView):

    def get(self, request, id, format=None):
        """
        Get Product By Id
        """
        result = productsService.get_product_by_Id(request, id, format=None)
        return Response(result, status=status.HTTP_200_OK)


class Product3DView(APIView):
    def get(self, request, id, format=None):
        """
        Get 3D view of Product By Id
        """
        result = productsService.product3dView(request, id, format=None)
        return Response(result, status=status.HTTP_200_OK)


class CategoriesView(APIView):
    def get(self, request, format=None):
        """
        Get all categories
        """
        result = productsService.getCategories(request, format=None)
        return Response(result, status=status.HTTP_200_OK)
    

class uploadGarmentView(APIView):
    def post(self, request, format=None):
        """
        Upload Garment
        """
        result = productsService.upload_garments(request, format=None)
        return Response(result, status=status.HTTP_200_OK)

class combinations(APIView):
    def get(self, request, format=None):
        """
        Combinations
        """
        result = productsService.combinations(request, format=None)
        return Response(result, status=status.HTTP_200_OK)
    
class getBackgrounds(APIView):
    def get(self, request, format=None):
        """
        Backgrounds
        """
        result = productsService.get_backgrounds(request, format=None)
        return Response(result, status=status.HTTP_200_OK)
    
class getBrands(APIView):
    def get(self, request, format=None):
        """
        Brands
        """
        result = productsService.get_brands(request, format=None)
        return Response(result, status=status.HTTP_200_OK)
