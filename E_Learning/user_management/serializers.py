from rest_framework import serializers


class resetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    resetKey = serializers.CharField()
