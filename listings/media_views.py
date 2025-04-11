from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.views.static import serve
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os
import boto3
from botocore.exceptions import ClientError

class MediaServeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Disable authentication completely
    
    def get(self, request, path):
        # If using S3, redirect to the S3 URL
        if settings.USE_S3:
            try:
                # Construct the S3 URL
                s3_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/{path}"
                return HttpResponseRedirect(s3_url)
            except Exception as e:
                print(f"Error redirecting to S3: {str(e)}")
                return Response({'error': str(e)}, status=500)
        
        # Otherwise, serve from local storage
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, path)
            
            # Check if the requested file exists
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'))
                response['Access-Control-Allow-Origin'] = '*'
                return response
            
            # If file doesn't exist, try to serve the default image
            default_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')
            if os.path.exists(default_path):
                response = FileResponse(open(default_path, 'rb'))
                response['Access-Control-Allow-Origin'] = '*'
                return response
                
            # If default image doesn't exist either, return a 404
            return Response({'error': 'File not found'}, status=404)
            
        except Exception as e:
            print(f"Error serving media file: {str(e)}")
            return Response({'error': str(e)}, status=500) 