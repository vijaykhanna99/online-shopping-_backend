from rest_framework import serializers
from api.models import *


class UserMeasurementSerializer(serializers.ModelSerializer):
    """
    Api to Get Measurements
    """
    class Meta:
        model = user_measurement
        fields = "__all__"


class UserLoginSerializer(serializers.ModelSerializer):
    """
    Api to login user
    """

    class Meta(object):
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Api to Register user
    """
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Api for User Profile
    """
    user = UserLoginSerializer(read_only=True)

    class Meta:
        model = user_profile
        fields = "__all__"


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_profile
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = addresses
        exclude = ("id", "user")

class UserFeedback(serializers.ModelSerializer):
    class Meta:
        model = user_feedback
        fields = "__all__"
