import os
from dotenv import load_dotenv
from services.s3_service import upload_profile_picture
from PIL import Image
import io

load_dotenv()

# Create a test image
img = Image.new('RGB', (200, 200), color='blue')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)
test_image_content = img_bytes.read()

print("Uploading test image to S3...")
try:
    url = upload_profile_picture(
        file_content=test_image_content,
        user_id=12345,  # Test user ID
        filename="test_profile.jpg"
    )
    print(f"✓ Success! File uploaded to: {url}")
    print("\nCheck your AWS S3 bucket now - you should see profile-pictures/12345.jpg")
except Exception as e:
    print(f"✗ Error: {str(e)}")
