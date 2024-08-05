from django.shortcuts import render
from .models import Chat_History
from django.http import HttpResponse
from rest_framework.decorators import api_view
# Create your views here.
@api_view(["POST"])
def new_chat(request):
    if request.method == "POST":
        prompt = request.data.dict()
        print(prompt)
        chat = Chat_History(user_id=1, chat_id=1, messages=prompt["prompt"])
        chat.save()
        return HttpResponse("all good")

@api_view(["GET"])
def get_chat(request):
    if request.method == "GET":
        data = Chat_History.objects.all().order_by('message_index')[:3]
        print(data)
        return HttpResponse("Returned")