import random
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import OTPCode, Notification
from accounts.models import User
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, ResetPasswordSerializer, NotificationSerializer, MessageSerializer
from drf_spectacular.utils import extend_schema

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = str(random.randint(1000, 9999))
            print(f"Generating OTP {otp} for {email}")
            
            # Save OTP to database
            try:
                OTPCode.objects.create(email=email, code=otp)
            except Exception as e:
                return Response({
                    "error": "Database error: table might be missing.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Send Email (Try to send, but don't crash if it fails)
            try:
                send_mail(
                    'Your Password Reset OTP',
                    f'Your OTP is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"SMTP Error for {email}: {str(e)}")
            
            return Response({
                "message": "OTP process completed.",
                "otp_debug": otp if settings.DEBUG else "Sent to email",
                "notice": "If you don't receive the email, use the otp_debug code for testing."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            try:
                otp_obj = OTPCode.objects.filter(email=email, code=otp, is_verified=False).latest('created_at')
                otp_obj.is_verified = True
                otp_obj.save()
                print(f"OTP {otp} verified for {email}")
                return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
            except OTPCode.DoesNotExist:
                print(f"OTP Verification failed for {email} with code {otp}")
                return Response({"error": "Invalid or expired OTP code."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['new_password']
            otp = serializer.validated_data.get('otp')
            
            # Additional security: check if this OTP was actually verified
            if not OTPCode.objects.filter(email=email, code=otp, is_verified=True).exists():
                return Response({"error": "Unauthorized: OTP not verified for this email."}, status=status.HTTP_401_UNAUTHORIZED)

            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            user.set_password(password)
            user.save()
            
            # Cleanup: Delete used OTPs for this email
            OTPCode.objects.filter(email=email).delete()
            
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    @extend_schema(responses={200: MessageSerializer})

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)
