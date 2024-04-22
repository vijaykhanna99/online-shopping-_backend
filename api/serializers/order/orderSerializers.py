from rest_framework import serializers
from api.models import *


class OrderSerializer(serializers.ModelSerializer):
    """
    Api to Get Order 
    """
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Api to Get Order Items 
    """
    class Meta:
        model = OrderItem
        exclude = ("id", "order")
