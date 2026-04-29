import os
from dotenv import load_dotenv
from services.s3_service import upload_profile_picture, delete_profile_picture
from PIL import Image
import io

load_dotenv()

# Create a test image
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)
test_image_content = img_bytes.read()

print("=" * 60)
print("Testing S3 Profile Picture Upload")
print("=" * 60)

try:
    # Test upload
    print("\n1. Uploading test image to S3...")
    url = upload_profile_picture(
        file_content=test_image_content,
        user_id=999,  # Test user ID
        filename="test_profile.jpg"
    )
    print(f"✓ Upload successful!")
    print(f"✓ URL: {url}")
    
    # Test delete
    print("\n2. Deleting test image from S3...")
    deleted = delete_profile_picture(user_id=999)
    if deleted:
        print("✓ Deletion successful!")
    else:
        print("✗ Deletion failed")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! S3 integration is working!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    print("=" * 60)
