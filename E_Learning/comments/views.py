# All APIs described here take course_id as a required param to determine whether the user has brought
# the course or not. Only when he/she has brought the course, then they can use these APIs

from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CommentSerializer, ReplySerializer
from .models import Comment, Reply, Course
from .permissions import IsOwnerOrReadOnly

# Get method for this cbv will return all the comments along with requests for that course
class CommentList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        comments = Comment.objects.filter(course=courseInst)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, course_id, format=None):
        # Check if course exists
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Create the comment
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=self.request.user, course=courseInst)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # Only the author can change or delete comments
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, pk, courseInst):
        try:
            return Comment.objects.get(pk=pk, course=courseInst)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, course_id, pk, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        comment = self.get_object(pk, courseInst)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk, course_id, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        comment = self.get_object(pk, courseInst)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, course_id, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        comment = self.get_object(pk, courseInst)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReplyList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_comment(self, comment_id):
        try:
            return Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise Http404

    def post(self, request, course_id, comment_id, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReplySerializer(data=request.data)
        comment = self.get_comment(comment_id)
        if serializer.is_valid():
            serializer.save(author=self.request.user, comment=comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReplyDetail(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            return Reply.objects.get(pk=pk)
        except Reply.DoesNotExist:
            raise Http404

    def get(self, request, course_id, comment_id, pk, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        reply = self.get_object(pk)
        serializer = ReplySerializer(reply)
        return Response(serializer.data)

    def put(self, request, course_id, comment_id, pk, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        reply = self.get_object(pk)
        serializer = ReplySerializer(reply, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id, comment_id, pk, format=None):
        courseInst = Course.objects.filter(pk=course_id).first()
        if courseInst is None:
            data = {"error": "Course does not exist", "result": False, "message": ""}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        reply = self.get_object(pk)
        reply.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
