import boto3
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings

def create_bucket():
    print(f"Attempting to create bucket: {settings.AWS_S3_BUCKET}")
    print(f"Region: {settings.AWS_REGION_NAME}")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=settings.AWS_S3_BUCKET)
            print(f"Bucket {settings.AWS_S3_BUCKET} already exists.")
            return
        except Exception:
            # Bucket likely doesn't exist
            pass
            
        if settings.AWS_REGION_NAME == 'us-east-1':
            s3_client.create_bucket(Bucket=settings.AWS_S3_BUCKET)
        else:
            s3_client.create_bucket(
                Bucket=settings.AWS_S3_BUCKET,
                CreateBucketConfiguration={
                    'LocationConstraint': settings.AWS_REGION_NAME
                }
            )
        print(f"Successfully created bucket {settings.AWS_S3_BUCKET}")
        
    except Exception as e:
        print(f"Error creating bucket: {e}")

if __name__ == "__main__":
    create_bucket()
