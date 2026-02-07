import boto3
import json
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.config import settings

def make_bucket_public():
    bucket_name = settings.AWS_S3_BUCKET
    print(f"Configuring public access for bucket: {bucket_name}")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )
        
        # 1. Disable Block Public Access
        print("Disabling Block Public Access...")
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        print("Block Public Access disabled.")

        # 2. Add Bucket Policy for Public Read
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        # Convert the policy to a JSON string
        bucket_policy = json.dumps(bucket_policy)
        
        print("Setting Bucket Policy...")
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
        print("Bucket Policy set to Public Read.")
        
    except Exception as e:
        print(f"Error configuring bucket: {e}")

if __name__ == "__main__":
    make_bucket_public()
