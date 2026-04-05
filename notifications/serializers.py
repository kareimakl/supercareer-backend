from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)
    confirm_new_password = serializers.CharField(min_length=8, required=False)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')
        
        if confirm_new_password and new_password != confirm_new_password:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        return data

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
