from django.conf import settings
from django.http import FileResponse
from django.views.static import serve
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import os

class MediaServeView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, path):
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'))
        return FileResponse(open(os.path.join(settings.MEDIA_ROOT, 'default.jpg'), 'rb')) 