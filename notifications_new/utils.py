import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import json
import os

def initialize_firebase():
    """
    Initialize Firebase Admin SDK if not already initialized
    """
    if not firebase_admin._apps:
        if hasattr(settings, 'FIREBASE_SERVICE_ACCOUNT') and settings.FIREBASE_SERVICE_ACCOUNT:
            firebase_cred = credentials.Certificate(json.loads(settings.FIREBASE_SERVICE_ACCOUNT))
        else:
            firebase_cred = credentials.Certificate(os.path.join(settings.BASE_DIR, 'firebase-service-account.json'))
        firebase_admin.initialize_app(firebase_cred)

def send_push_notification(token, title, body, data=None):
    """
    Send a push notification to a specific device token
    """
    try:
        initialize_firebase()
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    priority='high'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        content_available=True,
                        priority=10
                    )
                )
            )
        )
        
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Error sending push notification: {e}")
        return None 