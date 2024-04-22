from django.urls import path, include, re_path
from api.views import *

app_name = 'api'

urlpatterns = [
    # get user data
    # update user data
    #


    # auth
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/phone_verification/',
         PhoneVerification.as_view(), name='phonelogin'),
    #     path('auth/login_with_phone/', PhoneVerification.as_view(), name='phonelogin'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/signup/client/', ClientSignupView.as_view(), name='client_signup'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/verify_otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('auth/profile/', UserProfile.as_view(), name="user_profile"),

    path('auth/forgotpassword/',
         ForgotPasswordView.as_view(), name="forgotpassword"),
    path('auth/resetpassword/<token>/',
         ResetPasswordView.as_view(), name="resetpassword"),

    # products
    path('products/categories/', CategoriesView.as_view(), name="get_categories"),
    path('products/get/', ProductsView.as_view(), name="get_products"),
    path('products/get/<int:id>/', ProductByIDView.as_view(),
         name="get_product_by_id"),
    path('products/add/', ProductsView.as_view(), name="add_product"),
    path('products/update/<int:id>/',
         ProductsView.as_view(), name="update_product"),
    path('products/delete/<int:id>/',
         ProductsView.as_view(), name="delete_product"),
    path('products/3d/<int:id>/', Product3DView.as_view(), name="product_3d_view"),
    path('products/upload-garment/', uploadGarmentView.as_view(), name="upload_garment"),
    path('products/combinations/', combinations.as_view(), name = "combinations"),
    path('products/backgrounds/', getBackgrounds.as_view(), name = "backgrounds"),
    path('products/brands/', getBrands.as_view(), name = "brands"),

    # user
    path('user/body-measurements/', UserMeasurementView.as_view(), name="user_measurement"),
    path('user/body-measurements/pdf/', UserMeasurementPdfView.as_view(), name="user_measurement_pdf"),
    path('user/upload-video/<int:id>/',
         UploadVideoView.as_view(), name="upload_video"),
    path('user/add-address/', UserAddress.as_view(), name="user_address"),
    path('user/human-3d/', Human3DView.as_view(), name="user_human_3d"),
    path('user/try-on/',TryOnView.as_view(), name="user_tryon"),
    path('user/order/', OrderView.as_view(), name='user_order'),
    path('user/feedback/',UserFeedback.as_view(), name='user_feedback'),
    path('user/delete/',UserDelete.as_view(), name="user_delete"),
    path('orders/', GetOrder.as_view(), name="get_orders")
]
