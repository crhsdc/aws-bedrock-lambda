import json
import boto3
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """
    Lambda function that demonstrates using Amazon Rekognition to detect objects and labels in images.
    
    This function:
    1. Gets an S3 object (image) from the event
    2. Uses Amazon Rekognition to detect labels in the image
    3. Returns the detected labels with confidence scores from all images
    
    The Lambda function requires these permissions:
    rekognition:DetectLabels
    s3:GetObject
    
    Example test event:
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
    """
    # Initialize the Rekognition client
    rekognition = boto3.client('rekognition')
    
    # Process all records and store results
    results = []
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        try:
            # Call Amazon Rekognition to detect labels
            response = rekognition.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                },
                MaxLabels=10,
                MinConfidence=70
            )
            
            # Extract labels from the response
            labels = [{'name': label['Name'], 'confidence': label['Confidence']} 
                     for label in response['Labels']]
            
            # Add this image's results to our collection
            results.append({
                'imageLocation': f"s3://{bucket}/{key}",
                'labels': labels
            })
            
        except Exception as e:
            print(f"Error analyzing image {bucket}/{key}: {str(e)}")
            results.append({
                'imageLocation': f"s3://{bucket}/{key}",
                'error': str(e)
            })
    
    # Return all results
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processed {len(results)} image(s)',
            'results': results
        })
    }