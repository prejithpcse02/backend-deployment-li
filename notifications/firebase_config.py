import os
import json
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with proper error handling
    """
    try:
        if not firebase_admin._apps:
            # Try to get credentials from environment variable
            if settings.FIREBASE_SERVICE_ACCOUNT:
                service_account_info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT)
                cred = credentials.Certificate(service_account_info)
            else:
                # Try to load from file
                cred_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    raise ValueError("Firebase credentials not found. Please set FIREBASE_SERVICE_ACCOUNT environment variable or add firebase-service-account.json file.")

            firebase_admin.initialize_app(cred)
            return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

def get_firebase_app():
    """
    Get the Firebase app instance
    """
    try:
        return firebase_admin.get_app()
    except ValueError:
        if initialize_firebase():
            return firebase_admin.get_app()
        return None 