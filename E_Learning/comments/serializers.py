from rest_framework import serializers
from .models import Comment, Reply


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = "__all__"
        read_only_fields = ["created", "author"]


class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["created", "author"]
