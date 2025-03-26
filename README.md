# AWS Bedrock Lambda Functions for Text and Image Generation

This project provides AWS Lambda functions that leverage Amazon Bedrock's AI capabilities to generate text using Claude 3 and images using Stable Diffusion. The functions offer a simple API interface for text generation and image creation with automatic S3 storage integration.

The repository contains two Lambda functions that demonstrate the integration of AWS Bedrock with serverless architecture. The text generation function utilizes Claude 3 Sonnet model to generate human-like text responses, while the image generation function employs Stable Diffusion XL to create images from text prompts and automatically stores them in S3. These functions are designed to be easily deployable and integrated into larger applications requiring AI-powered content generation capabilities.

## Repository Structure

```
.
├── bedrock_image_lambda.py  # Lambda function for generating images using Stable Diffusion
├── bedrock_text_lambda.py   # Lambda function for generating text using Claude 3
└── README.md               # Project documentation
```

## Usage Instructions

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Access to AWS Bedrock service
- Python 3.8 or later
- The following IAM permissions:
  - `bedrock:InvokeModel`
  - `s3:PutObject` (for image generation function)
- Environment variable `S3_BUCKET_NAME` (for image generation function)

### Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd [repository-name]
```

2. Create IAM Role for Lambda functions:

```bash
# Create a trust policy file
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role --role-name bedrock-lambda-role \
    --assume-role-policy-document file://trust-policy.json

# Create policy for Bedrock and S3 access
cat > permissions-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "s3:PutObject",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Attach the policy to the role
aws iam put-role-policy --role-name bedrock-lambda-role \
    --policy-name bedrock-lambda-policy \
    --policy-document file://permissions-policy.json
```

3. Creating an S3 Bucket using AWS CLI

```bash
aws s3api create-bucket --bucket bedrock-image-lambda-270325 --region us-east-1
```

3. Create Lambda functions in AWS Console:

```bash
# For text generation function
zip -r text-function.zip bedrock_text_lambda.py
aws lambda create-function --function-name bedrock-text-generator \
    --runtime python3.8 \
    --handler bedrock_text_lambda.lambda_handler \
    --zip-file fileb://text-function.zip \
    --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/bedrock-lambda-role \
    --timeout 30 \
    --memory-size 256


# Inline sample for Current AWS Environment
aws lambda create-function --function-name bedrock-text-generator --runtime python3.8 --handler bedrock_text_lambda.lambda_handler --zip-file fileb://text-function.zip --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/bedrock-lambda-role --timeout 30 --memory-size 256


# For image generation function
zip -r image-function.zip bedrock_image_lambda.py
aws lambda create-function --function-name bedrock-image-generator \
    --runtime python3.8 \
    --handler bedrock_image_lambda.lambda_handler \
    --zip-file fileb://image-function.zip \
    --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/bedrock-lambda-role \
    --timeout 60 \
    --memory-size 512 \
    --environment Variables={S3_BUCKET_NAME=[YOUR_BUCKET_NAME]}


# Inline sample for Current AWS Environment
aws lambda --profile genai create-function --function-name bedrock-image-generator --runtime python3.8 --handler bedrock_image_lambda.lambda_handler --zip-file fileb://bedrock_image_lambda.zip --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/bedrock-lambda-role --timeout 60 --memory-size 512

aws lambda update-function-configuration --function-name bedrock-image-generator --environment "Variables={S3_BUCKET_NAME=bedrock-image-lambda-270325}"

```

### Quick Start

1. Text Generation:

```python
# Example event for text generation
event = {
    "prompt": "Tell me a short story about space exploration"
}
```

2. Image Generation:

```python
# Example event for image generation
event = {
    "prompt": "A beautiful sunset over mountains"
}
```

### More Detailed Examples

1. Text Generation with Claude 3:

```python
# Detailed text generation example
response = lambda_client.invoke(
    FunctionName='bedrock-text-generator',
    Payload=json.dumps({
        "prompt": "Write a technical explanation of quantum computing"
    })
)
```

2. Image Generation with Stable Diffusion:

```python
# Detailed image generation example
response = lambda_client.invoke(
    FunctionName='bedrock-image-generator',
    Payload=json.dumps({
        "prompt": "A futuristic cityscape at night with flying cars"
    })
)
```

### Troubleshooting

Common Issues:

1. Bedrock Access Error

```
Error: AccessDeniedException: User is not authorized to perform bedrock:InvokeModel
Solution: Ensure proper IAM permissions are attached to the Lambda role
```

2. S3 Upload Failure

```
Error: NoSuchBucket: The specified bucket does not exist
Solution:
- Verify S3_BUCKET_NAME environment variable is set correctly
- Ensure bucket exists and Lambda has proper permissions
```

3. Memory Issues

```
Error: Task timed out after X seconds
Solution: Increase Lambda function timeout and memory allocation
```

## Data Flow

The functions process requests through AWS Lambda, interact with Bedrock for AI generation, and store results either directly in the response (text) or in S3 (images).

```ascii
Text Generation:
API Gateway → Lambda → Bedrock (Claude) → Response

Image Generation:
API Gateway → Lambda → Bedrock (Stable Diffusion) → S3 → Response
```

Key Component Interactions:

- Lambda functions authenticate with Bedrock using AWS SDK
- Text generation returns direct JSON responses
- Image generation stores files in S3 and returns URLs
- Both functions handle errors with appropriate HTTP status codes
- Bedrock models are invoked with specific parameters (temperature, tokens, image dimensions)
- S3 storage includes unique file names with timestamps
