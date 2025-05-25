import json
import boto3
import os
import uuid
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """
    Lambda function that demonstrates using Amazon Transcribe to convert speech to text.
    
    This function:
    1. Gets an S3 object (audio file) from the event
    2. Starts a transcription job
    3. Returns the job details
    
    The Lambda function requires these permissions:
    transcribe:StartTranscriptionJob
    s3:GetObject (for accessing the audio file)
    s3:PutObject (for storing the transcription results)
    
    Example test event:
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
    
    Note: This is an asynchronous process. In a real-world scenario, you would need to 
    check the job status later or set up a notification when the job completes.
    """
    # Initialize the Transcribe client
    transcribe = boto3.client('transcribe')
    
    # Get the S3 bucket and key from the event
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        # Generate a unique job name
        job_name = f"transcription-{uuid.uuid4()}"
        
        # Get the file extension to determine media format
        file_extension = os.path.splitext(key)[1].lower()
        media_format = file_extension[1:]  # Remove the dot
        
        # Map common extensions to formats Transcribe understands
        format_mapping = {
            'mp3': 'mp3',
            'mp4': 'mp4',
            'wav': 'wav',
            'flac': 'flac',
            'm4a': 'mp4',
            'ogg': 'ogg'
        }
        
        media_format = format_mapping.get(media_format, 'mp3')  # Default to mp3 if unknown
        
        # Define the S3 URI for the audio file
        s3_uri = f"s3://{bucket}/{key}"
        
        try:
            # Start the transcription job
            response = transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': s3_uri},
                MediaFormat=media_format,
                LanguageCode='en-US',  # Specify the language of the audio
                OutputBucketName=bucket,  # Where to store the results
                OutputKey=f"transcriptions/{os.path.basename(key)}.json"
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Transcription job started successfully',
                    'jobName': job_name,
                    'jobStatus': response['TranscriptionJob']['TranscriptionJobStatus']
                })
            }
            
        except Exception as e:
            print(f"Error starting transcription job: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Error starting transcription job',
                    'error': str(e)
                })
            }



