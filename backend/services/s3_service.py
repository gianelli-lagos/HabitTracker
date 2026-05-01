import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

logger.info(f"S3 Configuration - Bucket: {S3_BUCKET_NAME}, Region: {S3_REGION}")
if not S3_BUCKET_NAME:
    logger.error("S3_BUCKET_NAME environment variable is not set!")
if not AWS_ACCESS_KEY_ID:
    logger.error("AWS_ACCESS_KEY_ID environment variable is not set!")
if not AWS_SECRET_ACCESS_KEY:
    logger.error("AWS_SECRET_ACCESS_KEY environment variable is not set!")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
logger.info("S3 client initialized successfully")


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
        
        logger.info(f"Uploading file to S3: s3://{S3_BUCKET_NAME}/{s3_key}")
        logger.info(f"File size: {len(file_content)} bytes")
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType="image/jpeg",  # Adjust based on file type if needed
        )
        logger.info(f"File uploaded successfully to S3: {s3_key}")
        
        # Generate presigned URL (valid for 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=3600,  # 1 hour
        )
        logger.info(f"Presigned URL generated: {presigned_url[:80]}...")
        return presigned_url
    
    except ClientError as e:
        logger.error(f"ClientError during S3 upload: {str(e)}")
        raise Exception(f"Failed to upload to S3: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during S3 upload: {str(e)}", exc_info=True)
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
            logger.info(f"Found {len(response['Contents'])} files to delete for user {user_id}")
            for obj in response["Contents"]:
                logger.info(f"Deleting: {obj['Key']}")
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj["Key"])
        else:
            logger.info(f"No existing files to delete for user {user_id}")
        
        return True
    
    except ClientError as e:
        logger.error(f"Failed to delete from S3: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during S3 deletion: {str(e)}")
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
            logger.info(f"No profile picture found for user {user_id}")
            return None
        
        # Get the first (and usually only) file
        s3_key = response["Contents"][0]["Key"]
        logger.info(f"Generating presigned URL for: {s3_key}")
        
        # Generate a fresh presigned URL (valid for 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=3600,  # 1 hour
        )
        
        logger.info(f"Presigned URL generated for user {user_id}")
        return presigned_url
    
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL: {str(e)}")
        return None
