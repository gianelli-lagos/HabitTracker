import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    's3',
    region_name=os.getenv('S3_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

# Test connection by listing buckets
try:
    response = s3_client.list_buckets()
    buckets = [b['Name'] for b in response['Buckets']]
    print('✓ Successfully connected to AWS S3!')
    print(f'✓ Found {len(buckets)} bucket(s)')
    if 'habittracker-profiles' in buckets:
        print('✓ Your habittracker-profiles bucket is accessible!')
    else:
        print('✗ habittracker-profiles bucket not found')
except Exception as e:
    print(f'✗ Error: {str(e)}')
