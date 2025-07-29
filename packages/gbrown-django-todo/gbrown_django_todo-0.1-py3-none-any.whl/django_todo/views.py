from django.shortcuts import render
from rest_framework import generics
from django_todo.models import Todo
from django_todo.serializers import TodoSerializer

class TodoList(generics.ListCreateAPIView):
    """
    Provides GET and POST endpoints for viewing all TODOS and creating new TODOs
    """
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
