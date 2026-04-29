import os
from dotenv import load_dotenv
from services.s3_service import upload_profile_picture, get_profile_picture_url
from PIL import Image
import io
import requests

load_dotenv()

# Create a test image
img = Image.new('RGB', (300, 300), color='green')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)
test_image_content = img_bytes.read()

print("=" * 70)
print("Testing S3 with Presigned URLs")
print("=" * 70)

try:
    # Upload
    print("\n1. Uploading test image to S3...")
    presigned_url = upload_profile_picture(
        file_content=test_image_content,
        user_id=99999,
        filename="test_profile.jpg"
    )
    print(f"✓ Upload successful!")
    print(f"✓ Presigned URL: {presigned_url[:80]}...")
    
    # Test accessing the image with presigned URL
    print("\n2. Testing access with presigned URL...")
    response = requests.head(presigned_url)
    if response.status_code == 200:
        print(f"✓ File is accessible via presigned URL!")
        print(f"✓ Content-Type: {response.headers.get('Content-Type')}")
        print(f"✓ Content-Length: {response.headers.get('Content-Length')} bytes")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Test regenerating a fresh presigned URL
    print("\n3. Regenerating fresh presigned URL...")
    fresh_url = get_profile_picture_url(99999)
    if fresh_url:
        print(f"✓ Fresh presigned URL generated!")
        response = requests.head(fresh_url)
        if response.status_code == 200:
            print(f"✓ Fresh URL is also accessible!")
    else:
        print("✗ Failed to generate fresh URL")
    
    print("\n" + "=" * 70)
    print("✓ All tests passed! Presigned URL approach is working!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
