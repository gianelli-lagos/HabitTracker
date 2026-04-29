import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def upload_profile_picture(file_content: bytes, user_id: int, filename: str) -> str:
    """
    Upload a profile picture to S3.
    
    Args:
        file_content: The file content as bytes
        user_id: The user ID
        filename: Original filename
    
    Returns:
        A presigned URL of the uploaded file (valid for 1 hour)
    
    Raises:
        Exception: If upload fails
    """
    try:
        # Create a unique key for the file
        file_extension = os.path.splitext(filename)[1]
        s3_key = f"profile-pictures/{user_id}{file_extension}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType="image/jpeg",  # Adjust based on file type if needed
        )
        
        # Generate presigned URL (valid for 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=3600,  # 1 hour
        )
        return presigned_url
    
    except ClientError as e:
        raise Exception(f"Failed to upload to S3: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error during S3 upload: {str(e)}")


def delete_profile_picture(user_id: int) -> bool:
    """
    Delete a profile picture from S3.
    
    Args:
        user_id: The user ID
    
    Returns:
        True if deletion was successful
    """
    try:
        # List all files for this user and delete them
        # (in case there are old versions with different extensions)
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=f"profile-pictures/{user_id}"
        )
        
        if "Contents" in response:
            for obj in response["Contents"]:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj["Key"])
        
        return True
    
    except ClientError as e:
        print(f"Failed to delete from S3: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error during S3 deletion: {str(e)}")
        return False


def get_profile_picture_url(user_id: int) -> str:
    """
    Generate a fresh presigned URL for a profile picture (valid for 1 hour).
    Call this whenever you need to display the image URL.
    
    Args:
        user_id: The user ID
    
    Returns:
        A presigned URL or None if file doesn't exist
    """
    try:
        # List objects to find the profile picture
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=f"profile-pictures/{user_id}"
        )
        
        if "Contents" not in response or len(response["Contents"]) == 0:
            return None
        
        # Get the first (and usually only) file
        s3_key = response["Contents"][0]["Key"]
        
        # Generate a fresh presigned URL (valid for 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=3600,  # 1 hour
        )
        
        return presigned_url
    
    except ClientError as e:
        print(f"Failed to generate presigned URL: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error generating presigned URL: {str(e)}")
        return None
