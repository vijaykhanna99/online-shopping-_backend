from functools import lru_cache
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from django.core.files.base import ContentFile
from django.utils import timezone
import secrets
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from twilio.rest import Client
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.contrib.auth.models import User
from bould_backend import settings
from api.models import *
from .userBaseService import UserBaseService
from rest_framework.views import Response
from rest_framework import status
from api.utils.messages.commonMessages import *
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout, authenticate
from api.serializers import *
from django.http import JsonResponse
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import get_template
import subprocess
from django.core.cache import cache
load_dotenv()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)


class UserService(UserBaseService):

    def __init__(self):
        pass
        # self.remover = Remover()

    @lru_cache(maxsize=1)
    def load_model(self):
        import tensorflow_hub as hub
        return hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")

    def send_mail(self, subject, message, to):
        from_email = settings.FROM_EMAIL

        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=(to,)
            )
            email.send()
            return True
        except ValidationError as e:
            raise e
        except Exception as e:
            raise Exception('Failed to send the password reset email.')

    def sign_up(self, request, format=None):
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        dob = request.data.get('dob')
        gender = request.data.get('gender')

        if not email or not first_name or not last_name or not password or not dob:
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "The request is missing a required parameter."})

        already_exists = CustomUser.objects.get_active_users(email=email).first()
        deleted_user = CustomUser.objects.get_deleted(email=email)
        if deleted_user:
            subject = ""
            message = ""
            self.send_mail(subject, message, email)
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "This email is deactivated"})
        if already_exists:
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Email already exists"})

        today = datetime.today()
        dob_date = datetime.strptime(dob, '%Y-%m-%d')

        age = today.year - dob_date.year - \
            ((today.month, today.day) < (dob_date.month, dob_date.day))
        is_adult = age >= 18

        if not is_adult:
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "User must me an adult"})

        hashed_password = make_password(password)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['username'] = email
            serializer.validated_data['password'] = hashed_password
            serializer.save()
            user = CustomUser.objects.get_active_users(email=serializer.data.get('email')).first()
            refresh = RefreshToken.for_user(user)
            user_details = serializer.data
            user_details['token'] = str(refresh.access_token),
            profile = user_profile.objects.create(
                user=user, date_of_birth=dob_date, gender=gender)
            return ({"data": user_details, "code": status.HTTP_201_CREATED, "message": "User Created Successfully"})
        else:
            return ({"data": serializer.errors, "code": status.HTTP_400_BAD_REQUEST, "message": BAD_REQUEST})

    def login(self, request, format=None):
        email = request.data['email']
        password = request.data['password']
        if not email or not password:
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message":  REQUIRED_PARAMETER})
        try:
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                user_obj = CustomUser.objects.get_active_users(email=email).first()
                try:
                    user_profile_obj = user_profile.objects.get(user=user_obj)
                except user_profile.DoesNotExist:
                    return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND}) 
                if user_profile_obj.deleted_at:
                    return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "User Not Found"})
                serializer = UserLoginSerializer(user_obj)
                refresh = RefreshToken.for_user(user)
                user_details = serializer.data
                user_details['token'] = str(refresh.access_token),
                return ({"data": user_details, "code": status.HTTP_200_OK, "message": "LOGIN_SUCCESSFULLY"})
            else:
                user = CustomUser.objects.get_active_users(email=email).first()
                if user:
                    return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Invalid Credentials"})
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "User Not Found"})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def logout(self, request, format=None):
        try:
            user = request.user
            if user.is_authenticated:
                logout(request)
                return ({"data": None, "code": status.HTTP_200_OK, "message": "LOGED OUT SUCCESSFULLY"})
            else:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND})
        except Exception as e:
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def phoneverification(self, request, format=None):
        
        try:
            user_obj = CustomUser.objects.get_active_users(id=request.user.id).first()
            phone = request.data['phone']
            country_code = request.data['country_code']
            phone_no = country_code + phone

            if not phone or not country_code or not phone_no:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "The request is missing a required parameter."})
            otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
            otp_already_sent = OTP.objects.filter(user=request.user)
            if not otp_already_sent:
                create = OTP.objects.create(otp=otp,  user=request.user)
            else:
                otp_obj = OTP.objects.get(user=request.user)
                otp_obj.otp = str(otp)
                otp_obj.save()

            profile = user_profile.objects.filter(user=request.user).update(
                country_code=country_code, phone_number=phone)

            message = client.messages \
                .create(
                    body=f'Your OTP is: {otp}',
                    from_='+12568263146',
                    to='+917478044999'
                )

            return ({"data": None, "code": status.HTTP_200_OK, "message": "OTP sent successfully"})

        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

        except CustomUser.DoesNotExist:
            return ({"code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND})

    def OTPVerification(self, request, format=None):
        try:
            user_obj = CustomUser.objects.get_active_users(id=request.user.id).first()
            already_verfied = user_profile.objects.filter(
                user=user_obj, phone_is_verified=True)
            if not already_verfied:
                otp = request.data.get('otp')
                phone = request.data.get('phone')
                country_code = request.data.get('country_code')

                if not otp:
                    return ({"code": status.HTTP_400_BAD_REQUEST, "message": "Otp is required"})

                tz = pytz.timezone('Asia/Kolkata')
                try:
                    otp_obj = OTP.objects.get(user=request.user, otp=otp)
                except OTP.DoesNotExist:
                    return ({"code": status.HTTP_400_BAD_REQUEST, "message": "Invalid OTP. Please try again"})

                current_time = datetime.now(tz)
                otp_send_time = otp_obj.created_at.astimezone(tz)
                link_expire_time = otp_obj.created_at.astimezone(
                    tz) + timedelta(minutes=5)
                if link_expire_time < current_time:
                    return {"code": status.HTTP_400_BAD_REQUEST, "message": "OTP expired."}
                else:
                    otp_obj.delete()
                    user_profile.objects.filter(
                        user=request.user).update(phone_is_verified=True)
                    return {"code": status.HTTP_200_OK, "message": "OTP validated successfully"}
            else:
                return ({"code": status.HTTP_400_BAD_REQUEST, "message": "Already verified"})
        except CustomUser.DoesNotExist:
            return ({"code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND})

    def send_password_reset_email(self, user):
        try:
            token = PasswordResetToken.objects.get(user=user)
            token.token = secrets.token_urlsafe(64)
            token.created_at = timezone.now()
            token.save()
            token_to_send = token.token
        except PasswordResetToken.DoesNotExist:
            new_token = secrets.token_urlsafe(64)
            token = PasswordResetToken.objects.create(
                user=user, token=new_token)
            token.created_at = timezone.now()
            token.save()
            token_to_send = new_token

        reset_link = f'https://api.bouldhq.com/api/auth/resetpassword/{token_to_send}'

        subject = 'Password Reset'
        message = f'Hi {user.first_name},\n\nYou have requested to reset your password. Please click the following link to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email.'
        status = self.send_mail(subject, message, user.email)
        return status

    def forgotpassword(self, request, format=None):
        
        user_email = request.data.get('email')
        try:
            user = CustomUser.objects.get_active_users(email=user_email).first()
            if not user:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND})

            self.send_password_reset_email(user)
            return ({"data": None, "code": status.HTTP_200_OK, "message": "Password reset email sent successfully"})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def resetpassword(self, request, token, format=None):
        try:
            tz = pytz.timezone('Asia/Kolkata')
            valid_token = PasswordResetToken.objects.get(token=token)
            current_time = datetime.now(tz)
            link_send_time = valid_token.created_at.astimezone(tz)
            link_expire_time = valid_token.created_at.astimezone(
                tz) + timedelta(hours=2)
            if link_expire_time < current_time:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Token is expired."})
            user_obj = valid_token.user
            new_password = request.data.get('password')
            if not new_password:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Please enter the new password"})
            if user_obj.check_password(new_password):
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "New password should be different from the current password."})
            user_obj.set_password(new_password)
            user_obj.save()
            valid_token.delete()
            return ({"data": None, "code": status.HTTP_200_OK, "message": "Password reset successful"})
        except PasswordResetToken.DoesNotExist:
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Invalid Token"})
        except Exception as e:
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def client_sign_up(self, request, format=None):
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        company_name = request.data.get('company_name')

        if not email or not first_name or not last_name or not password or not company_name:
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": REQUIRED_PARAMETER})

        already_exists = CustomUser.objects.get_active_users(email=email).first()

        if already_exists:
            return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Email already exists"})

        hashed_password = make_password(password)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['username'] = email
            serializer.validated_data['password'] = hashed_password
            serializer.save()
            user = CustomUser.objects.get_active_users(email=serializer.data.get('email')).first()
            refresh = RefreshToken.for_user(user)
            user_details = serializer.data
            user_details['token'] = str(refresh.access_token),
            profile = user_profile.objects.create(
                user=user, company_name=company_name)
            return ({"data": user_details, "code": status.HTTP_201_CREATED, "message": "User Created Successfully"})
        else:
            return ({"data": serializer.errors, "code": status.HTTP_400_BAD_REQUEST, "message": BAD_REQUEST})

    def usermeasurement(self, request, format=None):
        import rembg, tensorflow as tf
        def get_joints(image, size):
            image = tf.cast(tf.image.resize_with_pad(
                image, 192, 192), dtype=tf.int32)

            outputs = self.movenet(image)
            keypoints = outputs['output_0']

            lb = ["nose", "left eye", "right eye", "left ear", "right ear", "left shoulder", "right shoulder", "left elbow",
                "right elbow", "left wrist", "right wrist", "left hip", "right hip", "left knee", "right knee", "left ankle", "right ankle"]
            joints = {}
            count = 0
            for i in range(17):
                arr = np.array(keypoints[0][0][i])
                y = int(size * arr[0])
                x = int(size * arr[1])
                z = arr[2]
                joints[lb[i]] = (x, y, z)
                if z < 0.3  :
                    count += 1
            if count > 5 or joints['left shoulder'][0] - joints['right shoulder'][0] < 10:
                return None
            return joints

        def get_length(image, actual_height, p=0):
            
            joints = self.joints

            height = ((joints['left ankle'][1]-joints['left eye'][1]+24)*0.027)
            ratio = actual_height/height
            if p == 0:
                chest = ((joints['left shoulder'][0] -
                        joints['right shoulder'][0])*0.027)*ratio
                return chest

            image = tf.cast(tf.image.resize_with_pad(
                image, 640, 640), dtype=tf.int32)
            img2 = np.array(image[0])

            b = (joints['left hip'][1]-joints['left shoulder'][1])*p
            d = int(joints['left shoulder'][1]+b)

            # out = self.remover.process(Image.fromarray(
            #     (img2 * 255).astype(np.uint8)), type='map')
            # masked_image = np.array(out)
            img2_reshaped = np.squeeze(img2.astype(np.uint8))
            masked_image = rembg.remove(img2_reshaped)
            # Image.fromarray(masked_image).save("masked_image.png")
            flag = False
            line = []
            l = []
            for i in list(masked_image[d]):
                if i[3] > 0:
                    flag = True
                else:
                    flag = False
                    if l:
                        line.append(l)
                    l = []
                if flag:
                    l.append(i)
            max = 0
            for i in line:
                if len(i) > max:
                    max = len(i)

            return ratio*max*0.027

        def ellipse_circumference(a, b):
            circumference = 3.14 * (3 * (a + b) - ((3 * a + b) * (a + 3 * b))**0.5)
            return circumference

        def get_measurements(actual_height):
            lb = ["nose", "left eye", "right eye", "left ear", "right ear", "left shoulder", "right shoulder", "left elbow",
                "right elbow", "left wrist", "right wrist", "left hip", "right hip", "left knee", "right knee", "left ankle", "right ankle"]

            PX = 0.027
            self.joints = get_joints(self.front_image, 640)
            if not self.joints:
                return None
            joints = self.joints
            height = ((self.joints['left ankle'][1] -
                    self.joints['left eye'][1]+20)*0.027)
            RATIO = actual_height/height

            front_waist = get_length(self.front_image, actual_height, 0.66)

            hip_distance = (joints['left hip'][0] - joints['right hip'][0])*RATIO*PX
            
            if front_waist/2>hip_distance:
                front_waist = hip_distance*2    
            side_waist = get_length(self.side_image, actual_height, 0.66)

            front_chest = get_length(self.front_image, actual_height)
            side_chest = get_length(self.side_image, actual_height, 0.33)

            
            front_hip = get_length(self.front_image,actual_height,1)
            side_hip = get_length(self.side_image,actual_height,1)
            hip = ellipse_circumference(front_hip/2, side_hip/2)*0.70
            if side_waist>front_waist:
                side_waist = side_chest
            waist = ellipse_circumference(
                front_waist/2, side_waist/2)*0.7
            chest = ellipse_circumference(
                front_chest/2, side_chest/2)*0.7
            shoulder_to_waist = ((joints['left hip'][1]-joints['left shoulder'][1])*0.66)*RATIO*0.027
            neck = (waist/2)*0.85
            front_chest = ((joints['left shoulder'][0] -
                        joints['right shoulder'][0])*PX)*RATIO 
            shoulder = (front_chest- (neck/3.14))/2
            torso = ((joints['left hip'][1]-joints['left shoulder'][1])*PX)*RATIO
            shoulder_to_waist = torso*0.66
            waist_to_hip = torso - shoulder_to_waist
            inside_leg = ((joints['left ankle'][1]-joints['left hip'][1])*PX)*RATIO
            outside_leg = inside_leg + waist_to_hip
            bicep = ((joints["left elbow"][0]-joints["left shoulder"][0]) **
                    2 + (joints["left elbow"][1]-joints["left shoulder"][1])**2)**0.5
            arm = ((joints["left elbow"][0]-joints["left wrist"][0])**2 +
                (joints["left elbow"][1]-joints["left wrist"][1])**2)**0.5
            sleeve = ((bicep+arm)*PX)*RATIO

            return {"height": round(actual_height, 2), "shoulder": round(shoulder, 2), "sleeve": round(sleeve, 2), "waist": round(waist, 2), "chest": round(chest, 2),"neck":round(neck,2),"waist_to_hip":round(waist_to_hip,2),"hip":round(hip,2),"shoulder_to_waist":round(shoulder_to_waist,2),"front_chest":round(front_chest,2), "back_width":round(front_chest,2)+2.1, "inside_leg": round(inside_leg, 2),"outside_leg": round(outside_leg, 2)}
        
        try:
            self.model = self.load_model()
            self.movenet = self.model.signatures['serving_default']
            front_image = request.FILES['frontImage']
            side_image = request.FILES['sideImage']

            pil_image = Image.open(BytesIO(front_image.read()))
            pil_image2 = Image.open(BytesIO(side_image.read()))

            if pil_image.format == 'PNG' and pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            if pil_image2.format == 'PNG' and pil_image2.mode != 'RGB':
                pil_image2 = pil_image2.convert('RGB')

            self.front_image = tf.expand_dims(np.array(pil_image), axis=0)
            self.side_image = tf.expand_dims(np.array(pil_image2), axis=0)

            try:
                actual_height = float(request.data.get('height'))
            except:
                print("required parameter")
                return ({"data": None, "code": status.HTTP_200_OK, "message": REQUIRED_PARAMETER})

        
            user = request.user
            print(user.is_authenticated, not user.is_deleted)
            if user.is_authenticated and not user.is_deleted:
                measurements = get_measurements(actual_height)
                if not measurements:
                    print("Wrong posture")
                    return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": WRONG_POSTURE})

                if user_measurement.objects.filter(user=request.user):
                    user_measurement.objects.filter(user=request.user).update(
                        height=measurements['height'],
                        shoulder=measurements['shoulder'],
                        back_width=measurements['back_width'],
                        sleeve=measurements['sleeve'],
                        waist=measurements['waist'],
                        chest=measurements['chest'],
                        neck=measurements['neck'],
                        waist_to_hip=measurements['waist_to_hip'],
                        hip=measurements['hip'],
                        shoulder_to_waist=measurements['shoulder_to_waist'],
                        front_chest=measurements['front_chest'],
                        inside_leg=measurements['inside_leg'],
                        outside_leg=measurements['outside_leg'],
                    )
                else:
                    user_measurement.objects.create(
                        user=request.user,
                        height=measurements['height'],
                        shoulder=measurements['shoulder'],
                        back_width=measurements['back_width'],
                        sleeve=measurements['sleeve'],
                        waist=measurements['waist'],
                        chest=measurements['chest'],
                        neck=measurements['neck'],
                        waist_to_hip=measurements['waist_to_hip'],
                        hip=measurements['hip'],
                        shoulder_to_waist=measurements['shoulder_to_waist'],
                        front_chest=measurements['front_chest'],
                        inside_leg=measurements['inside_leg'],
                        outside_leg=measurements['outside_leg'],
                    )
                profile = user_profile.objects.get(user=request.user)
                if measurements['waist'] < 80:
                    size = "S"
                elif measurements['waist'] < 90:
                    size = "M"
                elif measurements['waist'] < 100:
                    size = "L"
                elif measurements['waist'] < 110:
                    size = "XL"
                else:
                    size = "XXL"
                profile.size = size
                profile.save()
                return ({"data": measurements, "code": status.HTTP_200_OK, "message": MEASUREMENT_FETCHED_SUCCESSFULL})

            else:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def uploadVideo(self, request, id, format=None):
        import cv2
        try:
            if request.method == 'POST' and 'video' in request.FILES:
                product = products.objects.get(id=id)
                video_file = request.FILES['video']

                fs = FileSystemStorage()
                filename = fs.save('temp/video.mp4', video_file)
                file_path = fs.path(filename)
                product.video = filename
                product.save()
                print("File saved at:", file_path)

                if not os.path.isfile(file_path):
                    return ({"data": None, "code": status.HTTP, "message": FILE_NOT_SAVED})

                cap = cv2.VideoCapture(file_path)

                if not cap.isOpened():
                    return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": COULD_NOT_OPEN_FILE})
                x = 2
                while True:
                    _, frame = cap.read()
                    if not _:
                        break
                    if x % 2 == 0:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        im = Image.fromarray(frame)
                        im.save(
                            settings.MEDIA_ROOT+f"/upload-media/{x//2}.jpeg")

                        instance = uploads(product=products.objects.get(id=id),
                                           thumbnail=f"upload-media/{x//2}.jpeg", user=request.user, media_file_name=f"{x//2}")
                        instance.save()
                    x += 1

                cap.release()
                cv2.destroyAllWindows()

                # fs.delete(filename)
                return ({"data": None, "code": status.HTTP_200_OK, "message": VIDEO_PROCESSED_SUCCESSFULLY})
            else:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": NO_VIDEO_FILE_UPLOADED})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def check_values(self, measurements):
        waist = 0
        weight = 0.5
        muscle = 0
        age = measurements['age'] 
        
        if age >= 60:
            age = 1
        elif age >= 22:
            div = 0.5/(60-22)
            age = 0.5 + (div*(age-22))
        elif age >= 12:
            div = (0.5-0.18)/(22-12)
            age = 0.18+ (div*(age-12))
        else:
            div = (0.18)/12
            age =  div*age

        if measurements['chest']-measurements['waist'] >=0:
            muscle = (measurements['chest']-measurements['waist']) *0.1
            if (measurements['chest']-measurements['waist']) *0.1 > 0.8:
                muscle = 0.8
        if measurements['waist']>85:
            waist = (measurements['waist']-80) *0.025
            if measurements['waist']>measurements['chest']:
                if measurements['waist']>100:
                    waist = 0.5
                    weight = 1
                    if measurements['gender'] == 'female':
                        waist = 0.3
                        muscle = 0.4
                else:
                    waist = 0.3
                    weight = 0.6
                    if measurements['gender'] == 'female':
                        waist = 0.15
                        muscle = 0.5
            
        elif measurements['waist'] < 70:
            weight = 0.4
        return age, muscle, weight, waist

    def human3dmodel(self, request, format=None):
        try:
            if not user_profile.objects.filter(user=request.user):
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND}) 
            
            try:
                blender_executable = '/home/ubuntu/blender/blender/blender'
                f = open(blender_executable,'r')
                f.close()
            except FileNotFoundError:
                blender_executable = '/home/priyanka/Downloads/blender-3.6.5-linux-x64/blender'
            try:
                gender = request.data.get('gender')
                height = float(request.data.get('height'))
                age = float(request.data.get('age'))
                waist = float(request.data.get('waist'))
                chest = float(request.data.get('chest'))
            except:
                return ({"data": None, "code": status.HTTP_200_OK, "message": REQUIRED_PARAMETER})
            
            
            blender_script = f'{settings.BASE_DIR}/api/services/user/model_generation.py'

            age, muscle, weight, waist = self.check_values({"age": age, "waist": waist, "chest": chest,"gender":gender.lower()})
            average_height = 167.64
            h_p = height/average_height

            text = [f"bpy.context.scene.mpfb_macropanel_age = {age}\n",
                    f"bpy.context.scene.mpfb_macropanel_muscle = {muscle}\n",
                    f"bpy.context.scene.stomach_stomach_pregnant_decr_incr = {waist}\n",
                    f"bpy.context.scene.mpfb_macropanel_weight = {weight}\n"]

            height = [
                f"bpy.context.object.scale[0] = {h_p}\n",
                f"bpy.context.object.scale[1] = {h_p}\n",
                f"bpy.context.object.scale[2] = {h_p}\n"
            ]
            with open(blender_script, 'r') as file:
                code = file.readlines()

            code[6] = f"bpy.context.scene.MPFB_NH_phenotype_gender = '{gender.lower()}'\n"
            code[11:15] = text
            code[21:24] = height
            code[41] = f"name = 'model_{user_profile.objects.get(user=request.user).id}.usdz'\n"
            f = open(blender_script, "w")
            f.write("".join(code))
            f.close()
            addon_name = 'mpfb'

            command = [blender_executable, '--background',
                       '--python', blender_script, '--addons', addon_name]
            name = f'model_{user_profile.objects.get(user=request.user).id}.usdz'

            if os.path.exists(os.path.join( settings.MEDIA_ROOT, f"models/{name}")):
                os.remove(os.path.join(settings.MEDIA_ROOT, f"models/{name}"))
            
            result = subprocess.run(
                command, capture_output=True, text=True, check=True)
            if "Error" in result.stdout:
                print(result.stdout)
                return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})
            return ({"data": None, "code": status.HTTP_200_OK, "message": HUMAN_MODEL_CREATED})

        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def get_user_profile(self, request, format=None):
        try:
            user = request.user
            if user.is_authenticated:
                try:
                    user_obj = user_profile.objects.get(user=user)
                except user_profile.DoesNotExist:
                    return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND}) 
                profileSerializer = UserProfileSerializer(user_obj)

                data = profileSerializer.data
                user_data = data['user']
                data.pop('user')
                data['first_name'] = user_data['first_name']
                data['last_name'] = user_data['last_name']
                data['email'] = user_data['email']
                try:
                    add_obj = addresses.objects.get(user=request.user)
                    add_serializer = AddressSerializer(add_obj)
                    add_data = add_serializer.data
                    data['address'] = add_data
                except:
                    pass

                try:
                    user_measure = user_measurement.objects.get(user=user)
                    measurementSerializer = UserMeasurementSerializer(
                        user_measure)
                    m = measurementSerializer.data
                    m.pop('user')
                    data['measurements'] = m
                except:
                    pass

                return ({"data": data, "code": status.HTTP_200_OK, "message": USER_DATA_FETCHED_SUCCESSFULL})
            else:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def update_user_profile(self, request, format=None):
        try:
            try:
                email = request.data.get('email')
                user = CustomUser.objects.get_active_users(email=email).first()
                if user and not email == request.user.email:
                    return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": EMAIL_EXISTS})
            except:
                pass
            user_obj = user_profile.objects.get(user=request.user)
            profile_serializer = UpdateProfileSerializer(
                user_obj, data=request.data, partial=True)
            user_serializer = UserLoginSerializer(
                request.user, data=request.data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()

            if "measurements" in request.data:
                measurements = user_measurement.objects.get(user=request.user)
                measure_serializer = UserMeasurementSerializer(
                    measurements, data=request.data['measurements'], partial=True)

                if measure_serializer.is_valid():
                    measure_serializer.save()

            if "address" in request.data:
                add_obj = addresses.objects.get(user=request.user)
                add_serializer = AddressSerializer(
                    add_obj, data=request.data.get('address'), partial=True)

                if add_serializer.is_valid():
                    add_serializer.save()
            if user_serializer.is_valid():
                user_serializer.save()

            return ({"data": self.get_user_profile(request)['data'], "code": status.HTTP_200_OK, "message": USER_DATA_UPDATED_SUCCESSFULL})

        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def create_order(self, request, format=None):
        try:
            try:
                products_list = request.data.get('products')
                # address = request.data.get('address')
            except:
                return ({"data": None, "code": status.HTTP_200_OK, "message": REQUIRED_PARAMETER})
            total_amount = 0
            for i in products_list:
                total_amount += products.objects.get(
                    id=i['id']).sold_price * i['quantity']
            address = addresses.objects.filter(user=request.user).first()
            if not address:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": "Address Not Found"})
            addressSerializer = AddressSerializer(address)
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                address=address
            )
            serializer = OrderSerializer(order)
            data = serializer.data
            items = []
            for i in products_list:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=products.objects.get(id=i['id']),
                    quantity=i['quantity'],
                    order_status='Confirmed'
                )
                item_serializer = OrderItemSerializer(order_item)
                items.append(item_serializer.data)
            data['items'] = items
            data['address'] = addressSerializer.data
            return ({"data": data, "code": status.HTTP_200_OK, "message": ORDER_PLACED})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def get_orders(self, request, format=None):
        try:
            orders = Order.objects.all()
            data = []
            for order in orders:
                serializer = OrderSerializer(order)
                serializer_data = serializer.data
                product_list = OrderItem.objects.filter(order=order)
                items = []
                for product in product_list:
                    item_serializer = OrderItemSerializer(product)
                    items.append(item_serializer.data)
                serializer_data['items'] = items
                addressSerializer = AddressSerializer(order.address)
                serializer_data['address'] = addressSerializer.data
                data.append(serializer_data)
            return ({"data": data, "code": status.HTTP_200_OK, "message": ORDER_DATA_FETCHED})

        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def add_address(self, request, format=None):
        try:

            street = request.data.get('street')
            city = request.data.get('city')
            state = request.data.get('state')
            postal_code = request.data.get('postal_code')
            country = request.data.get('country')
            phone_number = request.data.get('phone_number')
            request.data['user'] = request.user.id
            address_serializer = AddressSerializer(data=request.data)
            if address_serializer.is_valid():
                address_serializer.save(user=request.user)
            return ({"data": None, "code": status.HTTP_200_OK, "message": ADDRESS_CREATED_SUCCESSFULLY})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def usermeasurementpdf(self, request, format=None):
        from weasyprint import HTML,CSS
        try:
            template = get_template('measurement_pdf_view.html')
            user_measurements = user_measurement.objects.get(user=request.user)
            
            context = {"measure_ins": user_measurements}
            
            html_content = template.render(context)
            pdf_file = HTML(string=html_content,base_url=request.build_absolute_uri('/')).write_pdf(stylesheets=[CSS(string='@page { size:215mm 350.5mm; }')])
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
            return response
        
        except user_measurement.DoesNotExist:
            data = {'message': 'No measurement found for this user'}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            data = {'message': 'Internal Server Error'}
            return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def user_feedback_options(self, request, format=None):
        try:
            data = {
                "feedback_options":[
                    {"id":4, "option":"It was great!"},
                    {"id":3, "option":"Went good"},
                    {"id":2, "option":"It was fine"},
                    {"id":1, "option":"It could be better"},
                ],
                "app_rating_options":[
                    {"id": 5, "option": "😍"},
                    {"id": 4, "option": "🙂"},
                    {"id": 3, "option": "😐"},
                    {"id": 2, "option": "🙁"},
                    {"id": 1, "option": "😥"},
                ]
            }
            return ({"data": data, "code": status.HTTP_200_OK, "message": FEEDBACK_FETCHED_SUCCESSFULLY})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})
    
    def user_feedback(self, request, format=None):
        try:
            overall_experience = request.data.get('overall_experience')
            input_feedback = request.data.get('input_feedback')
            scan_feedback = request.data.get('scan_feedback')
            fit_satisfaction = request.data.get('fit_satisfaction')
            app_rating = request.data.get('app_rating')
            request.data['user'] = request.user.id
            if overall_experience or input_feedback or scan_feedback or fit_satisfaction or app_rating:
                serializer = UserFeedback(data=request.data)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    return ({"data": serializer.data, "code": status.HTTP_200_OK, "message": FEEDBACK_CREATED_SUCCESSFULLY})
                else:
                    raise serializer.errors
            else:
                return ({"data":None, "code": status.HTTP_400_BAD_REQUEST,"message":"Empty Parameters"})
            
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})

    def user_delete(self, request, format=None):
        try:
            try:
                user_obj = user_profile.objects.get(user=request.user)
            except user_profile.DoesNotExist:
                return ({"data": None, "code": status.HTTP_400_BAD_REQUEST, "message": USER_NOT_FOUND}) 
            request.user.soft_delete()
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f%z")[:-3]
            user_obj.deleted_at = formatted_datetime
            user_obj.save()
            
            return ({"data": None, "code": status.HTTP_200_OK, "message": USER_DELETED_SUCCESSFULLY})
        except Exception as e:
            print(e)
            return ({"data": None, "code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": INTERNAL_SERVER_ERROR})
    
    def user_tryon(self, request, format=None):
        def calculate_size(user_m):
            if user_m.waist < 80:
                size = "small"
                result = "s"
            elif user_m.waist < 90:
                size = "medium"
                result = "m"
            elif user_m.waist < 100:
                size = "large"
                result = "l"
            elif user_m.waist < 110:
                size = "xlarge"
                result = "xl"
            else:
                size = "xxlarge"
                result = "xxl"
            return size, result

        try:
            # checking if the user measurement is available
            try:
                user_m = user_measurement.objects.get(user=request.user)
            except user_measurement.DoesNotExist:
                return {
                    "data": None,
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "User Measurement not found",
                }

            order = [
                "Headwear",
                "Topwear",
                "Bottomwear",
                "Footwear",
                "One Piece",
                "Accessories",
            ]
            user_obj = user_profile.objects.get(user=request.user)
            gender = user_obj.gender.lower()
            products_list = request.GET.getlist("product")
            garment_sizes = request.GET.getlist("size", None)
            human_size, gar = calculate_size(user_m)
            types = []
            ids = []
            for product_id in products_list:
                try:
                    product = products.objects.get(id=int(product_id))
                except products.DoesNotExist:
                    return {
                        "data": None,
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Product not found",
                    }

                product_type = product.category.type
                if product_type in types:
                    index = types.index(product_type)
                    types.pop(index)
                    ids.pop(index)
                if product_type == "One Piece":
                    for i in ["Topwear", "Bottomwear"]:
                        if i in types:
                            index = types.index(i)
                            types.pop(index)
                            ids.pop(index)
                elif product_type == "Topwear" or product_type == "Bottomwear":
                    if "One Piece" in types:
                        index = types.index("One Piece")
                        types.pop(index)
                        ids.pop(index)
                types.append(product_type)
                ids.append(product_id)
            products_list = ids.copy()
            if not garment_sizes or garment_sizes[0].lower() == 'default':
                garment_sizes = [gar] * len(products_list)
            else:
                garment_sizes = [request.GET.get("size").lower()] * len(products_list)
            name = ""
            g = ""
            for i in order:
                for k, j in enumerate(products_list):
                    if i == products.objects.get(id=j).category.type:
                        name += products.objects.get(id=j).title + "_"
                        g += garment_sizes[k] + "_"
                        break
            name = name.replace(" ", "_").lower()
            background_id = request.GET.get("background")
            is_background = False
            # Check if the background is available
            try:
                if background_id:
                    background_path = (
                        settings.BASE_DIR
                        + background.objects.get(id=int(background_id)).model.url
                    )
                    is_background = True
                else:
                    background_id = 1

            except background.DoesNotExist:
                return {
                    "data": None,
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Background not found",
                }

            file_name = f"{name}{gender[0]}_{human_size}_{g[:-1]}_b{background_id}"
            model_data = cache.get(file_name)

            file_path = settings.BASE_DIR + "/media/combinations/" + file_name + ".usdz"
            if model_data or os.path.exists(settings.BASE_DIR + "/media/combinations/" + file_name + ".usdz"):
                if model_data:
                    with open(file_path, "wb") as file:
                        file.write(model_data)
                output_path = (
                    f"https://api.bouldhq.com/media/combinations/{file_name}.usdz"
                )
            else:
                # Get product IDs and background ID from the request

                result = ""
                text = []
                for product_id, garment_size in zip(products_list, garment_sizes):
                    # Check if the product is available
                    product = products.objects.get(id=int(product_id))
                    clo_model = product_clo_3d.objects.filter(product=product).first()
                    # checking the closest group of size
                    clo_model_file = ""

                    if user_m.waist < 80:
                        result = "small"
                        clo_model_file = (
                            getattr(
                                clo_model, f"{gender[0]}_small_{garment_size}", None
                            ).url
                            if clo_model
                            and getattr(
                                clo_model, f"{gender[0]}_small_{garment_size}", None
                            )
                            else None
                        )

                    elif user_m.waist < 90:
                        result = "medium"
                        clo_model_file = (
                            getattr(
                                clo_model, f"{gender[0]}_medium_{garment_size}", None
                            ).url
                            if clo_model
                            and getattr(
                                clo_model, f"{gender[0]}_medium_{garment_size}", None
                            )
                            else None
                        )

                    elif user_m.waist < 100:
                        result = "large"
                        clo_model_file = (
                            getattr(
                                clo_model, f"{gender[0]}_large_{garment_size}", None
                            ).url
                            if clo_model
                            and getattr(
                                clo_model, f"{gender[0]}_large_{garment_size}", None
                            )
                            else None
                        )

                    elif user_m.waist < 110:
                        result = "xlarge"
                        clo_model_file = (
                            getattr(
                                clo_model, f"{gender[0]}_xlarge_{garment_size}", None
                            ).url
                            if clo_model
                            and getattr(
                                clo_model, f"{gender[0]}_xlarge_{garment_size}", None
                            )
                            else None
                        )

                    else:
                        result = "xxlarge"
                        clo_model_file = (
                            getattr(
                                clo_model, f"{gender[0]}_xxlarge_{garment_size}", None
                            ).url
                            if clo_model
                            and getattr(
                                clo_model, f"{gender[0]}_xxlarge_{garment_size}", None
                            )
                            else None
                        )

                    if not clo_model_file:
                        return {
                            "data": None,
                            "code": status.HTTP_400_BAD_REQUEST,
                            "message": f"Model not available for your size",
                        }

                    clo_model_file_path = settings.BASE_DIR + clo_model_file
                    text.append(clo_model_file_path)
                base_model_path = (
                    f"{settings.BASE_DIR}/media/tryon_models/{gender}_{result}.glb"
                )
                text.append(base_model_path)
                # Check Blender executable path
                blender_executable = (
                    "/home/ubuntu/blender/blender/blender"
                    if os.path.exists("/home/ubuntu/blender/blender/blender")
                    else "/home/priyanka/Downloads/blender-3.6.5-linux-x64/blender"
                )

                blender_script = f"{settings.BASE_DIR}/api/services/user/model_tryon.py"
                with open(blender_script, "r") as file:
                    code = file.readlines()

                output_path = f"https://api.bouldhq.com/media/tryon_models/base_{request.user.id}.usdz"
                if is_background:
                    text.append(background_path)
                else:
                    text.append(settings.BASE_DIR + "/media/backgrounds/default.glb")
                code[10] = f"filepaths = {text}\n"
                code[18] = f"name = 'base_{request.user.id}.usdz'\n"
                with open(blender_script, "w") as file:
                    file.write("".join(code))
                # Run Blender script
                command = [blender_executable, "--background", "--python", blender_script]
                result = subprocess.run(command, capture_output=True, text=True, check=True)

                if "error" in result.stdout:
                    print(result.stdout)
                file_path = settings.BASE_DIR + f"/media/tryon_models/base_{request.user.id}.usdz"
                with open(file_path, "rb") as file:
                    model_data = file.read()
                cache.set(file_name, model_data, timeout=600)

            return {
                "data": output_path,
                "code": status.HTTP_200_OK,
                "message": "Tryon Model Fetched",
            }
        except Exception as e:
            print(e)
            return {
                "data": None,
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": INTERNAL_SERVER_ERROR,
            }        
    