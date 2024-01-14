from members.serializers import UserRegistrationSerializer, BroadCastSerializer
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .utils import generate_access_token
import jwt
from .models import *
from .serializers import UserSerializer, VerifyAccountSerializer, OtpPasswordSerializer, EmailSerializer
from .utils import send_email_to_user, send_otp
import pandas as pd
from django.conf import settings
import uuid
from django.core.exceptions import ObjectDoesNotExist


class UserRegistrationAPIView(APIView):
    serializer_class = UserRegistrationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        content = {'message': 'Hello!'}
        return Response(content)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data['password'] != serializer.validated_data['password_confirmation']:
                return Response('Passwords do not match', status=status.HTTP_400_BAD_REQUEST)
            phone = serializer.validated_data['phone_number']
            if len(phone) != 10:
                return Response('Enter 10 digit phone number', status=status.HTTP_400_BAD_REQUEST)
            if not phone.isnumeric():
                return Response('Please enter a valid phone number', status=status.HTTP_400_BAD_REQUEST)

            new_user = serializer.save()
            user_email = new_user.email
            send_email_to_user(email=user_email, subject="Your OTP for email verification", plain_message=new_user.otp)
            if new_user:
                access_token = generate_access_token(new_user)
                data = {'access_token': access_token}
                response = Response(data, status=status.HTTP_201_CREATED)
                response.set_cookie(key='access_token', value=access_token, httponly=True)
                return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    serializer_class = VerifyAccountSerializer

    def post(request):
        serializer = VerifyAccountSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp2 = serializer.validated_data['otp']
            user = User.objects.get(email=email)
            if user.otp != otp2:
                return Response(
                    {'message': 'Wrong OTP entered'}
                )
            user.is_verified = True
            send_email_to_user(user.email, "Registration Successful",
                               "You've successfully registered and verified for EES")
            return Response({
                'message': 'Successfully Verified'
            })


class UserLoginAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email', None)
        user_password = request.data.get('password', None)

        if not user_password:
            raise AuthenticationFailed('A user password is needed.')

        if not email:
            raise AuthenticationFailed('An user email is needed.')

        user_instance = authenticate(username=email, password=user_password)

        if not user_instance:
            raise AuthenticationFailed('User not found.')

        if user_instance.is_active:
            user_access_token = generate_access_token(user_instance)
            response = Response()
            response.set_cookie(key='access_token', value=user_access_token, httponly=True)
            response.data = {
                'access_token': user_access_token
            }
            return response

        return Response({
            'message': 'Something went wrong.'
        })


class UserViewAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_token = request.COOKIES.get('access_token')

        if not user_token:
            raise AuthenticationFailed('Unauthenticated user.')

        payload = jwt.decode(user_token, settings.SECRET_KEY, algorithms=['HS256'])

        user_model = get_user_model()
        user = user_model.objects.filter(user_id=payload['user_id']).first()
        user_serializer = UserRegistrationSerializer(user)
        return Response(user_serializer.data)


class UserLogoutViewAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_token = request.COOKIES.get('access_token', None)
        if user_token:
            response = Response()
            response.delete_cookie('access_token')
            response.data = {
                'message': 'Logged out successfully.'
            }
            return response
        response = Response()
        response.data = {
            'message': 'User is already logged out.'
        }
        return response


class ExportImportExcel(APIView):
    authentication_classes = (IsAdminUser)

    def get(self, request, format=None):
        user_objs = User.objects.all()
        serializer = UserSerializer(user_objs, many=True)
        df = pd.DataFrame(serializer.data)
        print(df)
        df.to_csv(f"C:/Users/Public/Documents/{uuid.uuid4()}.csv", encoding="UTF-8")

        return Response({'status': 200})


class BroadCastViewAPI(APIView):
    serializer_class = BroadCastSerializer
    authentication_classes = (IsAdminUser,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subject = serializer.validated_data['subject']
            for user in User.objects.all():
                email = user.email
                send_email_to_user(email, subject)

        response = Response()
        response.data = {
            'message': 'Something went wrong.'
        }
        return response


class ForgotPassword(APIView):
    serializer_class = EmailSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data["email"])

            except ObjectDoesNotExist:
                return Response({"error": " Email does not exist"}, status=status.HTTP_404_NOT_FOUND)

            otp1 = send_otp(user.email ,"Password Reset OTP")
            user.set_and_hash_otp(str(otp1))
            return Response({"Check Your Mail"})


class ChangePassword(APIView):
    serializer_class = OtpPasswordSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.data["email"])

            except ObjectDoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve the hashed OTP from the database and compare it
            if user.check_otp(serializer.data["otp"]):
                # OTP is correct, check and change the password
                if serializer.data["password1"] == serializer.data["password2"]:
                    user.set_password(serializer.data["password1"])
                    return Response({"success": "Password changed successfully"})

                return Response({"error": "Passwords do not match"})

            return Response({"error": "Wrong OTP entered"})
