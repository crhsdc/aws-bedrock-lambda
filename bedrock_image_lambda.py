import json
import boto3
import base64
import uuid
import os
from datetime import datetime

def lambda_handler(event, context):
    # Initialize Bedrock and S3 clients
    bedrock = boto3.client('bedrock-runtime')
    s3 = boto3.client('s3')
    
    # Validate environment variable
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    if not bucket_name:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'S3_BUCKET_NAME environment variable is not set'})
        }
    
    # Get the prompt from the event
    prompt = event.get('prompt', 'A beautiful sunset over mountains')
    
    # Prepare the request body for Stable Diffusion
    request_body = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "steps": 50,
        "seed": 42,
        "width": 512,
        "height": 512
    }
    
    try:
        # Call Bedrock with Stable Diffusion model
        response = bedrock.invoke_model(
            modelId='stability.stable-diffusion-xl-v1',
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response.get('body').read())
        
        # The response includes base64-encoded image
        image_data = response_body['artifacts'][0]['base64']
        
        # Decode base64 string to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_id = str(uuid.uuid4())[:8]
        file_name = f"image_{timestamp}_{file_id}.png"
        
        # Upload the image to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=image_bytes,
            ContentType='image/png'
        )
        
        # Generate the S3 URL
        s3_url = f"s3://{bucket_name}/{file_name}"
        
        # Remove sensitive data from response
        return {
            'statusCode': 200,
            'body': json.dumps({
                's3_url': s3_url,
                'file_name': file_name
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }