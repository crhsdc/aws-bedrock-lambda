import json
import boto3
import os
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """
    Lambda function that demonstrates using Amazon Textract to extract text from documents.
    
    This function:
    1. Gets an S3 object (document/image) from the event
    2. Uses Amazon Textract to extract text from the document
    3. Returns the extracted text from all records
    
    The Lambda function requires these permissions:
    textract:DetectDocumentText
    textract:AnalyzeDocument
    s3:GetObject
    
    Example test event:
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
    """
    # Initialize the Textract client
    textract = boto3.client('textract')
    
    # Process all records and store results
    results = []
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        try:
            # Call Amazon Textract to detect text
            response = textract.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            # Extract text from the response
            extracted_text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    extracted_text += item['Text'] + '\n'
            
            # Add this document's results to our collection
            results.append({
                'documentLocation': f"s3://{bucket}/{key}",
                'extractedText': extracted_text
            })
            
        except Exception as e:
            print(f"Error extracting text from {bucket}/{key}: {str(e)}")
            results.append({
                'documentLocation': f"s3://{bucket}/{key}",
                'error': str(e)
            })
    
    # Return all results
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processed {len(results)} document(s)',
            'results': results
        })
    }