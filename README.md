# AWS Bedrock and AWS Services Lambda Functions

This project provides AWS Lambda functions that leverage various AWS services including Amazon Bedrock's AI capabilities, Amazon Transcribe, Amazon Polly, Amazon Textract, Amazon Rekognition, and Amazon Translate.

The repository contains Lambda functions that demonstrate the integration of AWS services with serverless architecture:
- Text generation using Claude 3 Sonnet model
- Image generation using Stable Diffusion XL
- Speech-to-text conversion using Amazon Transcribe
- Text-to-speech conversion using Amazon Polly
- Document text extraction using Amazon Textract
- Image analysis using Amazon Rekognition
- Text translation using Amazon Translate

## Repository Structure

```
.
├── bedrock_image_lambda.py  # Lambda function for generating images using Stable Diffusion
├── bedrock_nova_lambda.py   # Lambda function for using AWS Bedrock with Nova model
├── bedrock_text_lambda.py   # Lambda function for generating text using Claude 3
├── transcribe_lambda.py     # Lambda function for converting speech to text using Amazon Transcribe
├── polly_lambda.py          # Lambda function for converting text to speech using Amazon Polly
├── textract_lambda.py       # Lambda function for extracting text from documents using Amazon Textract
├── rekognition_lambda.py    # Lambda function for analyzing images using Amazon Rekognition
├── translate_lambda.py      # Lambda function for translating text using Amazon Translate
└── README.md                # Project documentation
```

## AWS AI Services Lambda Functions

### Amazon Transcribe Lambda Function

The `transcribe_lambda.py` file demonstrates how to use Amazon Transcribe with AWS Lambda. This function:

1. Triggers when a new audio file is uploaded to an S3 bucket
2. Starts an Amazon Transcribe job to convert the speech to text
3. Stores the transcription results back in the S3 bucket

#### Required IAM Permissions for Transcribe Lambda

The Lambda function requires the following permissions:
- `transcribe:StartTranscriptionJob`
- `s3:GetObject` (for the source bucket)
- `s3:PutObject` (for the destination bucket)

#### Example test event for Transcribe Lambda

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "your-audio-bucket"
        },
        "object": {
          "key": "path/to/audio-file.mp3"
        }
      }
    }
  ]
}
```

### Amazon Polly Lambda Function

The `polly_lambda.py` file demonstrates how to use Amazon Polly with AWS Lambda. This function:

1. Takes text input from the event
2. Converts it to speech using Amazon Polly's Generative Engine
3. Saves the audio file to S3
4. Returns the S3 URL of the generated audio

#### Required IAM Permissions for Polly Lambda

The Lambda function requires the following permissions:
- `polly:SynthesizeSpeech`
- `s3:PutObject` (for storing the audio file)

#### Example test event for Polly Lambda

```json
{
  "text": "Hola, ¿cómo estás hoy?",
  "voiceId": "Mia",
  "languageCode": "es-MX",
  "outputFormat": "mp3",
  "bucket": "your-s3-bucket-name"
}
```

### Amazon Textract Lambda Function

The `textract_lambda.py` file demonstrates how to use Amazon Textract with AWS Lambda. This function:

1. Triggers when new documents are uploaded to an S3 bucket
2. Uses Amazon Textract to extract text from the documents
3. Returns the extracted text from all documents

#### Required IAM Permissions for Textract Lambda

The Lambda function requires the following permissions:
- `textract:DetectDocumentText`
- `textract:AnalyzeDocument`
- `s3:GetObject` (for accessing the document)

#### Example test event for Textract Lambda

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "your-document-bucket"
        },
        "object": {
          "key": "path/to/document.pdf"
        }
      }
    }
  ]
}
```

### Amazon Rekognition Lambda Function

The `rekognition_lambda.py` file demonstrates how to use Amazon Rekognition with AWS Lambda. This function:

1. Triggers when new images are uploaded to an S3 bucket
2. Uses Amazon Rekognition to detect labels in the images
3. Returns the detected labels with confidence scores from all images

#### Required IAM Permissions for Rekognition Lambda

