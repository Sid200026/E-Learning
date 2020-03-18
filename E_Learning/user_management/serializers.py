from rest_framework import serializers

class userSerializer(serializers.Serializer):
    username = serializers.CharField()