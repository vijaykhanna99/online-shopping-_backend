from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.services.user import UserService

userService = UserService()


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Create User
        """
        result = userService.sign_up(request)
        return Response(result, status=status.HTTP_200_OK)


class ClientSignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Create User
        """
        result = userService.client_sign_up(request)
        return Response(result, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Login
        """
        result = userService.login(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )
    """
    Logout
    """

    def post(self, request, format=None):
        result = userService.logout(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class PhoneVerification(APIView):

    def post(self, request, format=None):
        """
        Login With Phone
        """
        result = userService.phoneverification(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class OTPVerificationView(APIView):

    def post(self, request, format=None):
        """
        OTP Verification
        """
        result = userService.OTPVerification(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, format=None):
        """
        Forgot Password
        """
        result = userService.forgotpassword(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, token, format=None):
        """
        Forgot Password
        """
        result = userService.resetpassword(request, token, format=None)
        return Response(result, status=status.HTTP_200_OK)


class UserMeasurementView(APIView):
    # permission_classes = (AllowAny, )
    # print("measurement-1")

    def post(self, request, format=None):
        """
        User Measurement
        """
        result = userService.usermeasurement(request, format=None)
        return Response(result, status=status.HTTP_200_OK)

class UserMeasurementPdfView(APIView):

    def get(self, request, format=None):
        """
        User Measurement Pdf
        """
        result = userService.usermeasurementpdf(request, format=None)
        return result 

    
class UploadVideoView(APIView):
    # permission_classes = (AllowAny, )
    # print("measurement-1")

    def post(self, request, id, format=None):
        """
        Upload Video
        """
        result = userService.uploadVideo(request, id, format=None)
        return Response(result, status=status.HTTP_200_OK)


class Human3DView(APIView):
    def post(self, request, format=None):
        """
        Human 3D 
        """
        result = userService.human3dmodel(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class UserProfile(APIView):
    def put(self, request, format=None):
        result = userService.update_user_profile(request, format=None)
        return Response(result, status=status.HTTP_200_OK)

    def get(self, request, format=None):
        """
        User Profle
        """
        result = userService.get_user_profile(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class OrderView(APIView):
    def post(self, request, format=None):
        """
        Order View
        """
        result = userService.create_order(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class GetOrder(APIView):
    def get(self, request, format=None):
        """
        Get All Orders
        """
        result = userService.get_orders(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class UserAddress(APIView):
    def post(self, request, format=None):
        """
        Add address
        """
        result = userService.add_address(request, format=None)
        return Response(result, status=status.HTTP_200_OK)


class UserFeedback(APIView):
    def get(self, request, format=None):
        """
        Get User Feedback
        """
        result = userService.user_feedback_options(request, format=None)
        return Response(result, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        """
        Post User Feedback
        """
        result = userService.user_feedback(request, format=None)
        return Response(result, status=status.HTTP_200_OK)
    

class UserDelete(APIView):
    def delete(self, request, format=None):
        """
        Delete User
        """
        result = userService.user_delete(request, format=None)
        return Response(result, status=status.HTTP_200_OK)

class TryOnView(APIView):
    def get(self, request, format=None):
        """
        Try On
        """
        result = userService.user_tryon(request, format=None)
        return Response(result, status=status.HTTP_200_OK)
    

