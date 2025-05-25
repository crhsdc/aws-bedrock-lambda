import json
import boto3
import qrcode
import io
import uuid
from datetime import datetime

def lambda_handler(event, context):
    """
    Lambda function that generates a QR code from a URL, uploads it to S3,
    and stores the URL and image location in DynamoDB.
    
    This function:
    1. Takes a URL input from the event
    2. Generates a QR code image
    3. Uploads the image to S3
    4. Stores the URL and image location in DynamoDB
    5. Returns the S3 URL of the generated image
    
    The Lambda function requires these permissions:
    s3:PutObject (for storing the QR code image)
    dynamodb:PutItem (for storing URL data)
    
    Example test event:
    {
      "url": "https://aws.amazon.com",
      "bucket": "your-s3-bucket-name",
      "tableName": "qrcode-urls",
      "filename": "my-qrcode.png"  # Optional
    }
    """
    # Get parameters from the event
    url = event.get('url')
    bucket = event.get('bucket')
    table_name = event.get('tableName')
    filename = event.get('filename')
    
    # Validate required parameters
    if not url:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'URL is required'
            })
        }
    
    if not bucket:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'S3 bucket name is required'
            })
        }
    
    if not table_name:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'DynamoDB table name is required'
            })
        }
    
    # Generate a filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"qrcode-{timestamp}.png"
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create an image from the QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Upload to S3
        s3_client = boto3.client('s3')
        s3_key = f"qrcodes/{filename}"
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=buffer,
            ContentType='image/png'
        )
        
        # Generate a pre-signed URL (valid for 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': s3_key},
            ExpiresIn=3600
        )
        
        # Store URL data in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        item_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        table.put_item(
            Item={
                'id': item_id,
                'url': url,
                's3Uri': f"s3://{bucket}/{s3_key}",
                'createdAt': timestamp
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'QR code generated successfully',
                'id': item_id,
                's3Uri': f"s3://{bucket}/{s3_key}",
                'presignedUrl': presigned_url,
                'url': url,
                'createdAt': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error generating QR code',
                'error': str(e)
            })
        }