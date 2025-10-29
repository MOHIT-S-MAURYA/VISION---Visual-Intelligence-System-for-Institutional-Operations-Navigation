#!/usr/bin/env python3
import os
import io
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

import django
django.setup()

from PIL import Image
from rest_framework.test import APIRequestFactory
from students.views import StudentViewSet


def make_dummy_image_bytes(width=160, height=160, color=(200, 200, 200)):
    img = Image.new('RGB', (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    buf.seek(0)
    return buf


def main():
    factory = APIRequestFactory()
    img_bytes = make_dummy_image_bytes()
    img_bytes.name = 'dummy.jpg'  # DRF uses this for filename

    payload = {
        'roll_number': 'TEST-R123',
        'full_name': 'Test User',
        'department': 'CSE',
        'class_year': '2025',
        'face_image': img_bytes,
    }

    request = factory.post('/api/students/register_with_face/', payload, format='multipart')
    view = StudentViewSet.as_view({'post': 'register_with_face'})
    response = view(request)
    print('Status:', response.status_code)
    try:
        print('Body:', response.data)
    except Exception as e:
        print('No JSON body. Raw:', getattr(response, 'content', b'')[:200])


if __name__ == '__main__':
    main()
