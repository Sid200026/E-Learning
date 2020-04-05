from rest_framework import serializers


class emailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class resetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    resetKey = serializers.CharField()
