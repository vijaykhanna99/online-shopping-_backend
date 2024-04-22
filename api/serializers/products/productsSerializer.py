from rest_framework import serializers
from api.models import *


class CategoriesSerializer(serializers.ModelSerializer):
    """
    Api to return categories
    """
    class Meta(object):
        model = categories
        exclude = ("created_at",)


class AddUpdateProductsSerializer(serializers.ModelSerializer):
    """
    Api to add or update the product
    """
    class Meta(object):
        model = products
        fields = '__all__'


class GetProductsSerializer(serializers.ModelSerializer):
    """
    Api to return all the Products
    """
    category = CategoriesSerializer()
    brand = serializers.SerializerMethodField()

    class Meta(object):
        model = products
        fields = '__all__'

    def get_brand(self,obj):
        return obj.brand.name

class GetProductsImages(serializers.ModelSerializer):
    """
    Api to return all the images of Products
    """

    class Meta(object):
        model = uploads
        fields = ('thumbnail',)

class BackgroundSerializer(serializers.ModelSerializer):
    """
    Api to return all the Backgrounds
    """
    class Meta(object):
        model = background
        fields = ('id', 'thumbnail')

class BrandSerializer(serializers.ModelSerializer):
    """
    Api to return all the Backgrounds
    """
    class Meta(object):
        model = brand
        fields = ('id', 'name', 'logo')


