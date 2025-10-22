#!/bin/bash

BUCKET_NAME="crop-recommendation-terraform-state-mumbai-$(whoami)"

# Create S3 bucket
aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region ap-south-1 \
  --create-bucket-configuration LocationConstraint=ap-south-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# # Create DynamoDB table
# aws dynamodb create-table \
#   --table-name terraform-state-lock \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
#   --region ap-south-1

echo "Backend setup complete! Update backend.tf with bucket: $BUCKET_NAME"