The Lambda function requires the following permissions:
- `rekognition:DetectLabels`
- `s3:GetObject` (for accessing the image)

#### Example test event for Rekognition Lambda

```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "your-image-bucket"
        },
        "object": {
          "key": "path/to/image.jpg"
        }
      }
    }
  ]
}
```

### Amazon Translate Lambda Function

The `translate_lambda.py` file demonstrates how to use Amazon Translate with AWS Lambda. This function:

1. Takes text input from the event
2. Translates the text from source language to target language
3. Returns the translated text

#### Required IAM Permissions for Translate Lambda

The Lambda function requires the following permissions:
- `translate:TranslateText`

#### Example test event for Translate Lambda

```json
{
  "text": "Hello, how are you today?",
  "sourceLanguage": "en",
  "targetLanguage": "es"
}
```

## AWS Bedrock Lambda Functions

This project provides AWS Lambda functions that leverage Amazon Bedrock's AI capabilities to generate text using Claude 3 and images using Stable Diffusion. The functions offer a simple API interface for text generation and image creation with automatic S3 storage integration.

The text generation function utilizes Claude 3 Sonnet model to generate human-like text responses, while the image generation function employs Stable Diffusion XL to create images from text prompts and automatically stores them in S3. These functions are designed to be easily deployable and integrated into larger applications requiring AI-powered content generation capabilities.

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
aws iam create-role --role-name aws-services-lambda-role \
    --assume-role-policy-document file://trust-policy.json

# Create policy for AWS services access
cat > permissions-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "polly:SynthesizeSpeech",
                "transcribe:StartTranscriptionJob",
                "textract:DetectDocumentText",
                "textract:AnalyzeDocument",
                "rekognition:DetectLabels",
                "translate:TranslateText",
                "s3:GetObject",
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
aws iam put-role-policy --role-name aws-services-lambda-role \
    --policy-name aws-services-lambda-policy \
    --policy-document file://permissions-policy.json
```

3. Creating an S3 Bucket using AWS CLI

```bash
aws s3api create-bucket --bucket aws-services-lambda-bucket --region us-east-1
```

4. Create Lambda functions in AWS Console:

```bash
# For text generation function
zip -r text-function.zip bedrock_text_lambda.py
aws lambda create-function --function-name bedrock-text-generator \
    --runtime python3.8 \
    --handler bedrock_text_lambda.lambda_handler \
    --zip-file fileb://text-function.zip \
    --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/aws-services-lambda-role \
    --timeout 30 \
    --memory-size 256

# For image generation function
zip -r image-function.zip bedrock_image_lambda.py
aws lambda create-function --function-name bedrock-image-generator \
    --runtime python3.8 \
    --handler bedrock_image_lambda.lambda_handler \
    --zip-file fileb://image-function.zip \
    --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/aws-services-lambda-role \
    --timeout 60 \
    --memory-size 512 \
    --environment Variables={S3_BUCKET_NAME=[YOUR_BUCKET_NAME]}
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

## Troubleshooting

Common Issues:

1. Access Error

```
Error: AccessDeniedException: User is not authorized to perform [service]:[action]
Solution: Ensure proper IAM permissions are attached to the Lambda role
```

2. S3 Upload Failure

```
Error: NoSuchBucket: The specified bucket does not exist
Solution:
- Verify bucket name is provided correctly
- Ensure bucket exists and Lambda has proper permissions
```

3. Memory Issues

```
Error: Task timed out after X seconds
Solution: Increase Lambda function timeout and memory allocation
```

## Data Flow

The functions process requests through AWS Lambda, interact with AWS services, and store results either directly in the response or in S3.

```ascii
Text Generation:
API Gateway → Lambda → Bedrock (Claude) → Response

Image Generation:
API Gateway → Lambda → Bedrock (Stable Diffusion) → S3 → Response

Transcribe:
S3 Upload → Lambda → Transcribe → S3 → Response

Polly:
API Gateway → Lambda → Polly → S3 → Response

Textract:
S3 Upload → Lambda → Textract → Response

Rekognition:
S3 Upload → Lambda → Rekognition → Response

Translate:
API Gateway → Lambda → Translate → Response
```