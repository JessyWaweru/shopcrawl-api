from django.urls import path, include
from django.contrib import admin
from django.http import JsonResponse # <--- Import this

# 1. Simple Test Function (No Database)
def ping(request):
    return JsonResponse({"message": "Pong! Server is fast."})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('ping/', ping),  # <--- Add this line
]