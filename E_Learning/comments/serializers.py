from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment, Reply, Course

User = get_user_model()


class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        read_only_fields = ["first_name", "last_name"]


class CourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["name", "id"]
        read_only_fields = ["name", "id"]


class ReplySerializer(serializers.ModelSerializer):
    author = NameSerializer(required=False)

    class Meta:
        model = Reply
        fields = "__all__"
        read_only_fields = ["created", "author", "comment"]


class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)
    # Here we specify required = False to prevent DRF asking these values on PUT or DELETE
    author = NameSerializer(required=False)
    course = CourseNameSerializer(required=False)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["created", "course", "author"]
